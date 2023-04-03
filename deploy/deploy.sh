#!/bin/bash

# according to https://ydb.tech/en/docs/deploy/manual/deploy-ydb-on-premises


DISKS=$(cat nodes-disks.txt)
CONFIG_PATH=https://raw.githubusercontent.com/Sodex/ydb/main/ydb/deploy/yaml_config_examples/config.yaml

sudo groupadd ydb
sudo useradd ydb -g ydb
sudo usermod -aG disk ydb

mkdir ydbd-stable-linux-amd64
curl -L https://binaries.ydb.tech/ydbd-stable-linux-amd64.tar.gz | tar -xz --strip-component=1 -C ydbd-stable-linux-amd64

sudo mkdir -p /opt/ydb /opt/ydb/cfg
sudo cp -iR ydbd-stable-linux-amd64/bin /opt/ydb/
sudo cp -iR ydbd-stable-linux-amd64/lib /opt/ydb/

sudo chown -R root:bin /opt/ydb

IDX=1
for disk in $DISKS
do
  sudo parted ${disk} mklabel gpt -s
  sudo parted -a optimal ${disk} mkpart primary 0% 100%
  sudo parted ${disk} name 1 ydb_disk_ssd_0${IDX}
  sudo partx --u ${disk}
  sudo LD_LIBRARY_PATH=/opt/ydb/lib /opt/ydb/bin/ydbd admin bs disk obliterate /dev/disk/by-partlabel/ydb_disk_ssd_0${IDX}
  IDX=$(expr $IDX + 1)
done

sudo wget -nc -P /opt/ydb/cfg https://raw.githubusercontent.com/Sodex/ydb_test/main/deploy/config.yaml

#(1)#sudo su - ydb
#(2)#cd /opt/ydb

#(3)#LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ydb/lib /opt/ydb/bin/ydbd server --log-level 3 --syslog --tcp --yaml-config /opt/ydb/cfg/config.yaml --grpc-port 2135 --ic-port 19001 --mon-port 8765 --node static &

#(4)#LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ydb/lib /opt/ydb/bin/ydbd admin blobstorage config init --yaml-file /opt/ydb/cfg/config.yaml

#(5)#LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ydb/lib /opt/ydb/bin/ydbd admin database /Root/testdb create ssd:1

#(6)#LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ydb/lib /opt/ydb/bin/ydbd server --grpc-port 2136 --ic-port 19002 --mon-port 8766 --yaml-config /opt/ydb/cfg/config.yaml --tenant /Root/testdb --node-broker grpc://<first_node_FQDN>:2135 --node-broker grpc://<second_node_FQDN>:2135 --node-broker grpc://<third_node_FQDN>:2135 &

# важна последовательность:
# 1. исполнить команды (1,2) на каждом узле
# 2. исполнить команду (3) на каждом узле
# 3. исполнить команду (4 и 5) на одному из узлов
# 4. исполнить команду (6) на всех узлах 

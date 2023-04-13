# Sanity check output:
```bash
vks@ydb-node-zone-a:~/sanity_checks$ python3 -m pip install pandas
vks@ydb-node-zone-a:~/sanity_checks$ python3 -m pip install ydb
vks@ydb-node-zone-a:~/sanity_checks$ python3 main.py -e <node_ip>:2136 -d /Root/testdb
```
```sql
SELECT brand.name AS Brand, cars_ads.price as Price, cars_ads.color as Color \
FROM brand INNER JOIN cars_ads ON cars_ads.id == brand.id \
WHERE cars_ads.color == 'Белый'

{'Brand': 'Lexus', 'Price': 445000, 'Color': 'Белый'}
{'Brand': 'Kia', 'Price': 700000, 'Color': 'Белый'}
{'Brand': 'Hummer', 'Price': 360000, 'Color': 'Белый'}
{'Brand': 'Geely', 'Price': 550000, 'Color': 'Белый'}
{'Brand': 'Chery', 'Price': 2150000, 'Color': 'Белый'}
```

```sql
SELECT brand.name AS Brand, min(price) AS MinPrice, max(price) AS MaxPrice \
FROM cars_ads INNER JOIN  brand ON brand.id == cars_ads.brand_id \
GROUP BY brand.name
{'Brand': 'Volkswagen', 'MinPrice': 415000, 'MaxPrice': 1480000}
{'Brand': 'Cadillac', 'MinPrice': 1305000, 'MaxPrice': 1305000}
{'Brand': 'Audi', 'MinPrice': 188000, 'MaxPrice': 478000}
{'Brand': 'Toyota', 'MinPrice': 470000, 'MaxPrice': 2150000}
{'Brand': 'ВАЗ (LADA)', 'MinPrice': 189000, 'MaxPrice': 395000}
{'Brand': 'BMW', 'MinPrice': 610000, 'MaxPrice': 715000}
{'Brand': 'Skoda', 'MinPrice': 595000, 'MaxPrice': 595000}
{'Brand': 'Hyundai', 'MinPrice': 520000, 'MaxPrice': 700000}
{'Brand': 'Mazda', 'MinPrice': 465000, 'MaxPrice': 465000}
{'Brand': 'Ford', 'MinPrice': 215000, 'MaxPrice': 215000}
{'Brand': 'Kia', 'MinPrice': 445000, 'MaxPrice': 790000}
{'Brand': 'Nissan', 'MinPrice': 870000, 'MaxPrice': 880000}
{'Brand': 'Dodge', 'MinPrice': 360000, 'MaxPrice': 360000}
{'Brand': 'Renault', 'MinPrice': 249000, 'MaxPrice': 249000}
{'Brand': 'Honda', 'MinPrice': 990000, 'MaxPrice': 990000}
{'Brand': 'Suzuki', 'MinPrice': 660000, 'MaxPrice': 660000}
```
```sql
SELECT price FROM cars_ads WHERE id == 0
{'price': 475000}

UPDATE cars_ads SET price = price - 10000000 WHERE id == 0
SELECT price FROM cars_ads WHERE id == 0
{'price': 18446744073700026616}
```

```sql
ALTER TABLE cars_ads ADD COLUMN true_mileage Uint64
UPDATE cars_ads SET true_mileage = mileage + 100000
SELECT true_mileage, mileage FROM cars_ads WHERE id < 5

{'true_mileage': 225000, 'mileage': 125000}
{'true_mileage': 224600, 'mileage': 124600}
{'true_mileage': 330000, 'mileage': 230000}
{'true_mileage': 216000, 'mileage': 116000}
{'true_mileage': 389940, 'mileage': 289940}

ALTER TABLE cars_ads DROP COLUMN true_mileage
```

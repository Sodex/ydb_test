import ydb
import argparse
import pandas as pd

def add_new_column(session: ydb.Session):
    print("\n> ALTER TABLE cars_ads ADD COLUMN true_mileage Uint64")
    session.execute_scheme("ALTER TABLE cars_ads ADD COLUMN true_mileage Uint64")

    print("> UPDATE cars_ads SET true_mileage = mileage + 100000")
    session.transaction().execute("UPDATE cars_ads SET true_mileage = mileage + 100000", commit_tx=True)

    print("\n> SELECT true_mileage, mileage FROM cars_ads WHERE id < 5")
    result_sets = session.transaction().execute("SELECT true_mileage, mileage FROM cars_ads WHERE id < 5")
    for row in result_sets[0].rows:
        print(row)

    print("\n> ALTER TABLE cars_ads DROP COLUMN true_mileage")
    session.execute_scheme("ALTER TABLE cars_ads DROP COLUMN true_mileage")

def update_current_record(session: ydb.Session):
    print("\n> SELECT price FROM cars_ads WHERE id == 0")
    result_sets = session.transaction().execute("SELECT price FROM cars_ads WHERE id == 0")
    for row in result_sets[0].rows:
        print(row)
    
    print("\n> UPDATE cars_ads SET price = price - 10000000 WHERE id == 0")
    session.transaction().execute("UPDATE cars_ads SET price = price - 10000000 WHERE id == 0", commit_tx=True)

    print("> SELECT price FROM cars_ads WHERE id == 0")
    result_sets = session.transaction().execute("SELECT price FROM cars_ads WHERE id == 0")
    for row in result_sets[0].rows:
        print(row)


def select_simple(session: ydb.Session):
    print("\n> SELECT brand.name AS Brand, cars_ads.price as Price, cars_ads.color as Color FROM brand INNER JOIN cars_ads ON cars_ads.id == brand.id WHERE cars_ads.color == 'Белый'")
    result_sets = session.transaction().execute("SELECT brand.name AS Brand, cars_ads.price as Price, cars_ads.color as Color FROM brand INNER JOIN cars_ads ON cars_ads.id == brand.id WHERE cars_ads.color == 'Белый'")
    for row in result_sets[0].rows:
        print(row)        

    print("\n> SELECT brand.name AS Brand, min(price) AS MinPrice, max(price) AS MaxPrice FROM cars_ads INNER JOIN  brand ON brand.id == cars_ads.brand_id GROUP BY brand.name")
    result_sets = session.transaction().execute("SELECT brand.name AS Brand, min(price) AS MinPrice, max(price) AS MaxPrice FROM cars_ads INNER JOIN  brand ON brand.id == cars_ads.brand_id GROUP BY brand.name")
    for row in result_sets[0].rows:
        print(row)

     
def fill_tables_with_data(session: ydb.Session):
    df_brand = pd.read_csv('brand_table.csv')
    df_cars_ads = pd.read_csv('cars_ads_table.csv')

    for row in df_brand.iterrows():
        session.transaction().execute(f"""
            UPSERT INTO brand (id, name)
            VALUES ({row[-1][0]}, "{row[-1][1]}");
        """,
        commit_tx=True)
    
    for row in df_cars_ads.iterrows():
        session.transaction().execute(f"""
            UPSERT INTO cars_ads (id, city, price, body_type, brand_id, power, color, condition, drive, engine_type, mileage, transmission, wheel, year)
            VALUES ({row[-1][0]}, "{row[-1][1]}", {row[-1][2]}, "{row[-1][3]}", {row[-1][4]}, {int(row[-1][5])}, "{row[-1][6]}", "{row[-1][7]}", "{row[-1][8]}", "{row[-1][9]}", {int(row[-1][10])}, "{row[-1][11]}", "{row[-1][12]}", {int(row[-1][13])});
        """,
        commit_tx=True)

        
def create_tables(session: ydb.Session):
    session.execute_scheme("""
        CREATE TABLE brand (
            id Uint64,
            name Utf8,
            PRIMARY KEY (id)
        )    
        """)

    session.execute_scheme("""
        CREATE TABLE cars_ads (
            id Uint64,
            city Utf8,
            price Uint64,
            body_type Utf8,
            brand_id Uint64,
            power Uint16,
            color Utf8,
            condition Utf8,
            drive Utf8,
            engine_type Utf8,
            mileage Uint64,
            transmission Utf8,
            wheel Utf8,
            year Uint64,
            PRIMARY KEY (id)
        )
        """)


def run_sanity_checks(endpoint, database):
    try:
        driver = ydb.Driver(endpoint=endpoint, database=database)
        driver.wait(timeout=5, fail_fast=True)
    except TimeoutError:
        raise RuntimeError("Connect failed to YDB")

    session = driver.table_client.session().create()
    
    create_tables(session) 
    fill_tables_with_data(session)
    select_simple(session)
    update_current_record(session)
    add_new_column(session)

    driver.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-e", "--endpoint", required=True, help="Endpoint URL to use")
    parser.add_argument("-d", "--database", required=True, help="Name of the database to use")

    args = parser.parse_args()

    run_sanity_checks(args.endpoint, args.database)

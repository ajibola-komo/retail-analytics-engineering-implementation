import duckdb as db
from src.config.paths import (PRODUCT_RAW_PATH, PRODUCTS_DDL_PATH, PRODUCTS_CSV_PATH, PRODUCTS_PARQUET_PATH)

def generate_products(conn):
        create_db = PRODUCTS_DDL_PATH.read_text()
        conn.execute(create_db)

        conn.execute("DELETE FROM DIM_PRODUCT")

        conn.execute(f'''

WITH priced_products AS (

    SELECT
        product_id,
        product_name,
        category_id,
        subcategory_id,
        brand_id,
        unit_cost,

        ROUND(
            CASE

                -- Televisions
                WHEN category_id = 1 THEN
                    unit_cost * (1.12 + RANDOM() * 0.10)

                -- Computing / Audio / Storage
                WHEN category_id IN (2,7,9) THEN
                    unit_cost * (1.15 + RANDOM() * 0.15)

                -- Home Cinema / Cameras / Security
                WHEN category_id IN (3,4,5) THEN
                    unit_cost * (1.25 + RANDOM() * 0.20)

                -- Mobiles & Gaming
                WHEN category_id IN (6,8) THEN
                    unit_cost * (1.08 + RANDOM() * 0.12)

                -- Kitchen Appliances
                ELSE
                    unit_cost * (1.30 + RANDOM() * 0.25)

            END,
        2) AS unit_price,

        warranty_years

    FROM READ_CSV_AUTO('{PRODUCT_RAW_PATH}')
)

INSERT INTO DIM_PRODUCT

SELECT
    *,
    
    CASE
        WHEN unit_price < 150 THEN 'Low'
        WHEN unit_price < 300 THEN 'Entry Level'
        WHEN unit_price < 800 THEN 'Mid Tier'
        WHEN unit_price < 2000 THEN 'High End'
        ELSE 'Flagship'
    END AS product_segment

FROM priced_products

''')

        conn.execute(f'''
                    COPY DIM_PRODUCT TO '{PRODUCTS_PARQUET_PATH}' (FORMAT PARQUET)
''')
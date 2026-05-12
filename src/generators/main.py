from src.generators.date import generate_dates
from src.generators.brands import generate_brands
from src.generators.categories import generate_categories
from src.generators.campaigns import generate_campaigns
from src.generators.subcategories import generate_subcategories
from src.generators.fact_clickstream import generate_clickstreams
from src.generators.stores import generate_stores
from src.generators.location import generate_locations
from src.generators.products import generate_products
from src.generators.customers import generate_customers
from src.generators.promotions import generate_promotions
from src.generators.fact_sale import generate_sales
from src.generators.fact_transaction import generate_transactions
from src.generators.inventory import generate_inventories
from src.storage.s3_upload import upload_parquet_files
from src.storage.snowflake_upload import upload_from_s3_to_snowflake
from src.snowflake_setup.create_raw_tables import create_snowflake_bronze_tables
from src.run_dbt.run_models import run_dbt_models
import duckdb as db
import os
from dotenv import load_dotenv
import numpy as np
import random
from faker import Faker
from src.config.envariables import RANDOM_SEED
load_dotenv()

def create_snowflake_tables():
    create_snowflake_bronze_tables()

def run_generators(conn):
    generate_dates(conn)
    generate_locations(conn)
    generate_stores(conn,num_of_stores=50)
    generate_categories(conn)
    generate_subcategories(conn)
    generate_brands(conn)
    generate_products(conn)
    generate_customers(conn,num_of_customers=150_000)
    generate_promotions(conn, num_of_promotions=150)
    generate_campaigns(conn,number_of_campaigns=120)
    generate_clickstreams(conn,num_of_sessions_y1=3000000, num_of_sessions_y2=5000000, num_of_sessions_y3=6500000)
    generate_sales(conn, num_of_transactions=900_000)
    generate_transactions(conn)
    generate_inventories(conn)


def run_storage_layer():
    upload_parquet_files()

def run_warehouse():
    upload_from_s3_to_snowflake()

def run_transformation():
    run_dbt_models()

def run_all():

    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    Faker.seed(RANDOM_SEED)

    create_snowflake_tables()
    
    with db.connect() as conn:
       run_generators(conn=conn) 
        
    run_storage_layer()
    run_warehouse()
    run_transformation()

        
run_all()


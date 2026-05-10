from faker import Faker
import numpy as np
import pandas as pd
from datetime import timedelta
import re
from src.config.constants import (
    CUSTOMER_EMAIL_OPT_IN, CUSTOMER_GENDER, CUSTOMER_SIGNUP_CHANNEL, CUSTOMER_SMS_OPT_IN,
    BASE_TRANSACTION_END_TIMESTAMP_Y3, CUSTOMER_EMAIL_DOMAIN, COMPANY_START_DATE, CUSTOMERS_PERSONA_MAP, CUSTOMER_PERSONAS, PERSONA_WEIGHTS, SIGNUP_MONTH_WEIGHTS
)
from src.config.paths import CUSTOMERS_DDL_PATH, CUSTOMERS_PARQUET_PATH

FAKE = Faker("en_CA")

def generate_customers(conn, num_of_customers):

    create_db = CUSTOMERS_DDL_PATH.read_text()

    conn.execute(create_db)

    customer_ids = np.arange(1,num_of_customers + 1)

    urban_location_data = conn.execute("""select distinct s.location_id, l.location_weight from dim_store s join dim_location l on s.location_id = l.location_id 
                                       where l.location_type = 'Urban'""").df()
    suburban_location_data = conn.execute("""select distinct s.location_id, l.location_weight from dim_store s join dim_location l on s.location_id = l.location_id 
                                          where l.location_type = 'Suburban'""").df()
    rural_location_data = conn.execute("""select distinct s.location_id, l.location_weight from dim_store s join dim_location l on s.location_id = l.location_id 
                                        where l.location_type = 'Rural'""").df()
    

    customer_personas = np.random.choice(CUSTOMER_PERSONAS, p = PERSONA_WEIGHTS, size=num_of_customers)

    customer_age_lo = np.array([CUSTOMERS_PERSONA_MAP[cp]['age_range'][0]
                                for cp in customer_personas])
    
    customer_age_hi = np.array([CUSTOMERS_PERSONA_MAP[cp]['age_range'][1]
                                for cp in customer_personas])
    
    customer_age = np.random.randint(customer_age_lo, customer_age_hi + 1)

    tech_enthusiast_mask = customer_personas == "Tech Enthusiast"
    bargain_hunter_mask = customer_personas == "Bargain Hunter"
    gift_shopper_mask = customer_personas == "Gift Shopper"
    everyday_shopper_mask = customer_personas == "Everyday Shopper"
    practical_buyer_mask = customer_personas == "Practical Buyer"

    customer_genders = np.empty(num_of_customers, dtype=object)

    customer_genders[tech_enthusiast_mask] = np.random.choice(CUSTOMER_GENDER, p = CUSTOMERS_PERSONA_MAP['Tech Enthusiast']['gender_weight'], size = tech_enthusiast_mask.sum())
    customer_genders[bargain_hunter_mask] = np.random.choice(CUSTOMER_GENDER, p = CUSTOMERS_PERSONA_MAP['Bargain Hunter']['gender_weight'], size = bargain_hunter_mask.sum())
    customer_genders[gift_shopper_mask] = np.random.choice(CUSTOMER_GENDER, p = CUSTOMERS_PERSONA_MAP['Gift Shopper']['gender_weight'], size = gift_shopper_mask.sum())
    customer_genders[everyday_shopper_mask] = np.random.choice(CUSTOMER_GENDER, p = CUSTOMERS_PERSONA_MAP['Everyday Shopper']['gender_weight'], size = everyday_shopper_mask.sum())
    customer_genders[practical_buyer_mask] = np.random.choice(CUSTOMER_GENDER, p = CUSTOMERS_PERSONA_MAP['Practical Buyer']['gender_weight'], size = practical_buyer_mask.sum())



    male_mask = customer_genders == 'Male'

    female_mask = customer_genders == 'Female'

    other_mask = customer_genders == 'Other'

    customers_first_names = np.empty(num_of_customers, dtype=object)
    customers_last_names = np.empty(num_of_customers, dtype=object)

    customers_first_names[male_mask] = [FAKE.first_name_male() for _ in range(male_mask.sum())]
    customers_first_names[female_mask] = [FAKE.first_name_female() for _ in range(female_mask.sum())]
    customers_first_names[other_mask] = [FAKE.first_name() for _ in range(other_mask.sum())]

    customers_last_names[male_mask] = [FAKE.last_name_male() for _ in range(male_mask.sum())]
    customers_last_names[female_mask] = [FAKE.last_name_female() for _ in range(female_mask.sum())]
    customers_last_names[other_mask] = [FAKE.last_name() for _ in range(other_mask.sum())]

    email_domains  = np.random.choice(CUSTOMER_EMAIL_DOMAIN, size = num_of_customers)

    first_name_clean = np.array([re.sub(r'[^a-z]', '', name.lower())
                                for name in customers_first_names])
    
    last_name_clean = np.array([re.sub(r'[^a-z]', '', name.lower())
                                for name in customers_last_names])
    
    email_addresses = np.array([
                f"{first_name}.{last_name}.{cid}{domain}".lower()
                for first_name, last_name, cid, domain in zip(first_name_clean, last_name_clean, customer_ids, email_domains)
    ])


    date_range = pd.date_range(
    start=COMPANY_START_DATE,
    end=BASE_TRANSACTION_END_TIMESTAMP_Y3.date(),
    freq='D'
)

    signup_weights = np.array([SIGNUP_MONTH_WEIGHTS[date.month - 1] for date in date_range])
    signup_weights = signup_weights / signup_weights.sum()

    sampled_dates = np.random.choice(date_range, size=num_of_customers, p=signup_weights)


    random_seconds = np.random.randint(0, 86400, size=num_of_customers)
    signup_date = np.array([
    pd.Timestamp(d).date() + timedelta(seconds=int(s))
    for d, s in zip(sampled_dates, random_seconds)
    ])

    signup_date_ids = np.array([
    int(d.strftime('%Y%m%d')) for d in signup_date
        ])
    
    location_ids = np.empty(num_of_customers, dtype=int)
    location_ids[tech_enthusiast_mask] = np.random.choice(urban_location_data['location_id'], p = urban_location_data['location_weight']/urban_location_data['location_weight'].sum(), size = tech_enthusiast_mask.sum())
    location_ids[bargain_hunter_mask] = np.random.choice(urban_location_data['location_id'], p = urban_location_data['location_weight']/urban_location_data['location_weight'].sum(), size = bargain_hunter_mask.sum())
    location_ids[gift_shopper_mask] = np.random.choice(suburban_location_data['location_id'], p = suburban_location_data['location_weight']/suburban_location_data['location_weight'].sum(), size = gift_shopper_mask.sum())
    location_ids[everyday_shopper_mask] = np.random.choice(suburban_location_data['location_id'], p = suburban_location_data['location_weight']/suburban_location_data['location_weight'].sum(), size = everyday_shopper_mask.sum())
    if len(rural_location_data) > 0:  # In case there are no rural locations, avoid error
        location_ids[practical_buyer_mask] = np.random.choice(rural_location_data['location_id'], p = rural_location_data['location_weight']/rural_location_data['location_weight'].sum(), size = practical_buyer_mask.sum())
    else:
        location_ids[practical_buyer_mask] = np.random.choice(suburban_location_data['location_id'], p = suburban_location_data['location_weight']/suburban_location_data['location_weight'].sum(), size = practical_buyer_mask.sum())

    birth_dates = np.array([
    BASE_TRANSACTION_END_TIMESTAMP_Y3 - timedelta(days=int(age * 365.25))
    for age in customer_age
])

    birth_year = np.array([bd.year
                           for bd in birth_dates])
    
    customer_income_range_lo = np.array([CUSTOMERS_PERSONA_MAP[k]['income_range'][0] for k in customer_personas])
    customer_income_range_hi = np.array([CUSTOMERS_PERSONA_MAP[k]['income_range'][1] for k in customer_personas])

    estimated_annual_income = np.random.randint(customer_income_range_lo, customer_income_range_hi + 1) 
    
    high_value_mask = np.isin(customer_personas, ["Tech Enthusiast"])

    mid_value_mask = np.isin(customer_personas, ["Bargain Hunter","Gift Shopper","Everyday Shopper"])

    loyalty_status = np.full(num_of_customers,"Basic", dtype=object)

    loyalty_status[high_value_mask] = np.random.choice(["Elite","Gold"], p = [0.4,0.6], size=high_value_mask.sum())
    loyalty_status[mid_value_mask] = np.random.choice(["Gold","Silver","Basic"], p = [0.3,0.3,0.4], size=mid_value_mask.sum())

    customers_sms_opt_in = np.full(num_of_customers, False, dtype=bool)
    customers_email_opt_in = np.full(num_of_customers, False, dtype=bool)

    customers_sms_opt_in[tech_enthusiast_mask] = np.random.choice(CUSTOMER_SMS_OPT_IN, p = [0.6, 0.4], size = tech_enthusiast_mask.sum())
    customers_sms_opt_in[bargain_hunter_mask] = np.random.choice(CUSTOMER_SMS_OPT_IN, p = [0.5, 0.5], size = bargain_hunter_mask.sum())
    customers_sms_opt_in[gift_shopper_mask] = np.random.choice(CUSTOMER_SMS_OPT_IN, p = [0.3, 0.7], size = gift_shopper_mask.sum())
    customers_sms_opt_in[everyday_shopper_mask] = np.random.choice(CUSTOMER_SMS_OPT_IN, p = [0.4, 0.6], size = everyday_shopper_mask.sum())
    customers_sms_opt_in[practical_buyer_mask] = np.random.choice(CUSTOMER_SMS_OPT_IN, p = [0.2, 0.8], size = practical_buyer_mask.sum())

    customers_email_opt_in[tech_enthusiast_mask] = np.random.choice(CUSTOMER_EMAIL_OPT_IN, p = [0.9, 0.1], size = tech_enthusiast_mask.sum())
    customers_email_opt_in[bargain_hunter_mask] = np.random.choice(CUSTOMER_EMAIL_OPT_IN, p = [0.85, 0.15], size = bargain_hunter_mask.sum())
    customers_email_opt_in[gift_shopper_mask] = np.random.choice(CUSTOMER_EMAIL_OPT_IN, p = [0.8, 0.2], size = gift_shopper_mask.sum())
    customers_email_opt_in[everyday_shopper_mask] = np.random.choice(CUSTOMER_EMAIL_OPT_IN, p = [0.7, 0.3], size = everyday_shopper_mask.sum())
    customers_email_opt_in[practical_buyer_mask] = np.random.choice(CUSTOMER_EMAIL_OPT_IN, p = [0.5, 0.5], size = practical_buyer_mask.sum())

    signup_channels = np.full(num_of_customers, "Online", dtype=object)

    signup_channels[tech_enthusiast_mask] = np.random.choice(CUSTOMER_SIGNUP_CHANNEL, p = [0.2, 0.3, 0.5], size = tech_enthusiast_mask.sum())
    signup_channels[bargain_hunter_mask] = np.random.choice(CUSTOMER_SIGNUP_CHANNEL, p = [0.1, 0.5, 0.4], size = bargain_hunter_mask.sum())
    signup_channels[gift_shopper_mask] = np.random.choice(CUSTOMER_SIGNUP_CHANNEL, p = [0.3, 0.4, 0.3], size = gift_shopper_mask.sum())
    signup_channels[everyday_shopper_mask] = np.random.choice(CUSTOMER_SIGNUP_CHANNEL, p = [0.4, 0.35, 0.25], size = everyday_shopper_mask.sum())
    signup_channels[practical_buyer_mask] = np.random.choice(CUSTOMER_SIGNUP_CHANNEL, p = [0.7, 0.2, 0.1], size = practical_buyer_mask.sum())

    df_raw = pd.DataFrame({
        "customer_id":customer_ids,
        "email_address":email_addresses,
        "first_name":first_name_clean,
        "last_name":last_name_clean,
        "gender":customer_genders,
        "customer_persona":customer_personas,
        "birth_date":birth_dates,
        "birth_year":birth_year,
        "location_id":location_ids,
        "signup_date":signup_date,
        "signup_date_id":signup_date_ids,
        "signup_channel":signup_channels,
        "loyalty_status":loyalty_status,
        "estimated_annual_income":estimated_annual_income,
        "email_opt_in":customers_email_opt_in,
        "sms_opt_in":customers_sms_opt_in
    })

    conn.register("df_raw",df_raw)

    conn.execute('INSERT INTO DIM_CUSTOMER SELECT * FROM DF_RAW')

    conn.execute(f'''
                    COPY DIM_CUSTOMER TO '{CUSTOMERS_PARQUET_PATH}' (FORMAT PARQUET)
''')


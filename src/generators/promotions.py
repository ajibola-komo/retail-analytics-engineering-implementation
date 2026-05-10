import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from src.config.paths import (PROMOTIONS_DDL_PATH, PROMOTIONS_PARQUET_PATH)
from src.config.constants import (PROMO_TYPE_MAP, PROMO_TYPES, PROMO_TYPES_WEIGHTS, PROMOTION_DISCOUNT_TYPES, 
                                  PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y1, PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y2, 
                                  PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y3,
                                  PRE_HOLIDAY_PROMOTIONS_NAMES, OTHER_PROMOTIONS_NAMES, 
                                  JAN_FEB_PROMOTIONS_NAMES, WEEKEND_PROMOTIONS_NAMES,
                                  MID_YEAR_PROMOTIONS_NAMES, Y2, Y3, YEAR_END_PROMOTIONS_NAMES, BLACK_FRIDAY_PROMOTION_NAMES,
                                  PERCENTAGE_DISCOUNT_VALUES, PERCENTAGE_DISCOUNT_WEIGHTING, FIXED_AMOUNT_DISCOUNT_VALUES, 
                                  FIXED_AMOUNT_DISCOUNT_WEIGHTING,BASE_TRANSACTION_TIME_STAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y3,
                                  MONTH_WEIGHTS_PROMOTIONS_Y1, MONTH_WEIGHTS_PROMOTIONS_Y2, MONTH_WEIGHTS_PROMOTIONS_Y3,
                                  BASE_TRANSACTION_END_TIMESTAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y2, BASE_TRANSACTION_TIME_STAMP_Y2, BASE_TRANSACTION_TIME_STAMP_Y3,
                                  CURRENT_TIMESTAMP
                                  )

def gen_promo_name(start_date):

    week_day = start_date.weekday()
    month = start_date.month

    if week_day in (5, 6):
         promo_name = np.random.choice(WEEKEND_PROMOTIONS_NAMES)
    elif month == 11 and start_date.day >= 15:
        promo_name = np.random.choice(BLACK_FRIDAY_PROMOTION_NAMES)
    elif month == 12:
        promo_name = np.random.choice(YEAR_END_PROMOTIONS_NAMES)
    elif month in (1, 2):
        promo_name = np.random.choice(JAN_FEB_PROMOTIONS_NAMES)
    elif month in (5, 6, 7, 8):
        promo_name = np.random.choice(MID_YEAR_PROMOTIONS_NAMES)
    elif month in (9, 10):
        promo_name = np.random.choice(PRE_HOLIDAY_PROMOTIONS_NAMES)
    else:
        promo_name = np.random.choice(OTHER_PROMOTIONS_NAMES)
    
    return promo_name

def generate_promotions(conn, num_of_promotions):

    create_db = PROMOTIONS_DDL_PATH.read_text()

    conn.execute(create_db)
    promo_ids = np.arange(1,num_of_promotions + 1)

    promo_types = np.random.choice(PROMO_TYPES, p = PROMO_TYPES_WEIGHTS, size = num_of_promotions)

    promo_duration = np.array([np.random.choice(PROMO_TYPE_MAP[pt]['promo_duration'])
                               for pt in promo_types])

    promo_start_dates = np.empty(num_of_promotions, dtype='datetime64[ns]')

    n_y1 = int(num_of_promotions * 0.25)  # 38
    n_y2 = int(num_of_promotions * 0.35)  # 52
    n_y3 = num_of_promotions - n_y1 - n_y2  # remainder → 60, avoids rounding gap

    date_range_y1 = pd.date_range(start=BASE_TRANSACTION_TIME_STAMP_Y1, end=BASE_TRANSACTION_END_TIMESTAMP_Y1, freq='D')
    date_range_y2 = pd.date_range(start=BASE_TRANSACTION_TIME_STAMP_Y2, end=BASE_TRANSACTION_END_TIMESTAMP_Y2, freq='D')
    date_range_y3 = pd.date_range(start=BASE_TRANSACTION_TIME_STAMP_Y3, end=BASE_TRANSACTION_END_TIMESTAMP_Y3, freq='D')

    date_weights_y1 = np.array([MONTH_WEIGHTS_PROMOTIONS_Y1[d.month - 1] for d in date_range_y1])
    date_weights_y2 = np.array([MONTH_WEIGHTS_PROMOTIONS_Y2[d.month - 1] for d in date_range_y2])
    date_weights_y3 = np.array([MONTH_WEIGHTS_PROMOTIONS_Y3[d.month - 1] for d in date_range_y3])

    signup_weights_y1 = date_weights_y1 / date_weights_y1.sum()
    signup_weights_y2 = date_weights_y2 / date_weights_y2.sum()
    signup_weights_y3 = date_weights_y3 / date_weights_y3.sum()

    sampled_dates_y1 = np.random.choice(date_range_y1, size=n_y1, p=signup_weights_y1)
    sampled_dates_y2 = np.random.choice(date_range_y2, size=n_y2, p=signup_weights_y2)
    sampled_dates_y3 = np.random.choice(date_range_y3, size=n_y3, p=signup_weights_y3)

    sampled_dates = np.concatenate([sampled_dates_y1, sampled_dates_y2, sampled_dates_y3])

    random_seconds = np.random.randint(0, 86400, size=len(sampled_dates))  # sized to actual total

    promo_start_dates = np.array([
    pd.Timestamp(d).date() + timedelta(seconds=int(s))
    for d, s in zip(sampled_dates, random_seconds)
])
    
    promo_end_dates = np.array([
    pd.Timestamp(s) + timedelta(days=int(d))
    for s, d in zip(promo_start_dates, promo_duration)
    ])  

    promo_start_date_ids = np.array([
    int(pd.Timestamp(d).strftime('%Y%m%d'))
    for d in promo_start_dates
    ])

    promo_end_date_ids = np.array([
    int(pd.Timestamp(d).strftime('%Y%m%d'))
    for d in promo_end_dates
    ])

    is_active = pd.to_datetime(promo_end_dates) >= pd.Timestamp(CURRENT_TIMESTAMP)

    discount_types = np.empty(num_of_promotions, dtype=object)

    y1_promo = np.where(pd.to_datetime(promo_start_dates) < pd.Timestamp(f"{Y2}-01-01"))[0]
    y2_promo = np.where(
        (pd.to_datetime(promo_start_dates) >= pd.Timestamp(f"{Y2}-01-01")) &
        (pd.to_datetime(promo_start_dates) < pd.Timestamp(f"{Y3}-01-01"))
    )[0]
    y3_promo = np.where(pd.to_datetime(promo_start_dates) >= pd.Timestamp(f"{Y3}-01-01"))[0]
    discount_types[y1_promo] = np.random.choice(PROMOTION_DISCOUNT_TYPES, p = PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y1, size=len(y1_promo))
    discount_types[y2_promo] = np.random.choice(PROMOTION_DISCOUNT_TYPES, p = PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y2, size=len(y2_promo))
    discount_types[y3_promo] = np.random.choice(PROMOTION_DISCOUNT_TYPES, p = PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y3, size=len(y3_promo))

    percentage_discount_values = discount_types == 'Percentage_Discount'
    fixed_discount_values = discount_types == 'Fixed_Amount_Discount'

    discount_values = np.full(num_of_promotions,0.0, dtype=float)

    discount_values[percentage_discount_values] = np.random.choice(PERCENTAGE_DISCOUNT_VALUES, p = PERCENTAGE_DISCOUNT_WEIGHTING, size=percentage_discount_values.sum())

    discount_values[fixed_discount_values] = np.random.choice(FIXED_AMOUNT_DISCOUNT_VALUES, p = FIXED_AMOUNT_DISCOUNT_WEIGHTING, size= fixed_discount_values.sum())

    
    promo_names = promo_names = np.array([
    gen_promo_name(pd.Timestamp(d))
    for d in promo_start_dates
])

    promo_codes = np.array([
    f"{pt[:3].upper()}-{pd.Timestamp(d).year}{pd.Timestamp(d).month:02d}-{pid}"
    for pt, d, pid in zip(promo_types, promo_start_dates, promo_ids)
])

    promo_description_suffixes = np.empty(num_of_promotions, dtype = object)

    promo_description_suffixes[percentage_discount_values] = np.array([
        f"Get {int(dv * 100)}% Off" for dv in discount_values[percentage_discount_values]
    ])

    promo_description_suffixes[fixed_discount_values] = np.array([
        f" Get ${int(dv)} Off" for dv in discount_values[fixed_discount_values]
    ])

    promo_descriptions = np.array([
        pn + " " + pds 
        for pn, pds in zip(promo_names, promo_description_suffixes)
    ])

    df_raw = pd.DataFrame({
        "promo_id":promo_ids,
        "promo_name":promo_names,
        "promo_type":promo_types,
        "discount_type":discount_types,
        "discount_value":discount_values,
        "promo_start_date":promo_start_dates,
        "promo_start_date_id":promo_start_date_ids,
        "promo_end_date":promo_end_dates,
        "promo_end_date_id":promo_end_date_ids,
        "promo_duration":promo_duration,
        "promo_code":promo_codes,
        "is_active":is_active,
        "promo_description":promo_descriptions
    })

    conn.register("DF_RAW",df_raw)

    conn.execute("INSERT INTO DIM_PROMOTION SELECT * FROM DF_RAW")

    conn.execute(f'''
                    COPY DIM_PROMOTION TO '{PROMOTIONS_PARQUET_PATH}' (FORMAT PARQUET)
''')
    

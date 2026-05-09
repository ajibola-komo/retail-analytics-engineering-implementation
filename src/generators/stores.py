import numpy as np
import pandas as pd
from datetime import timedelta
from src.config.paths import (STORES_DDL_PATH, STORES_PARQUET_PATH)
from src.config.constants import (COMPANY_START_TIMESTAMP, STORE_TYPES_MAP,STORE_TYPES,STORE_WEIGHTS, 
                                  BASE_TRANSACTION_TIME_STAMP_Y1, COMPANY_NAME, CURRENT_DATE)

def generate_stores(conn, num_of_stores):
    total_days = (BASE_TRANSACTION_TIME_STAMP_Y1 - COMPANY_START_TIMESTAMP).days

    create_db = STORES_DDL_PATH.read_text()
    conn.execute(create_db)

    conn.execute("DELETE FROM DIM_STORE")

    loc_data = conn.execute('SELECT location_id, location_weight, foot_traffic_min, foot_traffic_max FROM dim_location').df()
    
    selected_types = np.random.choice(STORE_TYPES, size=num_of_stores, p=STORE_WEIGHTS)

    store_ids = np.arange(1,num_of_stores+1)

    location_ids = np.random.choice(loc_data['location_id'], p = loc_data['location_weight'], size=num_of_stores)

    store_sizes_lo = np.array([STORE_TYPES_MAP[i]['store_size'][0]
        for i in selected_types])
    
    store_sizes_hi = np.array([STORE_TYPES_MAP[i]['store_size'][1]
        for i in selected_types])
    
    store_sizes = np.random.randint(store_sizes_lo, store_sizes_hi + 1)

    last_new_store_day = CURRENT_DATE - timedelta(days=365 * 5)

    duration = int((pd.to_datetime(last_new_store_day) - COMPANY_START_TIMESTAMP).days)

    random_offset = np.sort(np.random.randint(0,duration, size=num_of_stores))

    random_offset[0] = 0

    opening_dates = np.array([
        COMPANY_START_TIMESTAMP + timedelta(days=int(ro))
        for ro in random_offset
    ])

    opening_date_ids = np.array([
    int(d.strftime('%Y%m%d')) for d in opening_dates
        ])

    loc_lookup = loc_data.set_index('location_id')

    foot_traffic_lo = loc_lookup.loc[
    location_ids, 'foot_traffic_min'
    ].values

    foot_traffic_hi = loc_lookup.loc[
    location_ids, 'foot_traffic_max'
    ].values

    foot_traffic_index = np.random.randint(
    foot_traffic_lo,
    foot_traffic_hi + 1
    )

    df_stores = pd.DataFrame({
        'store_id': store_ids,
        'store_name': [f"{COMPANY_NAME} Store #{i}" for i in range(1, num_of_stores + 1)],
        'location_id': location_ids.astype(int),
        'store_type': selected_types,
        'store_size': store_sizes,
        'opening_date': opening_dates,
        'opening_date_id':opening_date_ids,
        'foot_traffic_index': foot_traffic_index
    })

    conn.register('df_stores', df_stores)
    conn.execute("INSERT INTO dim_store SELECT * FROM df_stores")
    conn.execute(f'''
                    COPY DIM_STORE TO '{STORES_PARQUET_PATH}' (FORMAT PARQUET)
''')
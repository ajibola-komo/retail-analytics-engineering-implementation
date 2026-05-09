import numpy as np
import duckdb as db
import pandas as pd
from datetime import datetime, timedelta
from src.config.paths import CAMPAIGNS_DDL_PATH, CAMPAIGNS_CSV_PATH, CAMPAIGNS_PARQUET_PATH
from src.config.constants import (
                BASE_TRANSACTION_TIME_STAMP_Y1, CAMPAIGN_CHANNEL, CAMPAIGN_CHANNELS_WEIGHTS_Y1, CAMPAIGN_CHANNELS_WEIGHTS_Y2, CAMPAIGN_CHANNELS_WEIGHTS_Y3,
                BASE_TRANSACTION_END_TIMESTAMP_Y3, CAMPAIGN_PERIOD_OF_VALIDITY,Y1,Y2,Y3
              )

def generate_campaigns(conn, number_of_campaigns):

    create_db = CAMPAIGNS_DDL_PATH.read_text()

    conn.execute(create_db)

    promo_data = conn.execute("SELECT promo_id, promo_start_date, promo_end_date from dim_promotion").df()

    campaign_ids = np.arange(1, number_of_campaigns + 1)

    campaign_start_dates = np.empty(number_of_campaigns, dtype='datetime64[ns]')
    campaign_end_dates = np.empty(number_of_campaigns, dtype='datetime64[ns]')

    base_np = np.datetime64(BASE_TRANSACTION_TIME_STAMP_Y1)

    total_duration = int((BASE_TRANSACTION_END_TIMESTAMP_Y3 - BASE_TRANSACTION_TIME_STAMP_Y1).total_seconds())

    random_offset = np.random.randint(0,total_duration + 1, size = number_of_campaigns)

    random_offset_td = random_offset.astype('timedelta64[s]')

    campaign_start_dates = base_np + random_offset_td

    campaign_validity_hours = np.random.choice(CAMPAIGN_PERIOD_OF_VALIDITY, size=number_of_campaigns)

    campaign_end_dates = campaign_start_dates + campaign_validity_hours.astype('timedelta64[h]')
    
    campaign_start_date_ids = pd.to_datetime(campaign_start_dates).strftime('%Y%m%d').astype(int).values

    campaign_end_date_ids = pd.to_datetime(campaign_end_dates).strftime('%Y%m%d').astype(int).values

    campaign_names = np.array([
        f"Campaign #{id}" for id in campaign_ids
    ])

    campaign_channels = np.empty(number_of_campaigns, dtype=object)
    y1_campaign = np.where(campaign_start_dates < np.datetime64(f"{Y2}-01-01"))[0]
    y2_campaign = np.where((campaign_start_dates >= np.datetime64(f"{Y2}-01-01")) & (campaign_start_dates < np.datetime64(f"{Y3}-01-01")))[0]
    y3_campaign = np.where(campaign_start_dates >= np.datetime64(f"{Y3}-01-01"))[0]


    campaign_channels[y1_campaign] = np.random.choice(CAMPAIGN_CHANNEL, p = CAMPAIGN_CHANNELS_WEIGHTS_Y1, size=len(y1_campaign))
    campaign_channels[y2_campaign] = np.random.choice(CAMPAIGN_CHANNEL, p = CAMPAIGN_CHANNELS_WEIGHTS_Y2, size=len(y2_campaign))
    campaign_channels[y3_campaign] = np.random.choice(CAMPAIGN_CHANNEL, p = CAMPAIGN_CHANNELS_WEIGHTS_Y3, size=len(y3_campaign))

    promo_index = np.empty(number_of_campaigns, dtype=object)

    for idx in range(len(campaign_start_dates)):

        promo_mask = np.where(
    (promo_data['promo_start_date'] <= campaign_end_dates[idx]) &
    (promo_data['promo_end_date'] >= campaign_start_dates[idx])
)[0]

        if len(promo_mask) > 0:
            eligible_promo_index = np.random.choice(promo_mask)

            promo_index[idx] = eligible_promo_index
        else:
            promo_index[idx] = None

    
    promo_linked_campaigns = pd.notna(promo_index)

    linked_indices = np.where(promo_linked_campaigns)[0]


    promo_ids = np.full(number_of_campaigns, None, dtype=object)

    for idx in linked_indices:
        promo_ids[idx] = promo_data.loc[promo_index[idx], 'promo_id']
        

    df_raw = pd.DataFrame({
        "campaign_id":campaign_ids,
        "campaign_name":campaign_names,
        "campaign_channel":campaign_channels,
        "promo_id":promo_ids,
        "campaign_start_date":campaign_start_dates,
        "campaign_start_date_id":campaign_start_date_ids,
        "campaign_end_date":campaign_end_dates,
        "campaign_end_date_id":campaign_end_date_ids,
        
                })
    
    conn.register("DF_RAW", df_raw)

    conn.execute("DELETE FROM DIM_CAMPAIGN")

    conn.execute("INSERT INTO dim_campaign SELECT * FROM DF_RAW")

    conn.execute(f'''
                    COPY DIM_CAMPAIGN TO '{CAMPAIGNS_PARQUET_PATH}' (FORMAT PARQUET)
''')



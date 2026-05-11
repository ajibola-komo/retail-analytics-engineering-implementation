import numpy as np
import duckdb as db
import pandas as pd
from datetime import datetime, timedelta
from src.config.paths import CAMPAIGNS_DDL_PATH, CAMPAIGNS_PARQUET_PATH
from src.config.constants import (
                BASE_TRANSACTION_TIME_STAMP_Y1, CAMPAIGN_CHANNEL, CAMPAIGN_CHANNELS_WEIGHTS_Y1, CAMPAIGN_CHANNELS_WEIGHTS_Y2, CAMPAIGN_CHANNELS_WEIGHTS_Y3,
                BASE_TRANSACTION_END_TIMESTAMP_Y3, CAMPAIGN_PERIOD_OF_VALIDITY, BASE_TRANSACTION_END_TIMESTAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y2, 
                BASE_TRANSACTION_TIME_STAMP_Y2, BASE_TRANSACTION_TIME_STAMP_Y3, MONTH_WEIGHTS_CAMPAIGNS_Y1, MONTH_WEIGHTS_CAMPAIGNS_Y2, MONTH_WEIGHTS_CAMPAIGNS_Y3,
                Y2, Y3
              )

def generate_campaigns(conn, number_of_campaigns):

    create_db = CAMPAIGNS_DDL_PATH.read_text()
    conn.execute(create_db)

    promo_data = conn.execute("SELECT promo_id, promo_start_date, promo_end_date FROM dim_promotion").df()
    promo_data['promo_start_date'] = pd.to_datetime(promo_data['promo_start_date'])
    promo_data['promo_end_date']   = pd.to_datetime(promo_data['promo_end_date'])

    campaign_ids = np.arange(1, number_of_campaigns + 1)

    # ── Date sampling ─────────────────────────────────────────────────────────
    n_y1 = int(number_of_campaigns * 0.3)
    n_y2 = int(number_of_campaigns * 0.35)
    n_y3 = number_of_campaigns - n_y1 - n_y2

    date_range_y1 = pd.date_range(start=BASE_TRANSACTION_TIME_STAMP_Y1, end=BASE_TRANSACTION_END_TIMESTAMP_Y1, freq='D')
    date_range_y2 = pd.date_range(start=BASE_TRANSACTION_TIME_STAMP_Y2, end=BASE_TRANSACTION_END_TIMESTAMP_Y2, freq='D')
    date_range_y3 = pd.date_range(start=BASE_TRANSACTION_TIME_STAMP_Y3, end=BASE_TRANSACTION_END_TIMESTAMP_Y3, freq='D')

    date_weights_y1 = np.array([MONTH_WEIGHTS_CAMPAIGNS_Y1[d.month - 1] for d in date_range_y1])
    date_weights_y2 = np.array([MONTH_WEIGHTS_CAMPAIGNS_Y2[d.month - 1] for d in date_range_y2])
    date_weights_y3 = np.array([MONTH_WEIGHTS_CAMPAIGNS_Y3[d.month - 1] for d in date_range_y3])

    signup_weights_y1 = date_weights_y1 / date_weights_y1.sum()
    signup_weights_y2 = date_weights_y2 / date_weights_y2.sum()
    signup_weights_y3 = date_weights_y3 / date_weights_y3.sum()

    sampled_dates_y1 = np.random.choice(date_range_y1, size=n_y1, p=signup_weights_y1)
    sampled_dates_y2 = np.random.choice(date_range_y2, size=n_y2, p=signup_weights_y2)
    sampled_dates_y3 = np.random.choice(date_range_y3, size=n_y3, p=signup_weights_y3)

    sampled_dates = np.concatenate([sampled_dates_y1, sampled_dates_y2, sampled_dates_y3])

    random_seconds = np.random.randint(0, 86400, size=len(sampled_dates))

    campaign_start_dates = np.array([
        pd.Timestamp(d).date() + timedelta(seconds=int(s))
        for d, s in zip(sampled_dates, random_seconds)
    ])

    # ── End dates ─────────────────────────────────────────────────────────────
    campaign_validity_hours = np.random.choice(CAMPAIGN_PERIOD_OF_VALIDITY, size=number_of_campaigns)
    campaign_start_dates_dt = pd.to_datetime(campaign_start_dates)
    campaign_end_dates       = campaign_start_dates_dt + pd.to_timedelta(campaign_validity_hours, unit='h')

    campaign_start_date_ids = campaign_start_dates_dt.strftime('%Y%m%d').astype(int).values
    campaign_end_date_ids   = campaign_end_dates.strftime('%Y%m%d').astype(int).values

    # ── Campaign names ────────────────────────────────────────────────────────
    campaign_names = np.array([f"Campaign #{cid}" for cid in campaign_ids])

    # ── Channel assignment (safe datetime comparison) ─────────────────────────
    campaign_channels = np.empty(number_of_campaigns, dtype=object)

    y1_campaign = np.where(campaign_start_dates_dt < pd.Timestamp(f"{Y2}-01-01"))[0]
    y2_campaign = np.where(
        (campaign_start_dates_dt >= pd.Timestamp(f"{Y2}-01-01")) &
        (campaign_start_dates_dt <  pd.Timestamp(f"{Y3}-01-01"))
    )[0]
    y3_campaign = np.where(campaign_start_dates_dt >= pd.Timestamp(f"{Y3}-01-01"))[0]

    campaign_channels[y1_campaign] = np.random.choice(CAMPAIGN_CHANNEL, p=CAMPAIGN_CHANNELS_WEIGHTS_Y1, size=len(y1_campaign))
    campaign_channels[y2_campaign] = np.random.choice(CAMPAIGN_CHANNEL, p=CAMPAIGN_CHANNELS_WEIGHTS_Y2, size=len(y2_campaign))
    campaign_channels[y3_campaign] = np.random.choice(CAMPAIGN_CHANNEL, p=CAMPAIGN_CHANNELS_WEIGHTS_Y3, size=len(y3_campaign))

    # ── Promo linking (fixed: store promo_id directly, no second loop) ────────
    promo_ids = np.full(number_of_campaigns, None, dtype=object)

    for idx in range(number_of_campaigns):
        promo_mask = np.where(
            (promo_data['promo_start_date'] <= campaign_end_dates[idx]) &
            (promo_data['promo_end_date']   >= campaign_start_dates_dt[idx])
        )[0]

        if len(promo_mask) > 0:
            chosen_position = np.random.choice(promo_mask)
            promo_ids[idx] = promo_data.iloc[chosen_position]['promo_id']  # ✓ positional + column name

    # ── Build DataFrame & persist ─────────────────────────────────────────────
    df_raw = pd.DataFrame({
        "campaign_id":           campaign_ids,
        "campaign_name":         campaign_names,
        "campaign_channel":      campaign_channels,
        "promo_id":              promo_ids,
        "campaign_start_date":   campaign_start_dates_dt,
        "campaign_start_date_id": campaign_start_date_ids,
        "campaign_end_date":     campaign_end_dates,
        "campaign_end_date_id":  campaign_end_date_ids,
    })

    conn.register("DF_RAW", df_raw)
    conn.execute("DELETE FROM DIM_CAMPAIGN")
    conn.execute("INSERT INTO dim_campaign SELECT * FROM DF_RAW")
    conn.execute(f"COPY DIM_CAMPAIGN TO '{CAMPAIGNS_PARQUET_PATH}' (FORMAT PARQUET)")
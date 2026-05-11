from src.config.constants import (BASE_TRANSACTION_END_TIMESTAMP_Y1, BASE_TRANSACTION_TIME_STAMP_Y1, MONTH_WEIGHTS_ONLINE_Y1,
MONTH_WEIGHTS_STORE_Y1, MONTH_WEIGHTS_ONLINE_Y2, MONTH_WEIGHTS_STORE_Y2, MONTH_WEIGHTS_ONLINE_Y3, MONTH_WEIGHTS_STORE_Y3, ORGANIC_SESSION_MINUTES, 
BASE_TRANSACTION_TIME_STAMP_Y2, BASE_TRANSACTION_END_TIMESTAMP_Y2, BASE_TRANSACTION_TIME_STAMP_Y3, BASE_TRANSACTION_END_TIMESTAMP_Y3)
import numpy as np
import pandas as pd

def generate_online_month_distribution(num_of_records_y1, num_of_records_y2, num_of_records_y3):
    date_range_y1 = pd.date_range(
        start=BASE_TRANSACTION_TIME_STAMP_Y1,
        end=BASE_TRANSACTION_END_TIMESTAMP_Y1,
        freq='D'
    )

    date_range_y2 = pd.date_range(
        start=BASE_TRANSACTION_TIME_STAMP_Y2,
        end=BASE_TRANSACTION_END_TIMESTAMP_Y2,
        freq='D'
    )

    date_range_y3 = pd.date_range(
        start=BASE_TRANSACTION_TIME_STAMP_Y3,
        end=BASE_TRANSACTION_END_TIMESTAMP_Y3,
        freq='D'
    )

    date_weights_y1 = np.array([
        MONTH_WEIGHTS_ONLINE_Y1[date.month - 1] for date in date_range_y1
    ])

    date_weights_y2 = np.array([
        MONTH_WEIGHTS_ONLINE_Y2[date.month - 1] for date in date_range_y2
    ])

    date_weights_y3 = np.array([
        MONTH_WEIGHTS_ONLINE_Y3[date.month - 1] for date in date_range_y3
    ])

    date_weights_y1 = date_weights_y1 / date_weights_y1.sum()
    date_weights_y2 = date_weights_y2 / date_weights_y2.sum()
    date_weights_y3 = date_weights_y3 / date_weights_y3.sum()

    sampled_dates_y1 = np.random.choice(
        date_range_y1,
        size=num_of_records_y1,
        p=date_weights_y1
    )

    sampled_dates_y2 = np.random.choice(
        date_range_y2,
        size=num_of_records_y2,
        p=date_weights_y2
    )

    sampled_dates_y3 = np.random.choice(
        date_range_y3,
        size=num_of_records_y3,
        p=date_weights_y3
    )   

    max_random_seconds = 86400 - (max(ORGANIC_SESSION_MINUTES) * 60)

    random_seconds_y1 = np.random.randint(0, max_random_seconds, size=num_of_records_y1)
    

    random_seconds_y2 = np.random.randint(
    0,
    max_random_seconds,
    size=num_of_records_y2
)
    random_seconds_y3 = np.random.randint(
    0,
    max_random_seconds,
    size=num_of_records_y3
)

    seasonal_timestamps_y1 = sampled_dates_y1 + pd.to_timedelta(random_seconds_y1, unit='s')
    seasonal_timestamps_y2 = sampled_dates_y2 + pd.to_timedelta(random_seconds_y2, unit='s')
    seasonal_timestamps_y3 = sampled_dates_y3 + pd.to_timedelta(random_seconds_y3, unit='s')

    return {"y1": pd.to_datetime(seasonal_timestamps_y1), "y2": pd.to_datetime(seasonal_timestamps_y2), "y3": pd.to_datetime(seasonal_timestamps_y3)}

def generate_in_store_month_distribution(num_of_transactions):
    num_of_records_y1 = int(num_of_transactions * 0.25)
    num_of_records_y2 = int(num_of_transactions * 0.35)
    num_of_records_y3 = num_of_transactions - num_of_records_y1 - num_of_records_y2
    date_range_y1 = pd.date_range(
        start=BASE_TRANSACTION_TIME_STAMP_Y1,
        end=BASE_TRANSACTION_END_TIMESTAMP_Y1,
        freq='D'
    )

    date_range_y2 = pd.date_range(
        start=BASE_TRANSACTION_TIME_STAMP_Y2,
        end=BASE_TRANSACTION_END_TIMESTAMP_Y2,
        freq='D'
    )

    date_range_y3 = pd.date_range(
        start=BASE_TRANSACTION_TIME_STAMP_Y3,
        end=BASE_TRANSACTION_END_TIMESTAMP_Y3,
        freq='D'
    )

    date_weights_y1 = np.array([
        MONTH_WEIGHTS_STORE_Y1[date.month - 1] for date in date_range_y1
    ])

    date_weights_y2 = np.array([
        MONTH_WEIGHTS_STORE_Y2[date.month - 1] for date in date_range_y2
    ])

    date_weights_y3 = np.array([
        MONTH_WEIGHTS_STORE_Y3[date.month - 1] for date in date_range_y3
    ])

    date_weights_y1 = date_weights_y1 / date_weights_y1.sum()
    date_weights_y2 = date_weights_y2 / date_weights_y2.sum()
    date_weights_y3 = date_weights_y3 / date_weights_y3.sum()

    sampled_dates_y1 = np.random.choice(
        date_range_y1,
        size=num_of_records_y1,
        p=date_weights_y1
    )

    sampled_dates_y2 = np.random.choice(
        date_range_y2,
        size=num_of_records_y2,
        p=date_weights_y2
    )

    sampled_dates_y3 = np.random.choice(
        date_range_y3,
        size=num_of_records_y3,
        p=date_weights_y3
    )

    random_seconds_y1 = np.random.randint(28800, 75600, size=num_of_records_y1)
    random_seconds_y2 = np.random.randint(28800, 75600, size=num_of_records_y2)
    random_seconds_y3 = np.random.randint(28800, 75600, size=num_of_records_y3)
    seasonal_timestamps_y1 = sampled_dates_y1 + pd.to_timedelta(random_seconds_y1, unit='s')
    seasonal_timestamps_y2 = sampled_dates_y2 + pd.to_timedelta(random_seconds_y2, unit='s')
    seasonal_timestamps_y3 = sampled_dates_y3 + pd.to_timedelta(random_seconds_y3, unit='s')

    return {"y1": pd.to_datetime(seasonal_timestamps_y1), "y2": pd.to_datetime(seasonal_timestamps_y2), "y3": pd.to_datetime(seasonal_timestamps_y3)}



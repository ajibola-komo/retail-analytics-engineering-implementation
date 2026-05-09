import numpy as np
import pandas as pd
from src.generators.month_distribution import generate_online_month_distribution
from src.generators.segment_customers import generate_customer_segments
from src.config.paths import (CLICKSTREAMS_DDL_PATH, CLICKSTREAMS_PARQUET_PATH)
from src.config.constants import (PROB_OF_PURCHASE_INTENTION_Y3, SESSION_START_ID, TRAFFIC_SOURCES, TRAFFIC_WEIGHTS_Y1, TRAFFIC_WEIGHTS_Y2, TRAFFIC_WEIGHTS_Y3,
                                  DEVICE_TYPES, DEVICE_WEIGHTS_Y1, DEVICE_WEIGHTS_Y2, DEVICE_WEIGHTS_Y3, SESSION_MINUTES, SESSION_WEIGHTS, 
                                  PROB_OF_CAMPAIGN_LINKED_Y1, PROB_OF_CAMPAIGN_LINKED_Y2, PROB_OF_PURCHASE_INTENTION_Y1, PROB_OF_PURCHASE_INTENTION_Y2, 
                                  PROB_OF_PURCHASE_Y1, PROB_OF_PURCHASE_Y2,
                                  PROB_OF_CUSTOMER_SESSION_Y1, PROB_OF_CUSTOMER_SESSION_Y2,
                                  BASE_TRANSACTION_TIME_STAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y2,
                                  BASE_TRANSACTION_TIME_STAMP_Y2, BASE_TRANSACTION_END_TIMESTAMP_Y3, BASE_TRANSACTION_TIME_STAMP_Y3, PROB_OF_CAMPAIGN_LINKED_Y3, 
                                  PROB_OF_CUSTOMER_SESSION_Y3, PROB_OF_PURCHASE_Y3
                            )



def generate_clickstreams(conn,num_of_sessions_y1, num_of_sessions_y2, num_of_sessions_y3): #conn takes in the connection object as an argument, num_of_sessions is the total number of sessions to generate across both years

    # Generate customer segments to be used in clickstream generation
    customer_segments = generate_customer_segments(conn)

    all_customers = customer_segments["all_customers"]
    premium_customers = customer_segments["premium"]
    mid_level_customers = customer_segments["mid"]
    basic_level_customers = customer_segments["basic"]

    premium_customers["activity_weight"] = np.random.pareto(2, len(premium_customers)) + 1

    mid_level_customers["activity_weight"] = np.random.pareto(3, len(mid_level_customers)) + 1

    basic_level_customers["activity_weight"] = np.random.pareto(4, len(basic_level_customers)) + 1

    campaigns_data = conn.execute("select campaign_id, campaign_start_date, campaign_end_date from dim_campaign").df()

    session_ids = np.arange(SESSION_START_ID, SESSION_START_ID + num_of_sessions_y1 + num_of_sessions_y2 + num_of_sessions_y3)

    online_distribution = generate_online_month_distribution(
    num_of_sessions_y1,
    num_of_sessions_y2,
    num_of_sessions_y3
)

    session_start_times = pd.to_datetime(
    online_distribution["y1"].tolist()
    + online_distribution["y2"].tolist()
    + online_distribution["y3"].tolist()
)

    total_sessions = num_of_sessions_y1 + num_of_sessions_y2 + num_of_sessions_y3

    durations = np.random.choice(SESSION_MINUTES, p = SESSION_WEIGHTS, size= total_sessions)

    session_end_times = session_start_times + pd.to_timedelta(durations, unit="m")

    device_types = np.empty(total_sessions, dtype=object)

    number_of_pages_viewed = np.where(durations <= 2, np.random.randint(1,4,size=total_sessions),
                                    np.where((durations > 2) & (durations <= 5), np.random.randint(4,7, size = total_sessions),
                                             np.random.randint(7,13, size= total_sessions)))


    aov = np.full(total_sessions, None, dtype=object)

    product_page_visited_flag = number_of_pages_viewed >= 4
    y1_sessions = (session_start_times >= pd.to_datetime(BASE_TRANSACTION_TIME_STAMP_Y1)) & (session_start_times <= pd.to_datetime(BASE_TRANSACTION_END_TIMESTAMP_Y1))
    y2_sessions = (session_start_times >= pd.to_datetime(BASE_TRANSACTION_TIME_STAMP_Y2)) & (session_start_times <= pd.to_datetime(BASE_TRANSACTION_END_TIMESTAMP_Y2))
    y3_sessions = (session_start_times >= pd.to_datetime(BASE_TRANSACTION_TIME_STAMP_Y3)) & (session_start_times <= pd.to_datetime(BASE_TRANSACTION_END_TIMESTAMP_Y3))
    
    added_to_cart_flag = np.zeros(total_sessions, dtype=bool)
    purchased_flag = np.zeros(total_sessions, dtype=bool)
    is_customer_session = np.zeros(total_sessions, dtype=bool)
    probability_of_campaign_linked = np.zeros(total_sessions, dtype=bool)

    device_types[y1_sessions] = np.random.choice(DEVICE_TYPES, p = DEVICE_WEIGHTS_Y1, size=y1_sessions.sum())
    device_types[y2_sessions] = np.random.choice(DEVICE_TYPES, p = DEVICE_WEIGHTS_Y2, size=y2_sessions.sum())
    device_types[y3_sessions] = np.random.choice(DEVICE_TYPES, p = DEVICE_WEIGHTS_Y3, size=y3_sessions.sum())

    y1_product_sessions = y1_sessions & product_page_visited_flag
    y2_product_sessions = y2_sessions & product_page_visited_flag
    y3_product_sessions = y3_sessions & product_page_visited_flag

    added_to_cart_flag[y1_product_sessions] = (
    np.random.rand(y1_product_sessions.sum())
    <= PROB_OF_PURCHASE_INTENTION_Y1
    )

    added_to_cart_flag[y2_product_sessions] = (
    np.random.rand(y2_product_sessions.sum())
    <= PROB_OF_PURCHASE_INTENTION_Y2
    )

    added_to_cart_flag[y3_product_sessions] = (
    np.random.rand(y3_product_sessions.sum())
    <= PROB_OF_PURCHASE_INTENTION_Y3
    )

    purchased_flag[y1_sessions] = added_to_cart_flag[y1_sessions] & (np.random.rand(y1_sessions.sum()) <= PROB_OF_PURCHASE_Y1)
    purchased_flag[y2_sessions] = added_to_cart_flag[y2_sessions] & (np.random.rand(y2_sessions.sum()) <= PROB_OF_PURCHASE_Y2)
    purchased_flag[y3_sessions] = added_to_cart_flag[y3_sessions] & (np.random.rand(y3_sessions.sum()) <= PROB_OF_PURCHASE_Y3)

    is_customer_session[y1_sessions] = np.random.rand(y1_sessions.sum()) <= PROB_OF_CUSTOMER_SESSION_Y1
    is_customer_session[y2_sessions] = np.random.rand(y2_sessions.sum()) <= PROB_OF_CUSTOMER_SESSION_Y2
    is_customer_session[y3_sessions] = np.random.rand(y3_sessions.sum()) <= PROB_OF_CUSTOMER_SESSION_Y3
    customer_ids = np.full(num_of_sessions_y1 + num_of_sessions_y2 + num_of_sessions_y3, None, dtype=object)

    probability_of_campaign_linked[y1_sessions] = np.random.rand(y1_sessions.sum()) <= PROB_OF_CAMPAIGN_LINKED_Y1
    probability_of_campaign_linked[y2_sessions] = np.random.rand(y2_sessions.sum()) <= PROB_OF_CAMPAIGN_LINKED_Y2
    probability_of_campaign_linked[y3_sessions] = np.random.rand(y3_sessions.sum()) <= PROB_OF_CAMPAIGN_LINKED_Y3
    eligible_idx = np.where(probability_of_campaign_linked)[0]

    campaign_ids_for_sessions = np.full(total_sessions, None, dtype = object)

    eligible_starts = session_start_times[eligible_idx].to_numpy()

    camp_starts = pd.to_datetime(campaigns_data['campaign_start_date']).to_numpy()
    camp_ends = pd.to_datetime(campaigns_data['campaign_end_date']).to_numpy()
    camp_ids = campaigns_data['campaign_id'].to_numpy()

    valid_mask = (camp_starts[np.newaxis, :] <= eligible_starts[:, np.newaxis]) & (camp_ends[np.newaxis, :]   >= eligible_starts[:, np.newaxis])

    for i, idx in enumerate(eligible_idx):
        valid_camps = camp_ids[valid_mask[i]]
        if valid_camps.size > 0:
            campaign_ids_for_sessions[idx] = np.random.choice(valid_camps)

    linked_to_a_campaign_flag = pd.notnull(campaign_ids_for_sessions)
    prob_of_premium_sessions = np.random.rand(len(is_customer_session)) <= 0.3 
    prob_of_basic_sessions = np.random.rand(len(is_customer_session)) <= 0.35

    traffic_sources = np.full(num_of_sessions_y1 + num_of_sessions_y2 + num_of_sessions_y3, None, dtype=object)

    traffic_sources[linked_to_a_campaign_flag] = "Campaign"
    traffic_sources[~linked_to_a_campaign_flag & y1_sessions] = np.random.choice(TRAFFIC_SOURCES, p = TRAFFIC_WEIGHTS_Y1, size=(~linked_to_a_campaign_flag & y1_sessions).sum())
    traffic_sources[~linked_to_a_campaign_flag & y2_sessions] = np.random.choice(TRAFFIC_SOURCES, p = TRAFFIC_WEIGHTS_Y2, size=(~linked_to_a_campaign_flag & y2_sessions).sum())
    traffic_sources[~linked_to_a_campaign_flag & y3_sessions] = np.random.choice(TRAFFIC_SOURCES, p = TRAFFIC_WEIGHTS_Y3, size=(~linked_to_a_campaign_flag & y3_sessions).sum())

    eligible_premium_sessions = np.where(is_customer_session & purchased_flag & ~linked_to_a_campaign_flag & prob_of_premium_sessions)[0]
    premium_starts = session_start_times[eligible_premium_sessions].to_numpy()

    premium_startup_dates = premium_customers['signup_date'].to_numpy()
    premium_ids = premium_customers['customer_id'].to_numpy()
    
    sorted_premium_idx = np.argsort(premium_startup_dates)
    sorted_premium_dates = premium_startup_dates[sorted_premium_idx]
    sorted_premium_ids = premium_ids[sorted_premium_idx]

    for i, idx in enumerate(eligible_premium_sessions):
        cutoff = np.searchsorted(sorted_premium_dates, premium_starts[i], side='right')
        valid_ids = sorted_premium_ids[:cutoff]
        if valid_ids.size > 0:
            customer_ids[idx] = np.random.choice(valid_ids)
            aov[idx] = 'High'

    eligible_mid_level_sessions = np.where(is_customer_session & purchased_flag & ~linked_to_a_campaign_flag & ~prob_of_premium_sessions)[0]

    mid_starts = session_start_times[eligible_mid_level_sessions].to_numpy()

    mid_startup_dates = mid_level_customers['signup_date'].to_numpy()
    mid_ids = mid_level_customers['customer_id'].to_numpy()

    sorted_mid_idx = np.argsort(mid_startup_dates)
    sorted_mid_dates = mid_startup_dates[sorted_mid_idx]
    sorted_mid_ids = mid_ids[sorted_mid_idx]

    for i, idx in enumerate(eligible_mid_level_sessions):
        cutoff = np.searchsorted(sorted_mid_dates, mid_starts[i], side='right')
        valid_ids = sorted_mid_ids[:cutoff]
        if valid_ids.size > 0:
            customer_ids[idx] = np.random.choice(valid_ids)
            aov[idx] = np.random.choice(['Low','Mid'], p = [0.4,0.6])

    eligible_basic_level_sessions = np.where(is_customer_session & purchased_flag & linked_to_a_campaign_flag & prob_of_basic_sessions)[0]

    basic_starts = session_start_times[eligible_basic_level_sessions].to_numpy()

    basic_startup_dates = basic_level_customers['signup_date'].to_numpy()
    basic_ids = basic_level_customers['customer_id'].to_numpy()
    sorted_basic_idx = np.argsort(basic_startup_dates)
    sorted_basic_dates = basic_startup_dates[sorted_basic_idx]
    sorted_basic_ids = basic_ids[sorted_basic_idx]

    for i, idx in enumerate(eligible_basic_level_sessions):
        cutoff = np.searchsorted(sorted_basic_dates, basic_starts[i], side='right')
        valid_ids = sorted_basic_ids[:cutoff]
        if valid_ids.size > 0:
            customer_ids[idx] = np.random.choice(valid_ids)
            aov[idx] = 'Low'
    
    eligible_customer_sessions = np.where(np.logical_and(is_customer_session, pd.isnull(customer_ids)))[0]
    customer_starts = session_start_times[eligible_customer_sessions].to_numpy()

    customer_signup_dates = all_customers['signup_date'].to_numpy()
    customer_ids_array = all_customers['customer_id'].to_numpy()

    sorted_idx = np.argsort(customer_signup_dates)
    sorted_dates = customer_signup_dates[sorted_idx]
    sorted_ids = customer_ids_array[sorted_idx]

    for i, idx in enumerate(eligible_customer_sessions):
        start_time = customer_starts[i]

    # all customers with signup <= start_time
        cutoff = np.searchsorted(sorted_dates, start_time, side='right')
        valid_ids = sorted_ids[:cutoff]

        if valid_ids.size > 0:
            customer_ids[idx] = np.random.choice(valid_ids)
            aov[idx] = np.random.choice(['Low', 'Mid', 'High'], p=[0.5, 0.3, 0.2])
    

    remaining_transactions = pd.isna(aov)
    aov[remaining_transactions] = np.random.choice(['Low', 'Mid', 'High'], p=[0.5, 0.3, 0.2], size=remaining_transactions.sum())

    end_dates = pd.to_datetime(session_end_times)
    start_dates = pd.to_datetime(session_start_times)

    session_end_date_id = (
    end_dates.year * 10000 +
    end_dates.month * 100 +
    end_dates.day
    ).astype('int32')

    session_start_date_id = (
    start_dates.year * 10000 +
    start_dates.month * 100 +
    start_dates.day
    ).astype('int32')

    df_raw = pd.DataFrame({
        'session_id': session_ids,
        'customer_id': customer_ids,
        'session_start_time': session_start_times,
        'session_start_date_id': session_start_date_id,
        'session_end_time': session_end_times,
        'session_end_date_id': session_end_date_id,
        'device_type': device_types,
        'number_of_pages_viewed': number_of_pages_viewed,
        'product_page_visited_flag': product_page_visited_flag,
        'added_to_cart_flag': added_to_cart_flag,
        'purchased_flag': purchased_flag,
        'traffic_source': traffic_sources,
        'linked_to_a_campaign_flag': linked_to_a_campaign_flag,
        'campaign_id': campaign_ids_for_sessions,
        'aov_category': aov
        })
        
    conn.execute(CLICKSTREAMS_DDL_PATH.read_text())

    CHUNK_SIZE = 500_000

    for i in range(0, len(df_raw), CHUNK_SIZE):
        chunk = df_raw.iloc[i : i + CHUNK_SIZE]
        conn.register("chunk", chunk)  
        conn.execute("INSERT INTO fact_clickstream SELECT * FROM chunk")
        print(f"  Inserted rows {i:,} – {min(i + CHUNK_SIZE, len(df_raw)):,}")
        del chunk
    
    conn.execute(f'''COPY FACT_CLICKSTREAM TO '{CLICKSTREAMS_PARQUET_PATH}' (FORMAT PARQUET)''')
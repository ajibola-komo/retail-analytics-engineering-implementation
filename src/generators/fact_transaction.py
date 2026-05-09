import numpy as np
import pandas as pd
from src.config.paths import (TRANSACTIONS_DDL_PATH, TRANSACTIONS_PARQUET_PATH)
from src.config.constants import (BASE_TRANSACTION_END_TIMESTAMP_Y1, 
                                  BASE_TRANSACTION_END_TIMESTAMP_Y2, 
                                  BASE_TRANSACTION_END_TIMESTAMP_Y3,
                                  PAYMENT_TYPES,TRANSACTION_STATUSES, 
                                  PAYMENT_TYPES_WEIGHTS, TRANSACTION_WEIGHTS_Y1, TRANSACTION_WEIGHTS_Y2, TRANSACTION_WEIGHTS_Y3)

from src.generators.segment_customers import generate_customer_segments
from src.generators.segment_stores import segment_stores

def generate_transactions(conn):
    create_db = TRANSACTIONS_DDL_PATH.read_text()

    conn.execute(create_db)

    conn.execute(f"DELETE FROM FACT_TRANSACTION")


# retrieve the base transaction data from sales, sessions, customers, promotions, campaigns
    sales_data = conn.execute("""select transaction_id, session_id, transaction_timestamp, aov_category, sum(line_total) as transaction_subtotal, 
                              sum(line_cost) as transaction_cost,
                              count(product_id) as items_count
                              from fact_sale 
                              group by transaction_id, session_id, transaction_timestamp, aov_category""").df()

    transaction_ids = sales_data['transaction_id'].values
    total_transactions = len(transaction_ids)
    transaction_timestamps = sales_data['transaction_timestamp'].values
    transaction_date_ids = pd.to_datetime(transaction_timestamps).strftime('%Y%m%d').astype(np.int32)
    transaction_subtotals = sales_data['transaction_subtotal'].values
    transaction_costs = sales_data['transaction_cost'].values
    aov_categories = sales_data['aov_category'].values
    items_count_per_transaction = sales_data['items_count'].values
    session_ids = sales_data['session_id'].values

    sessions_data = conn.execute("""select session_id, customer_id, session_start_time, session_end_time, campaign_id,
    case when device_type = 'Mobile' then 'Mobile'
    when device_type = 'Tablet' then 'Web' 
    else 'Web' end as sales_channel from fact_clickstream where purchased_flag = TRUE""").df()
    session_id_customer_id_dict = dict(zip(sessions_data['session_id'].values, sessions_data['customer_id'].values))
    session_id_campaign_id_dict = dict(zip(sessions_data['session_id'].values, sessions_data['campaign_id'].values))
    session_id_sales_channel_dict = dict(zip(sessions_data['session_id'].values, sessions_data['sales_channel'].values))

    is_online_transaction = ~pd.isna(session_ids)
    is_in_store_transaction = pd.isna(session_ids)

    customer_ids = np.full(total_transactions, None, dtype=object)
    customer_ids[is_online_transaction] = [session_id_customer_id_dict.get(sid, None)for sid in session_ids[is_online_transaction]]
    campaign_ids = np.full(total_transactions, None, dtype=object)
    campaign_ids[is_online_transaction] = [session_id_campaign_id_dict.get(sid, None) for sid in session_ids[is_online_transaction]]
    sales_channels = np.full(total_transactions, None, dtype=object)
    sales_channels[is_online_transaction] = [session_id_sales_channel_dict.get(sid, None) for sid in session_ids[is_online_transaction]]
    sales_channels[is_in_store_transaction] = 'Store'

    payment_types = np.random.choice(PAYMENT_TYPES, size=len(transaction_ids), p=PAYMENT_TYPES_WEIGHTS)

    transaction_statuses = np.empty(total_transactions, dtype=object)
    y1_mask = pd.to_datetime(transaction_timestamps) <= pd.Timestamp(BASE_TRANSACTION_END_TIMESTAMP_Y1)
    y2_mask = (pd.to_datetime(transaction_timestamps) > pd.Timestamp(BASE_TRANSACTION_END_TIMESTAMP_Y1)) & \
          (pd.to_datetime(transaction_timestamps) <= pd.Timestamp(BASE_TRANSACTION_END_TIMESTAMP_Y2))
    y3_mask = pd.to_datetime(transaction_timestamps) > pd.Timestamp(BASE_TRANSACTION_END_TIMESTAMP_Y2)
    transaction_statuses[y1_mask] = np.random.choice(TRANSACTION_STATUSES, size=np.sum(y1_mask), p=TRANSACTION_WEIGHTS_Y1)
    transaction_statuses[y2_mask] = np.random.choice(TRANSACTION_STATUSES, size=np.sum(y2_mask), p=TRANSACTION_WEIGHTS_Y2)
    transaction_statuses[y3_mask] = np.random.choice(TRANSACTION_STATUSES, size=np.sum(y3_mask), p=TRANSACTION_WEIGHTS_Y3)

    customer_segments = generate_customer_segments(conn)

    all_customers = customer_segments["all_customers"]
    premium_customers = customer_segments["premium"]
    mid_level_customers = customer_segments["mid"]
    basic_level_customers = customer_segments["basic"]

    all_customer_ids = all_customers['customer_id'].values
    all_customer_sign_up_dates = all_customers['signup_date'].values
    cust_location_dict = dict(zip(all_customers['customer_id'], all_customers['location_id']))
    
    premium_customers_ids = premium_customers['customer_id'].values
    premium_customer_sign_up_dates = premium_customers['signup_date'].values
    mid_level_customers_ids = mid_level_customers['customer_id'].values
    mid_level_customer_sign_up_dates = mid_level_customers['signup_date'].values
    basic_level_customers_ids = basic_level_customers['customer_id'].values
    basic_level_customer_sign_up_dates = basic_level_customers['signup_date'].values

    premium_customers["activity_weight"] = np.random.pareto(2, len(premium_customers)) + 1

    mid_level_customers["activity_weight"] = np.random.pareto(3, len(mid_level_customers)) + 1

    basic_level_customers["activity_weight"] = np.random.pareto(4, len(basic_level_customers)) + 1

    in_store_indices = np.where(is_in_store_transaction)[0]

    locations_data = conn.execute("select location_id from dim_location").df()
    all_location_ids = locations_data['location_id']

    promotions_data = conn.execute('select promo_id, discount_type, discount_value from dim_promotion').df()
    all_promo_ids = promotions_data['promo_id']
    all_discount_types = promotions_data['discount_type']
    all_discount_values = promotions_data['discount_value']
    promo_disc_type = dict(zip(all_promo_ids, all_discount_types))
    promo_disc_value = dict(zip(all_promo_ids, all_discount_values))

    campaigns_data = conn.execute('select campaign_id, promo_id from dim_campaign').df()
    all_campaigns_id = campaigns_data['campaign_id'].values
    campaign_promo_ids = campaigns_data['promo_id'].values
    camp_promo_dict = dict(zip(all_campaigns_id,campaign_promo_ids))

    stores_data = segment_stores(conn)
    warehouse_store_map = stores_data['warehouse_store_map']
    physical_store_map = stores_data['physical_store_map']

    online_stores = conn.execute("select store_id from dim_store where store_type = 'Warehouse'").df()

    promo_ids = np.full(total_transactions, None, dtype=object)
    promo_ids[is_online_transaction] = [camp_promo_dict.get(cid, None) for cid in campaign_ids[is_online_transaction]]

    discount_types = np.full(total_transactions, None, dtype=object)
    discount_types[is_online_transaction] = [promo_disc_type.get(pid, None) for pid in promo_ids[is_online_transaction]]
    discount_values = np.full(total_transactions, 0.0, dtype=float)
    discount_values[is_online_transaction] = [promo_disc_value.get(pid, 0.0) for pid in promo_ids[is_online_transaction]]

    transaction_discount_applied = np.full(total_transactions, 0.0, dtype=float)

    is_percentage_discount = discount_types == 'Percentage_Discount'
    transaction_discount_applied[is_percentage_discount] = transaction_subtotals[is_percentage_discount] * discount_values[is_percentage_discount] / 100

    is_fixed_amount_discount = discount_types == 'Fixed_Amount_Discount'
    transaction_discount_applied[is_fixed_amount_discount] = discount_values[is_fixed_amount_discount]

    ineligible_for_discount_mask = transaction_subtotals < 50
    transaction_discount_applied[ineligible_for_discount_mask] = 0.0
    promo_ids[ineligible_for_discount_mask] = None

    transaction_totals = transaction_subtotals - transaction_discount_applied

    eligible_in_store_transactions = np.where(is_in_store_transaction)[0]

    for i,idx in enumerate(eligible_in_store_transactions):
        #subset_dates_map = {
            #'High': premium_subset_signup_dates,
            #'Mid': mid_subset_signup_dates,
            #'Low': basic_subset_signup_dates
        #}

        #subset_ids_map = {
            #'High': premium_subset_ids,
            #'Mid': mid_subset_ids,
            #'Low': basic_subset_ids
        #}

        category = aov_categories[idx]
        #if repeated_session[i]:
            #dates = subset_dates_map.get(category, all_customer_sign_up_dates)
            #ids = subset_ids_map.get(category, all_customer_ids)
        #else:
        dates = {
                'High': premium_customer_sign_up_dates,
                'Mid': mid_level_customer_sign_up_dates,
                'Low': basic_level_customer_sign_up_dates
                }.get(category, all_customer_sign_up_dates)
        ids = {
                    'High': premium_customers_ids,
                    'Mid': mid_level_customers_ids,
                    'Low': basic_level_customers_ids
                }.get(category, all_customer_ids)


        txn_time_np = np.datetime64(transaction_timestamps[idx])
        eligible_mask = dates <= txn_time_np
        eligible_customers = ids[eligible_mask]

        if len(eligible_customers) == 0:
            eligible_mask = all_customer_sign_up_dates <= txn_time_np
            eligible_customers = all_customer_ids[eligible_mask]
            if len(eligible_customers) == 0:  
                continue 

        customer_ids[idx] = np.random.choice(eligible_customers)
    
    guest_transaction_mask = pd.isna(customer_ids)

    location_ids = np.full(total_transactions, None, dtype=object)

    location_ids[~guest_transaction_mask] = [cust_location_dict.get(cid, None) for cid in customer_ids[~guest_transaction_mask]]

    location_ids[guest_transaction_mask] = np.random.choice(all_location_ids, size=np.sum(guest_transaction_mask))

    store_ids = np.full(total_transactions, None, dtype=object)
    store_ids[is_online_transaction] = [np.random.choice(warehouse_store_map.get(loc_id, [None])) for loc_id in location_ids[is_online_transaction]]
    store_ids[is_in_store_transaction] = [np.random.choice(physical_store_map.get(loc_id, [None])) for loc_id in location_ids[is_in_store_transaction]]
    unassigned_store_ids = pd.isna(store_ids)
    store_ids[unassigned_store_ids] = [np.random.choice(online_stores['store_id'].values) for _ in range(np.sum(unassigned_store_ids))]

    df_raw = pd.DataFrame({
            'transaction_id': transaction_ids,
            'transaction_timestamp': transaction_timestamps,
            'transaction_date_id': transaction_date_ids,
            'customer_id': customer_ids,
            'store_id': store_ids,
            'sales_channel': sales_channels,
            'session_id': session_ids,
            'promo_id': promo_ids,
            'campaign_id': campaign_ids,
            'transaction_subtotal': transaction_subtotals.astype(float),
            'transaction_discount_applied': transaction_discount_applied.astype(float),
            'transaction_total': transaction_totals.astype(float),
            'transaction_cost': transaction_costs.astype(float),
            'items_count': items_count_per_transaction,
            'payment_type': payment_types,
            'transaction_status': transaction_statuses
        })

    conn.register("df_raw", df_raw)

    conn.execute("INSERT INTO FACT_TRANSACTION SELECT * FROM DF_RAW")

    conn.execute(f'''COPY FACT_TRANSACTION TO '{TRANSACTIONS_PARQUET_PATH}' (FORMAT PARQUET)''')
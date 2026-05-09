import numpy as np
import pandas as pd
from src.config.constants import (SALES_START_ID, TRANSACTION_START_ID, PRODUCT_RANGES, PRODUCT_WEIGHTS)
from src.config.paths import (SALES_DDL_PATH, SALES_PARQUET_PATH)
from src.generators.month_distribution import generate_in_store_month_distribution

def generate_sales(conn,num_of_transactions):

    create_db = SALES_DDL_PATH.read_text()

    conn.execute(create_db)

    conn.execute(f"DELETE FROM FACT_SALE")

    products = conn.execute("select product_id, unit_cost, unit_price, product_segment from dim_product").df()
    all_product_ids = products['product_id'].values
    all_unit_costs = products['unit_cost'].values
    all_unit_prices = products['unit_price'].values

    sessions = conn.execute("select session_id, session_end_time, aov_category from fact_clickstream where purchased_flag = TRUE").df()
    low_aov_sessions = sessions[sessions['aov_category'] == 'Low']
    mid_aov_sessions = sessions[sessions['aov_category'] == 'Mid']
    high_aov_sessions = sessions[sessions['aov_category'] == 'High']

    entry_level_products_ids = all_product_ids[products['product_segment'] == 'Entry Level']
    low_cost_products_ids = all_product_ids[products['product_segment'] == 'Low']
    high_end_products_ids = all_product_ids[products['product_segment'] == 'High End']
    flagship_products_ids = all_product_ids[products['product_segment'] == 'Flagship']
    mid_tier_products_ids = all_product_ids[products['product_segment'] == 'Mid Tier']
    
    transaction_ids = np.arange(TRANSACTION_START_ID, TRANSACTION_START_ID + num_of_transactions)
    n_low_sessions = len(low_aov_sessions)
    n_mid_sessions = len(mid_aov_sessions)
    n_high_sessions = len(high_aov_sessions)
    n_sessions = n_low_sessions + n_mid_sessions + n_high_sessions
    remaining_transactions = max(0, num_of_transactions - n_sessions)
    transaction_timestamps = np.empty(num_of_transactions, dtype='datetime64[ns]')
    transaction_timestamps[:n_low_sessions] = low_aov_sessions['session_end_time'].values
    transaction_timestamps[n_low_sessions:n_low_sessions + n_mid_sessions] = mid_aov_sessions['session_end_time'].values
    transaction_timestamps[n_low_sessions + n_mid_sessions:n_low_sessions + n_mid_sessions + n_high_sessions] = high_aov_sessions['session_end_time'].values
    if remaining_transactions > 0:
        in_store_dist = generate_in_store_month_distribution(remaining_transactions)
        in_store_timestamps = np.concatenate([
        in_store_dist["y1"].to_numpy(),
        in_store_dist["y2"].to_numpy()
         ])
        transaction_timestamps[n_sessions:] = in_store_timestamps
    items_count_list = np.random.randint(1,4, size=num_of_transactions)
    total_items = items_count_list.sum()
    sale_transaction_ids = np.repeat(transaction_ids, items_count_list)
    sale_transaction_timestamps = np.repeat(transaction_timestamps, items_count_list)
    transaction_session_ids = pd.Series([None] * num_of_transactions, dtype="Int64")
    transaction_session_ids[:n_low_sessions] = low_aov_sessions['session_id'].values
    transaction_session_ids[n_low_sessions:n_low_sessions + n_mid_sessions] = mid_aov_sessions['session_id'].values
    transaction_session_ids[n_low_sessions + n_mid_sessions:n_low_sessions + n_mid_sessions + n_high_sessions] = high_aov_sessions['session_id'].values
    sale_ids = np.arange(SALES_START_ID, SALES_START_ID + total_items)
    sale_session_ids = np.repeat(transaction_session_ids.to_numpy(), items_count_list)

    product_ids = np.empty(total_items, dtype=np.int32)
    
    primary_range = np.empty(num_of_transactions, dtype=object)
    primary_range[:n_low_sessions] = low_aov_sessions['aov_category'].values
    primary_range[n_low_sessions:n_low_sessions + n_mid_sessions] = mid_aov_sessions['aov_category'].values
    primary_range[n_low_sessions + n_mid_sessions:n_low_sessions + n_mid_sessions + n_high_sessions] = high_aov_sessions['aov_category'].values
    in_store_mask = pd.isna(transaction_session_ids)
    primary_range[in_store_mask] = np.random.choice(PRODUCT_RANGES, p = PRODUCT_WEIGHTS, size=np.sum(in_store_mask))

    line_idx = 0
    for t, (tier, n_items) in enumerate(zip(primary_range, items_count_list)):
        if tier == 'High':
            product_ids[line_idx] = np.random.choice(
            high_end_products_ids if np.random.rand() < 0.6 else flagship_products_ids
            )
        elif tier == 'Mid':
            product_ids[line_idx] = np.random.choice(mid_tier_products_ids)
        elif tier == 'Low':
            product_ids[line_idx] = np.random.choice(
            low_cost_products_ids if np.random.rand() < 0.6 else entry_level_products_ids
        )

    # Additional items
        for i in range(1, n_items):
            if tier == 'High':
                product_ids[line_idx + i] = np.random.choice(
                mid_tier_products_ids if np.random.rand() < 0.5 else low_cost_products_ids
            )
            elif tier == 'Mid':
                product_ids[line_idx + i] = np.random.choice(
                mid_tier_products_ids if np.random.rand() < 0.7 else low_cost_products_ids
            )
            else:
                product_ids[line_idx + i] = np.random.choice(low_cost_products_ids if np.random.rand() < 0.6 else entry_level_products_ids)
        line_idx += n_items

    product_cost_map = dict(zip(all_product_ids, all_unit_costs))
    product_price_map = dict(zip(all_product_ids, all_unit_prices))

    unit_costs = np.vectorize(product_cost_map.get)(product_ids)
    unit_prices = np.vectorize(product_price_map.get)(product_ids)

    quantities = np.ones(total_items, dtype = int)

    line_costs = unit_costs * quantities
    line_totals = unit_prices * quantities

    aov_category = np.repeat(primary_range, items_count_list)

    df_raw = pd.DataFrame({
        "sale_id":sale_ids,
        "transaction_id":sale_transaction_ids,
        "session_id":sale_session_ids,
        "transaction_timestamp":sale_transaction_timestamps,
        "transaction_date_id":pd.to_datetime(sale_transaction_timestamps).strftime('%Y%m%d').astype(int),
        "product_id":product_ids,
        "quantity":quantities,
        "unit_cost":unit_costs,
        "unit_price":unit_prices,
        "line_cost":line_costs,
        "line_total":line_totals,
        "aov_category":aov_category
    })

    conn.register("df_raw", df_raw)

    conn.execute('INSERT INTO FACT_SALE SELECT * FROM DF_RAW')

    conn.execute(f'''
                    COPY FACT_SALE TO '{SALES_PARQUET_PATH}' (FORMAT PARQUET)
''')
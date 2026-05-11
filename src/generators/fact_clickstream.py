import numpy as np
import pandas as pd
from src.generators.month_distribution import generate_online_month_distribution
from src.generators.segment_customers import generate_customer_segments
from src.config.paths import (CLICKSTREAMS_DDL_PATH, CLICKSTREAMS_PARQUET_PATH)
from src.config.constants import (SESSION_START_ID, TRAFFIC_SOURCES, TRAFFIC_WEIGHTS_Y1, TRAFFIC_WEIGHTS_Y2, TRAFFIC_WEIGHTS_Y3,
                                  DEVICE_TYPES, DEVICE_WEIGHTS_Y1, DEVICE_WEIGHTS_Y2, DEVICE_WEIGHTS_Y3, CAMPAIGN_SESSION_MINUTES, CAMPAIGN_SESSION_WEIGHTS_Y1, CAMPAIGN_SESSION_WEIGHTS_Y2, CAMPAIGN_SESSION_WEIGHTS_Y3,
                                  PAID_SEARCH_SESSION_MINUTES, PAID_SEARCH_SESSION_WEIGHTS_Y1, PAID_SEARCH_SESSION_WEIGHTS_Y2, PAID_SEARCH_SESSION_WEIGHTS_Y3,
                                  ORGANIC_SESSION_MINUTES, ORGANIC_SESSION_WEIGHTS_Y1, ORGANIC_SESSION_WEIGHTS_Y2, ORGANIC_SESSION_WEIGHTS_Y3,
                                  DIRECT_SESSION_MINUTES, DIRECT_SESSION_WEIGHTS_Y1, DIRECT_SESSION_WEIGHTS_Y2, DIRECT_SESSION_WEIGHTS_Y3,
                                  REFERRAL_SESSION_MINUTES, REFERRAL_SESSION_WEIGHTS_Y1, REFERRAL_SESSION_WEIGHTS_Y2, REFERRAL_SESSION_WEIGHTS_Y3,
                                  PROB_OF_CAMPAIGN_LINKED_Y1, PROB_OF_CAMPAIGN_LINKED_Y2, PROB_OF_CUSTOMER_SESSION_Y1, PROB_OF_CUSTOMER_SESSION_Y2,
                                  BASE_TRANSACTION_TIME_STAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y1, BASE_TRANSACTION_END_TIMESTAMP_Y2,
                                  BASE_TRANSACTION_TIME_STAMP_Y2, BASE_TRANSACTION_END_TIMESTAMP_Y3, BASE_TRANSACTION_TIME_STAMP_Y3, PROB_OF_CAMPAIGN_LINKED_Y3, 
                                  PROB_OF_CUSTOMER_SESSION_Y3, PROB_INTENT_CAMPAIGN_Y1, PROB_INTENT_CAMPAIGN_Y2, PROB_INTENT_CAMPAIGN_Y3,
                                  PROB_INTENT_DIRECT_Y1, PROB_INTENT_DIRECT_Y2, PROB_INTENT_DIRECT_Y3, PROB_INTENT_ORGANIC_Y1, PROB_INTENT_ORGANIC_Y2, 
                                  PROB_INTENT_ORGANIC_Y3, PROB_INTENT_PAID_SEARCH_Y1, PROB_INTENT_PAID_SEARCH_Y2, PROB_INTENT_PAID_SEARCH_Y3, 
                                  PROB_INTENT_REFERRAL_Y1, PROB_INTENT_REFERRAL_Y2, PROB_INTENT_REFERRAL_Y3, PROB_PURCHASE_CAMPAIGN_Y1, PROB_PURCHASE_CAMPAIGN_Y2, PROB_PURCHASE_CAMPAIGN_Y3, 
                                  PROB_PURCHASE_DIRECT_Y1, PROB_PURCHASE_DIRECT_Y2, PROB_PURCHASE_DIRECT_Y3, PROB_PURCHASE_ORGANIC_Y1, PROB_PURCHASE_ORGANIC_Y2, PROB_PURCHASE_ORGANIC_Y3, PROB_PURCHASE_PAID_SEARCH_Y1, PROB_PURCHASE_PAID_SEARCH_Y2, PROB_PURCHASE_PAID_SEARCH_Y3, PROB_PURCHASE_REFERRAL_Y1, PROB_PURCHASE_REFERRAL_Y2, PROB_PURCHASE_REFERRAL_Y3
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

    device_types = np.empty(total_sessions, dtype=object)

    y1_sessions = (session_start_times >= pd.to_datetime(BASE_TRANSACTION_TIME_STAMP_Y1)) & (session_start_times <= pd.to_datetime(BASE_TRANSACTION_END_TIMESTAMP_Y1))
    y2_sessions = (session_start_times >= pd.to_datetime(BASE_TRANSACTION_TIME_STAMP_Y2)) & (session_start_times <= pd.to_datetime(BASE_TRANSACTION_END_TIMESTAMP_Y2))
    y3_sessions = (session_start_times >= pd.to_datetime(BASE_TRANSACTION_TIME_STAMP_Y3)) & (session_start_times <= pd.to_datetime(BASE_TRANSACTION_END_TIMESTAMP_Y3))

    device_types[y1_sessions] = np.random.choice(DEVICE_TYPES, p = DEVICE_WEIGHTS_Y1, size=y1_sessions.sum())
    device_types[y2_sessions] = np.random.choice(DEVICE_TYPES, p = DEVICE_WEIGHTS_Y2, size=y2_sessions.sum())
    device_types[y3_sessions] = np.random.choice(DEVICE_TYPES, p = DEVICE_WEIGHTS_Y3, size=y3_sessions.sum())

    traffic_sources = np.full(num_of_sessions_y1 + num_of_sessions_y2 + num_of_sessions_y3, None, dtype=object)

    traffic_sources[y1_sessions] = np.random.choice(TRAFFIC_SOURCES, p = TRAFFIC_WEIGHTS_Y1, size=(y1_sessions).sum())
    traffic_sources[y2_sessions] = np.random.choice(TRAFFIC_SOURCES, p = TRAFFIC_WEIGHTS_Y2, size=(y2_sessions).sum())
    traffic_sources[y3_sessions] = np.random.choice(TRAFFIC_SOURCES, p = TRAFFIC_WEIGHTS_Y3, size=(y3_sessions).sum())


    mobile_sessions_y1 = (device_types == "Mobile") & y1_sessions
    mobile_sessions_y2 = (device_types == "Mobile") & y2_sessions
    mobile_sessions_y3 = (device_types == "Mobile") & y3_sessions
    tablet_sessions_y1 = (device_types == "Tablet") & y1_sessions
    tablet_sessions_y2 = (device_types == "Tablet") & y2_sessions
    tablet_sessions_y3 = (device_types == "Tablet") & y3_sessions
    desktop_sessions_y1 = (device_types == "Desktop") & y1_sessions
    desktop_sessions_y2 = (device_types == "Desktop") & y2_sessions
    desktop_sessions_y3 = (device_types == "Desktop") & y3_sessions

    durations = np.zeros(total_sessions, dtype=int)

    campaign_y1 = y1_sessions
    campaign_y2 = y2_sessions
    campaign_y3 = y3_sessions
    organic_y1 = (traffic_sources == "Organic") & y1_sessions
    organic_y2 = (traffic_sources == "Organic") & y2_sessions
    organic_y3 = (traffic_sources == "Organic") & y3_sessions
    paid_search_y1 = (traffic_sources == "Paid Search") & y1_sessions
    paid_search_y2 = (traffic_sources == "Paid Search") & y2_sessions
    paid_search_y3 = (traffic_sources == "Paid Search") & y3_sessions
    direct_y1 = (traffic_sources == "Direct") & y1_sessions
    direct_y2 = (traffic_sources == "Direct") & y2_sessions
    direct_y3 = (traffic_sources == "Direct") & y3_sessions
    referral_y1 = (traffic_sources == "Referral") & y1_sessions
    referral_y2 = (traffic_sources == "Referral") & y2_sessions
    referral_y3 = (traffic_sources == "Referral") & y3_sessions
    
    durations[campaign_y1] = np.random.choice(CAMPAIGN_SESSION_MINUTES, p = CAMPAIGN_SESSION_WEIGHTS_Y1, size= campaign_y1.sum())
    durations[campaign_y2] = np.random.choice(CAMPAIGN_SESSION_MINUTES, p = CAMPAIGN_SESSION_WEIGHTS_Y2, size= campaign_y2.sum())
    durations[campaign_y3] = np.random.choice(CAMPAIGN_SESSION_MINUTES, p = CAMPAIGN_SESSION_WEIGHTS_Y3, size= campaign_y3.sum())
    durations[organic_y1] = np.random.choice(ORGANIC_SESSION_MINUTES, p = ORGANIC_SESSION_WEIGHTS_Y1, size= organic_y1.sum())
    durations[organic_y2] = np.random.choice(ORGANIC_SESSION_MINUTES, p = ORGANIC_SESSION_WEIGHTS_Y2, size= organic_y2.sum())
    durations[organic_y3] = np.random.choice(ORGANIC_SESSION_MINUTES, p = ORGANIC_SESSION_WEIGHTS_Y3, size= organic_y3.sum())
    durations[paid_search_y1] = np.random.choice(PAID_SEARCH_SESSION_MINUTES, p = PAID_SEARCH_SESSION_WEIGHTS_Y1, size= paid_search_y1.sum())
    durations[paid_search_y2] = np.random.choice(PAID_SEARCH_SESSION_MINUTES, p = PAID_SEARCH_SESSION_WEIGHTS_Y2, size= paid_search_y2.sum())
    durations[paid_search_y3] = np.random.choice(PAID_SEARCH_SESSION_MINUTES, p = PAID_SEARCH_SESSION_WEIGHTS_Y3, size= paid_search_y3.sum())
    durations[direct_y1] = np.random.choice(DIRECT_SESSION_MINUTES, p = DIRECT_SESSION_WEIGHTS_Y1, size= direct_y1.sum())
    durations[direct_y2] = np.random.choice(DIRECT_SESSION_MINUTES, p = DIRECT_SESSION_WEIGHTS_Y2, size= direct_y2.sum())
    durations[direct_y3] = np.random.choice(DIRECT_SESSION_MINUTES, p = DIRECT_SESSION_WEIGHTS_Y3, size= direct_y3.sum())
    durations[referral_y1] = np.random.choice(REFERRAL_SESSION_MINUTES, p = REFERRAL_SESSION_WEIGHTS_Y1, size= referral_y1.sum())
    durations[referral_y2] = np.random.choice(REFERRAL_SESSION_MINUTES, p = REFERRAL_SESSION_WEIGHTS_Y2, size= referral_y2.sum())
    durations[referral_y3] = np.random.choice(REFERRAL_SESSION_MINUTES, p = REFERRAL_SESSION_WEIGHTS_Y3, size= referral_y3.sum())

    session_end_times = session_start_times + pd.to_timedelta(durations, unit="m")

    number_of_pages_viewed = np.zeros(total_sessions, dtype=int)

    mobile_y1_durations = durations[mobile_sessions_y1]
    mobile_y2_durations = durations[mobile_sessions_y2]
    mobile_y3_durations = durations[mobile_sessions_y3]
    tablet_y1_durations = durations[tablet_sessions_y1]
    tablet_y2_durations = durations[tablet_sessions_y2]
    tablet_y3_durations = durations[tablet_sessions_y3]
    desktop_y1_durations = durations[desktop_sessions_y1]
    desktop_y2_durations = durations[desktop_sessions_y2]
    desktop_y3_durations = durations[desktop_sessions_y3]

    number_of_pages_viewed[mobile_sessions_y1] = np.where(mobile_y1_durations <= 2, np.random.randint(1,4,size=mobile_sessions_y1.sum()),
                                    np.where((mobile_y1_durations > 2) & (mobile_y1_durations <= 5), np.random.randint(4,7, size = mobile_sessions_y1.sum()),
                                             np.random.randint(7,13, size= mobile_sessions_y1.sum())))
    

    number_of_pages_viewed[tablet_sessions_y1] = np.where(tablet_y1_durations <= 2, np.random.randint(1,5,size=tablet_sessions_y1.sum()),
                                    np.where((tablet_y1_durations > 2) & (tablet_y1_durations <= 5), np.random.randint(5,8, size = tablet_sessions_y1.sum()),
                                             np.random.randint(8,15, size= tablet_sessions_y1.sum())))
    
    number_of_pages_viewed[desktop_sessions_y1] = np.where(desktop_y1_durations <= 2, np.random.randint(1,6,size=desktop_sessions_y1.sum()),
                                    np.where((desktop_y1_durations > 2) & (desktop_y1_durations <= 5), np.random.randint(6,10, size = desktop_sessions_y1.sum()),
                                             np.random.randint(10,20, size= desktop_sessions_y1.sum())))
    
    number_of_pages_viewed[mobile_sessions_y2] = np.where(mobile_y2_durations <= 2, np.random.randint(1,4,size=mobile_sessions_y2.sum()),
                                    np.where((mobile_y2_durations > 2) & (mobile_y2_durations <= 5), np.random.randint(4,7, size = mobile_sessions_y2.sum()),
                                             np.random.randint(7,13, size= mobile_sessions_y2.sum())))
    
    number_of_pages_viewed[tablet_sessions_y2] = np.where(tablet_y2_durations <= 2, np.random.randint(1,5,size=tablet_sessions_y2.sum()),
                                    np.where((tablet_y2_durations > 2) & (tablet_y2_durations <= 5), np.random.randint(5,8, size = tablet_sessions_y2.sum()),
                                             np.random.randint(8,15, size= tablet_sessions_y2.sum())))
    
    number_of_pages_viewed[desktop_sessions_y2] = np.where(desktop_y2_durations <= 2, np.random.randint(1,6,size=desktop_sessions_y2.sum()),
                                    np.where((desktop_y2_durations > 2) & (desktop_y2_durations <= 5), np.random.randint(6,10, size = desktop_sessions_y2.sum()),
                                             np.random.randint(10,20, size= desktop_sessions_y2.sum())))
    
    number_of_pages_viewed[mobile_sessions_y3] = np.where(mobile_y3_durations <= 2, np.random.randint(1,4,size=mobile_sessions_y3.sum()),
                                    np.where((mobile_y3_durations > 2) & (mobile_y3_durations <= 5), np.random.randint(4,7, size = mobile_sessions_y3.sum()),
                                             np.random.randint(7,13, size= mobile_sessions_y3.sum())))
    
    number_of_pages_viewed[tablet_sessions_y3] = np.where(tablet_y3_durations <= 2, np.random.randint(1,5,size=tablet_sessions_y3.sum()),
                                    np.where((tablet_y3_durations > 2) & (tablet_y3_durations <= 5), np.random.randint(5,8, size = tablet_sessions_y3.sum()),
                                             np.random.randint(8,15, size= tablet_sessions_y3.sum())))
    
    number_of_pages_viewed[desktop_sessions_y3] = np.where(desktop_y3_durations <= 2, np.random.randint(1,6,size=desktop_sessions_y3.sum()),
                                    np.where((desktop_y3_durations > 2) & (desktop_y3_durations <= 5), np.random.randint(6,10, size = desktop_sessions_y3.sum()),
                                             np.random.randint(10,20, size= desktop_sessions_y3.sum())))  


    aov = np.full(total_sessions, None, dtype=object)

    product_page_visited_flag = number_of_pages_viewed >= 4
    
    added_to_cart_flag = np.zeros(total_sessions, dtype=bool)
    purchased_flag = np.zeros(total_sessions, dtype=bool)
    is_customer_session = np.zeros(total_sessions, dtype=bool)
    probability_of_campaign_linked = np.zeros(total_sessions, dtype=bool)


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
    traffic_sources[linked_to_a_campaign_flag] = "Campaign"

    
    prob_of_premium_sessions = np.random.rand(len(is_customer_session)) <= 0.3 
    prob_of_basic_sessions = np.random.rand(len(is_customer_session)) <= 0.35

    
    y1_product_sessions_campaign = y1_sessions & product_page_visited_flag & (traffic_sources == "Campaign")
    y2_product_sessions_campaign = y2_sessions & product_page_visited_flag & (traffic_sources == "Campaign")
    y3_product_sessions_campaign = y3_sessions & product_page_visited_flag & (traffic_sources == "Campaign")
    y1_product_sessions_direct = y1_sessions & product_page_visited_flag & (traffic_sources == "Direct")
    y2_product_sessions_direct = y2_sessions & product_page_visited_flag & (traffic_sources == "Direct")
    y3_product_sessions_direct = y3_sessions & product_page_visited_flag & (traffic_sources == "Direct")
    y1_product_sessions_organic = y1_sessions & product_page_visited_flag & (traffic_sources == "Organic")
    y2_product_sessions_organic = y2_sessions & product_page_visited_flag & (traffic_sources == "Organic")
    y3_product_sessions_organic = y3_sessions & product_page_visited_flag & (traffic_sources == "Organic")
    y1_product_sessions_paid_search = y1_sessions & product_page_visited_flag & (traffic_sources == "Paid Search")
    y2_product_sessions_paid_search = y2_sessions & product_page_visited_flag & (traffic_sources == "Paid Search")
    y3_product_sessions_paid_search = y3_sessions & product_page_visited_flag & (traffic_sources == "Paid Search")
    y1_product_sessions_referral = y1_sessions & product_page_visited_flag & (traffic_sources == "Referral")
    y2_product_sessions_referral = y2_sessions & product_page_visited_flag & (traffic_sources == "Referral")
    y3_product_sessions_referral = y3_sessions & product_page_visited_flag & (traffic_sources == "Referral")

    


    added_to_cart_flag[y1_product_sessions_campaign] = (
    np.random.rand(y1_product_sessions_campaign
                   .sum())
    <= PROB_INTENT_CAMPAIGN_Y1
    )

    added_to_cart_flag[y2_product_sessions_campaign] = (
    np.random.rand(y2_product_sessions_campaign
                   .sum())
    <= PROB_INTENT_CAMPAIGN_Y2
    )

    added_to_cart_flag[y3_product_sessions_campaign] = (
    np.random.rand(y3_product_sessions_campaign
                   .sum())
    <= PROB_INTENT_CAMPAIGN_Y3
    )

    added_to_cart_flag[y1_product_sessions_direct] = (
    np.random.rand(y1_product_sessions_direct
                   .sum())
    <= PROB_INTENT_DIRECT_Y1
    )

    added_to_cart_flag[y2_product_sessions_direct] = (
    np.random.rand(y2_product_sessions_direct
                   .sum())
    <= PROB_INTENT_DIRECT_Y2
    )

    added_to_cart_flag[y3_product_sessions_direct] = (
    np.random.rand(y3_product_sessions_direct
                   .sum())
    <= PROB_INTENT_DIRECT_Y3
    )

    added_to_cart_flag[y1_product_sessions_organic] = (
    np.random.rand(y1_product_sessions_organic
                   .sum())
    <= PROB_INTENT_ORGANIC_Y1
    )

    added_to_cart_flag[y2_product_sessions_organic] = (
    np.random.rand(y2_product_sessions_organic
                   .sum())
    <= PROB_INTENT_ORGANIC_Y2
    )

    added_to_cart_flag[y3_product_sessions_organic] = (
    np.random.rand(y3_product_sessions_organic
                   .sum())
    <= PROB_INTENT_ORGANIC_Y3
    )

    added_to_cart_flag[y1_product_sessions_paid_search] = (
    np.random.rand(y1_product_sessions_paid_search
                   .sum())
    <= PROB_INTENT_PAID_SEARCH_Y1
    )

    added_to_cart_flag[y2_product_sessions_paid_search] = (
    np.random.rand(y2_product_sessions_paid_search
                   .sum())
    <= PROB_INTENT_PAID_SEARCH_Y2
    )

    added_to_cart_flag[y3_product_sessions_paid_search] = (
    np.random.rand(y3_product_sessions_paid_search
                   .sum())
    <= PROB_INTENT_PAID_SEARCH_Y3
    )

    added_to_cart_flag[y1_product_sessions_referral] = (
    np.random.rand(y1_product_sessions_referral
                   .sum())
    <= PROB_INTENT_REFERRAL_Y1
    )

    added_to_cart_flag[y2_product_sessions_referral] = (
    np.random.rand(y2_product_sessions_referral
                   .sum())
    <= PROB_INTENT_REFERRAL_Y2
    )

    added_to_cart_flag[y3_product_sessions_referral] = (
    np.random.rand(y3_product_sessions_referral
                   .sum())
    <= PROB_INTENT_REFERRAL_Y3
    )


    #purchase conversion
    y1_purchase_sessions_campaign = y1_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Campaign")
    y2_purchase_sessions_campaign = y2_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Campaign")
    y3_purchase_sessions_campaign = y3_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Campaign")
    y1_purchase_sessions_direct = y1_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Direct")
    y2_purchase_sessions_direct = y2_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Direct")
    y3_purchase_sessions_direct = y3_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Direct")
    y1_purchase_sessions_organic = y1_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Organic")
    y2_purchase_sessions_organic = y2_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Organic")
    y3_purchase_sessions_organic = y3_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Organic")
    y1_purchase_sessions_paid_search = y1_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Paid Search")
    y2_purchase_sessions_paid_search = y2_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Paid Search")
    y3_purchase_sessions_paid_search = y3_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Paid Search")
    y1_purchase_sessions_referral = y1_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Referral")
    y2_purchase_sessions_referral = y2_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Referral")
    y3_purchase_sessions_referral = y3_sessions & product_page_visited_flag & added_to_cart_flag & (traffic_sources == "Referral")

    purchased_flag[y1_purchase_sessions_campaign] = (
    np.random.rand(y1_purchase_sessions_campaign
                   .sum())
    <= PROB_PURCHASE_CAMPAIGN_Y1
    )
    
    purchased_flag[y2_purchase_sessions_campaign] = (
    np.random.rand(y2_purchase_sessions_campaign
                   .sum())
    <= PROB_PURCHASE_CAMPAIGN_Y2
    )

    purchased_flag[y3_purchase_sessions_campaign] = (
    np.random.rand(y3_purchase_sessions_campaign
                   .sum())
    <= PROB_PURCHASE_CAMPAIGN_Y3
    )

    purchased_flag[y1_purchase_sessions_direct] = (
    np.random.rand(y1_purchase_sessions_direct
                   .sum())
    <= PROB_PURCHASE_DIRECT_Y1
    )

    purchased_flag[y2_purchase_sessions_direct] = (
    np.random.rand(y2_purchase_sessions_direct
                   .sum())
    <= PROB_PURCHASE_DIRECT_Y2
    )

    purchased_flag[y3_purchase_sessions_direct] = (
    np.random.rand(y3_purchase_sessions_direct
                   .sum())
    <= PROB_PURCHASE_DIRECT_Y3
    )

    purchased_flag[y1_purchase_sessions_organic] = (
    np.random.rand(y1_purchase_sessions_organic
                   .sum())
    <= PROB_PURCHASE_ORGANIC_Y1
    )

    purchased_flag[y2_purchase_sessions_organic] = (
    np.random.rand(y2_purchase_sessions_organic
                   .sum())
    <= PROB_PURCHASE_ORGANIC_Y2
    )

    purchased_flag[y3_purchase_sessions_organic] = (
    np.random.rand(y3_purchase_sessions_organic
                   .sum())
    <= PROB_PURCHASE_ORGANIC_Y3
    )

    purchased_flag[y1_purchase_sessions_paid_search] = (
    np.random.rand(y1_purchase_sessions_paid_search
                   .sum())
    <= PROB_PURCHASE_PAID_SEARCH_Y1
    )

    purchased_flag[y2_purchase_sessions_paid_search] = (
    np.random.rand(y2_purchase_sessions_paid_search
                   .sum())
    <= PROB_PURCHASE_PAID_SEARCH_Y2
    )

    purchased_flag[y3_purchase_sessions_paid_search] = (
    np.random.rand(y3_purchase_sessions_paid_search
                   .sum())
    <= PROB_PURCHASE_PAID_SEARCH_Y3
    )

    purchased_flag[y1_purchase_sessions_referral] = (
    np.random.rand(y1_purchase_sessions_referral
                   .sum())
    <= PROB_PURCHASE_REFERRAL_Y1
    )

    purchased_flag[y2_purchase_sessions_referral] = (
    np.random.rand(y2_purchase_sessions_referral
                   .sum())
    <= PROB_PURCHASE_REFERRAL_Y2
    )

    purchased_flag[y3_purchase_sessions_referral] = (
    np.random.rand(y3_purchase_sessions_referral
                   .sum())
    <= PROB_PURCHASE_REFERRAL_Y3
    )

    is_customer_session[y1_sessions] = np.random.rand(y1_sessions.sum()) <= PROB_OF_CUSTOMER_SESSION_Y1
    is_customer_session[y2_sessions] = np.random.rand(y2_sessions.sum()) <= PROB_OF_CUSTOMER_SESSION_Y2
    is_customer_session[y3_sessions] = np.random.rand(y3_sessions.sum()) <= PROB_OF_CUSTOMER_SESSION_Y3
    customer_ids = np.full(num_of_sessions_y1 + num_of_sessions_y2 + num_of_sessions_y3, None, dtype=object)

    eligible_premium_sessions = np.where(is_customer_session & purchased_flag & ~linked_to_a_campaign_flag & prob_of_premium_sessions)[0]
    premium_starts = session_start_times[eligible_premium_sessions].to_numpy()

    premium_startup_dates = premium_customers['signup_date'].to_numpy()
    premium_ids = premium_customers['customer_id'].to_numpy()
    
    sorted_premium_idx = np.argsort(premium_startup_dates)
    sorted_premium_dates = premium_startup_dates[sorted_premium_idx]
    sorted_premium_ids = premium_ids[sorted_premium_idx]

    premium_positions = np.arange(1, len(sorted_premium_ids) + 1, dtype=float)

    for i, idx in enumerate(eligible_premium_sessions):
        cutoff = np.searchsorted(sorted_premium_dates, premium_starts[i], side='right')
        valid_ids = sorted_premium_ids[:cutoff]
        if valid_ids.size > 0:
            w = premium_positions[:cutoff]
            w = w / w.sum()
            customer_ids[idx] = np.random.choice(valid_ids, p=w)

    eligible_mid_level_sessions = np.where(is_customer_session & purchased_flag & ~linked_to_a_campaign_flag & ~prob_of_premium_sessions)[0]
    mid_starts = session_start_times[eligible_mid_level_sessions].to_numpy()
    mid_startup_dates = mid_level_customers['signup_date'].to_numpy()
    mid_ids = mid_level_customers['customer_id'].to_numpy()
    sorted_mid_idx = np.argsort(mid_startup_dates)
    sorted_mid_dates = mid_startup_dates[sorted_mid_idx]
    sorted_mid_ids = mid_ids[sorted_mid_idx]

    mid_positions = np.arange(1, len(sorted_mid_ids) + 1, dtype=float)

    for i, idx in enumerate(eligible_mid_level_sessions):
        cutoff = np.searchsorted(sorted_mid_dates, mid_starts[i], side='right')
        valid_ids = sorted_mid_ids[:cutoff]
        if valid_ids.size > 0:
            w = mid_positions[:cutoff]
            w = w / w.sum()
            customer_ids[idx] = np.random.choice(valid_ids, p=w)

    eligible_basic_level_sessions = np.where(is_customer_session & purchased_flag & linked_to_a_campaign_flag & prob_of_basic_sessions)[0]
    basic_starts = session_start_times[eligible_basic_level_sessions].to_numpy()
    basic_startup_dates = basic_level_customers['signup_date'].to_numpy()
    basic_ids = basic_level_customers['customer_id'].to_numpy()
    sorted_basic_idx = np.argsort(basic_startup_dates)
    sorted_basic_dates = basic_startup_dates[sorted_basic_idx]
    sorted_basic_ids = basic_ids[sorted_basic_idx]

    basic_positions = np.arange(1, len(sorted_basic_ids) + 1, dtype=float)

    for i, idx in enumerate(eligible_basic_level_sessions):
        cutoff = np.searchsorted(sorted_basic_dates, basic_starts[i], side='right')
        valid_ids = sorted_basic_ids[:cutoff]
        if valid_ids.size > 0:
            w = basic_positions[:cutoff]
            w = w / w.sum()
            customer_ids[idx] = np.random.choice(valid_ids, p=w)

    eligible_customer_sessions = np.where(np.logical_and(is_customer_session, pd.isnull(customer_ids)))[0]
    customer_starts = session_start_times[eligible_customer_sessions].to_numpy()
    customer_signup_dates = all_customers['signup_date'].to_numpy()
    customer_ids_array = all_customers['customer_id'].to_numpy()
    sorted_idx = np.argsort(customer_signup_dates)
    sorted_dates = customer_signup_dates[sorted_idx]
    sorted_ids = customer_ids_array[sorted_idx]

    for i, idx in enumerate(eligible_customer_sessions):
        cutoff = np.searchsorted(sorted_dates, customer_starts[i], side='right')
        valid_ids = sorted_ids[:cutoff]
        if valid_ids.size > 0:
            customer_ids[idx] = np.random.choice(valid_ids)

    purchased_idx = np.where(purchased_flag)[0]
    aov[purchased_idx] = np.random.choice(
        ['Low', 'Mid', 'High'],
        p=[0.55, 0.30, 0.15],
        size=len(purchased_idx)
    )

    for idx in eligible_premium_sessions:
        if customer_ids[idx] is not None:
            aov[idx] = 'High'


    for idx in eligible_basic_level_sessions:
        if customer_ids[idx] is not None:
            aov[idx] = 'Low'

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
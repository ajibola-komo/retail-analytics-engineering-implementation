with source as (
    select campaign_id::INTEGER as campaign_id, campaign_name, lower(campaign_channel) as campaign_channel,
    promo_id,
    campaign_start_date::timestamp_ntz as campaign_start_date, campaign_start_date_id::INTEGER as campaign_start_date_id,
    campaign_end_date::timestamp_ntz as campaign_end_date, campaign_end_date_id::INTEGER as campaign_end_date_id 
    from {{source('bronze','dim_campaign')}}
) select * from source
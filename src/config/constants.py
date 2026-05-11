import numpy as np
from datetime import timedelta, datetime, time, date


CURRENT_YEAR = datetime.now().year
CURRENT_DATE = datetime.now().date()
CURRENT_TIMESTAMP = datetime.now()
START_YEAR = CURRENT_YEAR - 3
BASE_TRANSACTION_TIME_STAMP_Y1 = datetime.combine(date(START_YEAR,1,1), time(0,0,0))
BASE_TRANSACTION_END_TIMESTAMP_Y1 = datetime.combine(date(START_YEAR,12,31), time(23,59,59))
BASE_TRANSACTION_TIME_STAMP_Y2 = datetime.combine(date(START_YEAR + 1,1,1), time(0,0,0))
BASE_TRANSACTION_END_TIMESTAMP_Y2 = datetime.combine(date(START_YEAR + 1,12,31), time(23,59,59))
BASE_TRANSACTION_TIME_STAMP_Y3 = datetime.combine(date(START_YEAR + 2,1,1), time(0,0,0))
BASE_TRANSACTION_END_TIMESTAMP_Y3 = datetime.combine(date(START_YEAR + 2,12,31), time(23,59,59))
Y1 = BASE_TRANSACTION_END_TIMESTAMP_Y1.year
Y2 = BASE_TRANSACTION_END_TIMESTAMP_Y2.year
Y3 = BASE_TRANSACTION_END_TIMESTAMP_Y3.year
COMPANY_START_TIMESTAMP = datetime.combine(date(2001,5,30), time(10,0,0))
COMPANY_START_DATE = date(2001,5,30)

#--------------------------- CUSTOMERS TABLE -----------------------------------------

PROVINCE_CITY_MAP = {
    "Ontario": {
        "cities": ["Toronto", "Ottawa", "Mississauga"],
        "location_type": ["Urban", "Urban", "Suburban"],
        "location_weights": [0.18, 0.08, 0.06]   # ~32% total
    },
    "Quebec": {
        "cities": ["Montreal", "Gatineau"],
        "location_type": ["Urban", "Suburban"],
        "location_weights": [0.18, 0.04]           # ~22% total
    },
    "British Columbia": {
        "cities": ["Vancouver", "Burnaby"],
        "location_type": ["Urban", "Suburban"],
        "location_weights": [0.10, 0.08]           # ~18% total
    },
    "Alberta": {
        "cities": ["Calgary", "Red Deer"],
        "location_type": ["Urban", "Rural"],
        "location_weights": [0.10, 0.02]           # ~12% total
    },
    "Manitoba": {
        "cities": ["Winnipeg"],
        "location_type": ["Urban"],
        "location_weights": [0.06]                 # ~6% total
    },
    "Saskatchewan": {
        "cities": ["Regina"],
        "location_type": ["Suburban"],
        "location_weights": [0.05]                 # ~5% total
    },
    "Prince Edward Island": {
        "cities": ["Charlottetown"],
        "location_type": ["Rural"],
        "location_weights": [0.01]                 # ~1% total
    }
}

PROVINCES = list(PROVINCE_CITY_MAP.keys())

FOOT_TRAFFIC = {
    "Urban": (75, 90),
    "Suburban": (50, 70),
    "Rural": (20, 40)
}
  
CUSTOMER_GENDER = ["Male", "Female", "Other"]

CUSTOMERS_PERSONA_MAP = {
    "Tech Enthusiast": {"age_range":(25,40), "weight":0.2, "gender_weight":[0.55,0.4,0.05], "income_range":(60_000,1_00_000)},
    "Bargain Hunter": {"age_range":(18,35), "weight":0.25, "gender_weight":[0.5,0.45,0.05], "income_range":(10_000,50_000)},
    "Gift Shopper": {"age_range":(28,45), "weight":0.05, "gender_weight":[0.35,0.6,0.05], "income_range":(40_000,80_000)},
    "Everyday Shopper": {"age_range":(30,50), "weight":0.4, "gender_weight":[0.5,0.48,0.02], "income_range":(60_000,100_000)},
    "Practical Buyer": {"age_range":(30,60), "weight":0.1, "gender_weight":[0.6,0.38,0.02], "income_range":(30_000,70_000)}
}

CUSTOMER_PERSONAS = list(CUSTOMERS_PERSONA_MAP.keys())
PERSONA_WEIGHTS = [CUSTOMERS_PERSONA_MAP[k]['weight'] for k in CUSTOMER_PERSONAS]
    
CUSTOMER_SIGNUP_CHANNEL = ["In-Store", "Online", "Mobile"]
CUSTOMER_LOYALTY_STATUS = ['Elite', 'Gold', 'Silver', 'Basic']
CUSTOMER_EMAIL_OPT_IN = [True, False]
CUSTOMER_SMS_OPT_IN = [True, False]
CUSTOMER_EMAIL_DOMAIN = ['@example.com','@bac.com','@xyz.com','@mail.com']

SIGNUP_MONTH_WEIGHTS = [
    1.1, 0.9, 0.92, 0.95,
    1.00, 1.02, 1.05, 1.03,
    1.00, 1.05, 1.20, 1.40
]

#------------------------------------- STORES TABLE -----------------------------------
COMPANY_NAME = 'ELEC-MART'
STORE_TYPES_MAP = {
    "Mall":{
        "store_weight":0.35,
        "store_size":(300,1200)
    },
    "Outlet":{
        "store_weight":0.20,
        "store_size":(200,900)
    },
    "Standalone":{
        "store_weight":0.35,
        "store_size":(400,1500)
    },
    "Warehouse":{
        "store_weight":0.10,
        "store_size":(3000,8000)
    }
}
STORE_TYPES = list(STORE_TYPES_MAP.keys())
STORE_WEIGHTS = [STORE_TYPES_MAP[k]['store_weight'] for k in STORE_TYPES]


#-------------------------------------- PROMOTIONS TABLE ------------------------------
JAN_FEB_PROMOTIONS_NAMES = ["New Year Mega Sale", "January Clearance Deals","Cold Season Appliance Sale"]
MID_YEAR_PROMOTIONS_NAMES = ["Summer Power Sale","Hot Tech Deals","Plug-In & Save","Mobile Life Sale","Smart Summer Savings"]
YEAR_END_PROMOTIONS_NAMES = ["Holiday Season Specials","Christmas Mega Sale","Year-End Clearance","Boxing Day Deals","Holiday Tech Gifts","End-of-Year Super Sale"]
WEEKEND_PROMOTIONS_NAMES = ["Weekend Flash Sale","Deal of the Day","Customer Appreciation Sale","Limited Time Offers","Cyber Monday Sale"]
PRE_HOLIDAY_PROMOTIONS_NAMES = ["Early Holiday Deals","Pre-Holiday Specials"]
BLACK_FRIDAY_PROMOTION_NAMES = ["Black Friday Mega Deals"]
OTHER_PROMOTIONS_NAMES = ["Power Hour Deals","Gadget Grab","Flash Tech Sale","Plug & Save","Stock-Clearance Surge"]

PROMOTION_DISCOUNT_TYPES = ["Percentage_Discount","Fixed_Amount_Discount"]
PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y1 = [0.65,0.35]
PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y2 = [0.6,0.4]
PROMOTIONS_DISCOUNT_TYPES_WEIGHTING_Y3 = [0.7,0.3]

PERCENTAGE_DISCOUNT_VALUES = [0.05,0.1,0.15,0.2]
PERCENTAGE_DISCOUNT_WEIGHTING = [0.2,0.4,0.25,0.15]

FIXED_AMOUNT_DISCOUNT_VALUES = [20,25]
FIXED_AMOUNT_DISCOUNT_WEIGHTING = [0.8,0.2]

PROMO_TYPE_MAP = {
    'Major':
    {
        'months':[1,7,11,12],
        'promo_duration':[7,14],
        'cooldown':5,
        'weight':0.4,
        'months_weight':[0.3,0.2,0.2,0.3]
    },
    'Medium':
    {
        'months':[2,9,10],
        'promo_duration':[5,7],
        'cooldown':3,
        'weight':0.35,
        'months_weight':[0.3,0.35,0.35]
    },
    'Flash':
    {
        'months':[3,4,5,6,7,8],
        'promo_duration':[1,3],
        'cooldown':1,
        'weight':0.25,
        'months_weight':[0.15,0.15,0.15,0.2,0.15,0.2]
    } 
}
PROMO_TYPES = list(PROMO_TYPE_MAP.keys())
PROMO_TYPES_WEIGHTS = [PROMO_TYPE_MAP[k]['weight'] for k in PROMO_TYPES]


MONTH_WEIGHTS_PROMOTIONS_Y1 = [
    0.70, 0.75, 0.85, 0.95,
    1.00, 1.05, 1.08, 1.10,
    1.05, 1.15, 1.55, 1.80
]
MONTH_WEIGHTS_PROMOTIONS_Y2 = [
    0.72, 0.78, 0.88, 0.97,
    1.02, 1.08, 1.10, 1.12,
    1.08, 1.18, 1.60, 1.85
]
MONTH_WEIGHTS_PROMOTIONS_Y3 = [
    0.75, 0.80, 0.90, 1.00,
    1.05, 1.10, 1.12, 1.15,
    1.10, 1.20, 1.65, 1.90
]


#------------------------------------------------ CAMPAIGNS_TABLE ----------------------------------
CAMPAIGN_LINK_MAP = {
    'Promo':{
        'weight':0.55
    },
    'Normal':{
        'weight':0.45
    }
}

CAMPAIGN_LINK = list(CAMPAIGN_LINK_MAP.keys())
CAMPAIGN_LINK_WEIGHT = [CAMPAIGN_LINK_MAP[k]['weight'] for k in CAMPAIGN_LINK]

CAMPAIGN_CHANNEL = ['Email', 'SMS', 'Google Ads']
CAMPAIGN_CHANNELS_WEIGHTS_Y1 = [0.5,0.2,0.3]
CAMPAIGN_CHANNELS_WEIGHTS_Y2 = [0.45,0.15,0.4]
CAMPAIGN_CHANNELS_WEIGHTS_Y3 = [0.25,0.1,0.65]

CAMPAIGN_COOLDOWN_PERIODS = [2,5,7]

CAMPAIGN_PERIOD_OF_VALIDITY = [3,12,24]

MONTH_WEIGHTS_CAMPAIGNS_Y1 = [
    0.65, 0.70, 0.80, 0.90,
    0.98, 1.05, 1.10, 1.12,
    1.08, 1.20, 1.60, 1.85
]
MONTH_WEIGHTS_CAMPAIGNS_Y2 = [
    0.68, 0.73, 0.83, 0.93,
    1.00, 1.08, 1.12, 1.15,
    1.10, 1.22, 1.65, 1.90
]
MONTH_WEIGHTS_CAMPAIGNS_Y3 = [
    0.70, 0.75, 0.85, 0.95,
    1.02, 1.10, 1.15, 1.18,
    1.12, 1.25, 1.70, 1.95
]

#------------------------------------------- CLICKSTREAMS ------------------------------------------------

# Campaign
CAMPAIGN_SESSION_MINUTES = [0.5, 1, 2, 3, 5, 8, 12]
CAMPAIGN_SESSION_WEIGHTS_Y1 = [0.08, 0.12, 0.22, 0.25, 0.18, 0.10, 0.05]
CAMPAIGN_SESSION_WEIGHTS_Y2 = [0.06, 0.11, 0.21, 0.25, 0.20, 0.11, 0.06]
CAMPAIGN_SESSION_WEIGHTS_Y3 = [0.05, 0.10, 0.20, 0.25, 0.22, 0.12, 0.06]

# Paid Search
PAID_SEARCH_SESSION_MINUTES = [0.5, 1, 2, 3, 5, 8, 12]
PAID_SEARCH_SESSION_WEIGHTS_Y1 = [0.10, 0.14, 0.23, 0.24, 0.16, 0.09, 0.04]
PAID_SEARCH_SESSION_WEIGHTS_Y2 = [0.09, 0.13, 0.22, 0.25, 0.17, 0.10, 0.04]
PAID_SEARCH_SESSION_WEIGHTS_Y3 = [0.08, 0.12, 0.22, 0.25, 0.18, 0.10, 0.05]

# Organic
ORGANIC_SESSION_MINUTES = [0.5, 1, 2, 3, 5, 8, 12]
ORGANIC_SESSION_WEIGHTS_Y1 = [0.15, 0.20, 0.25, 0.20, 0.12, 0.06, 0.02]
ORGANIC_SESSION_WEIGHTS_Y2 = [0.14, 0.19, 0.25, 0.21, 0.13, 0.06, 0.02]
ORGANIC_SESSION_WEIGHTS_Y3 = [0.13, 0.18, 0.25, 0.22, 0.13, 0.07, 0.02]

# Direct
DIRECT_SESSION_MINUTES = [0.5, 1, 2, 3, 5, 8, 12]
DIRECT_SESSION_WEIGHTS_Y1 = [0.20, 0.23, 0.25, 0.17, 0.09, 0.04, 0.02]
DIRECT_SESSION_WEIGHTS_Y2 = [0.19, 0.22, 0.25, 0.18, 0.10, 0.04, 0.02]
DIRECT_SESSION_WEIGHTS_Y3 = [0.18, 0.22, 0.25, 0.18, 0.10, 0.05, 0.02]

# Referral
REFERRAL_SESSION_MINUTES = [0.5, 1, 2, 3, 5, 8, 12]
REFERRAL_SESSION_WEIGHTS_Y1 = [0.22, 0.23, 0.25, 0.17, 0.08, 0.04, 0.01]
REFERRAL_SESSION_WEIGHTS_Y2 = [0.21, 0.23, 0.25, 0.17, 0.09, 0.04, 0.01]
REFERRAL_SESSION_WEIGHTS_Y3 = [0.20, 0.22, 0.25, 0.18, 0.10, 0.04, 0.01]

DEVICE_TYPES = ["Mobile","Tablet","Desktop"]
DEVICE_WEIGHTS_Y1 = [0.45,0.3,0.25]
DEVICE_WEIGHTS_Y2 = [0.55,0.3,0.15]
DEVICE_WEIGHTS_Y3 = [0.55,0.2,0.25]

TRAFFIC_SOURCES = ["Organic", "Paid Search", "Direct", "Referral"]
TRAFFIC_WEIGHTS_Y1 = [0.40, 0.2, 0.22, 0.18]
TRAFFIC_WEIGHTS_Y2 = [0.35, 0.25, 0.25, 0.15]
TRAFFIC_WEIGHTS_Y3 = [0.30, 0.30, 0.25, 0.15]

PROB_OF_CUSTOMER_SESSION_Y1 = 0.55        # Known vs guest
PROB_OF_CUSTOMER_SESSION_Y2 = 0.60        # Known vs guest
PROB_OF_CUSTOMER_SESSION_Y3 = 0.63        # Known vs guest

# ── Year 1 ────────────────────────────────────────────────────────────────────
# Effective rates: Organic 4.5%, Paid 6.2%, Direct 4.2%, Referral 3.7%, Campaign 7.2%

# Intent (browse → cart)
PROB_INTENT_ORGANIC_Y1      = 0.18
PROB_INTENT_PAID_SEARCH_Y1  = 0.22
PROB_INTENT_DIRECT_Y1       = 0.16
PROB_INTENT_REFERRAL_Y1     = 0.17
PROB_INTENT_CAMPAIGN_Y1     = 0.24

# Purchase (cart → buy)
PROB_PURCHASE_ORGANIC_Y1      = 0.25
PROB_PURCHASE_PAID_SEARCH_Y1  = 0.28
PROB_PURCHASE_DIRECT_Y1       = 0.26
PROB_PURCHASE_REFERRAL_Y1     = 0.22
PROB_PURCHASE_CAMPAIGN_Y1     = 0.30

# ── Year 2 ────────────────────────────────────────────────────────────────────
# Effective rates: Organic 5.4%, Paid 7.5%, Direct 5.1%, Referral 4.5%, Campaign 8.8%
# ~20% relative improvement over Y1 — brand maturity + better targeting

# Intent
PROB_INTENT_ORGANIC_Y2      = 0.22
PROB_INTENT_PAID_SEARCH_Y2  = 0.27
PROB_INTENT_DIRECT_Y2       = 0.20
PROB_INTENT_REFERRAL_Y2     = 0.21
PROB_INTENT_CAMPAIGN_Y2     = 0.29

# Purchase
PROB_PURCHASE_ORGANIC_Y2      = 0.28
PROB_PURCHASE_PAID_SEARCH_Y2  = 0.32
PROB_PURCHASE_DIRECT_Y2       = 0.29
PROB_PURCHASE_REFERRAL_Y2     = 0.25
PROB_PURCHASE_CAMPAIGN_Y2     = 0.34

# ── Year 3 ────────────────────────────────────────────────────────────────────
# Effective rates: Organic 6.5%, Paid 9.0%, Direct 6.1%, Referral 5.4%, Campaign 10.8%
# ~20% relative improvement over Y2 — loyalty + personalisation kicking in

# Intent
PROB_INTENT_ORGANIC_Y3      = 0.26
PROB_INTENT_PAID_SEARCH_Y3  = 0.32
PROB_INTENT_DIRECT_Y3       = 0.24
PROB_INTENT_REFERRAL_Y3     = 0.25
PROB_INTENT_CAMPAIGN_Y3     = 0.35

# Purchase
PROB_PURCHASE_ORGANIC_Y3      = 0.32
PROB_PURCHASE_PAID_SEARCH_Y3  = 0.36
PROB_PURCHASE_DIRECT_Y3       = 0.33
PROB_PURCHASE_REFERRAL_Y3     = 0.28
PROB_PURCHASE_CAMPAIGN_Y3     = 0.38

# ── Attribution ───────────────────────────────────────────────────────────────
PROB_OF_CAMPAIGN_LINKED_Y1  = 0.35
PROB_OF_CAMPAIGN_LINKED_Y2  = 0.40
PROB_OF_CAMPAIGN_LINKED_Y3  = 0.45

PROB_OF_REPEATED_SESSION_Y1 = 0.2               # Repeat visits/sessions
PROB_OF_REPEATED_SESSION_Y2 = 0.25               # Repeat visits/sessions
PROB_OF_REPEATED_SESSION_Y3 = 0.30               # Repeat visits/sessions

REPEATED_SESSION_SUBSET_PREMIUM = 1.2
REPEATED_SESSION_SUBSET_MID = 1.2
REPEATED_SESSION_SUBSET_BASIC = 1.5

#----------------------------------------- Transactions ------------------------------------------------------


PAYMENT_TYPES = [
    "Credit Card",
    "Debit Card",
    "Cash",
    "Gift Card",
    "Apple Pay",
    "Google Pay",
    "PayPal"
]

PAYMENT_TYPES_WEIGHTS = [0.40, 0.35, 0.10, 0.05, 0.05, 0.03, 0.02]

TRANSACTION_STATUSES = [
    "Completed",
    "Returned"]

TRANSACTION_WEIGHTS_Y1 = [0.93, 0.07]
TRANSACTION_WEIGHTS_Y2 = [0.95, 0.05]
TRANSACTION_WEIGHTS_Y3 = [0.945, 0.055]

TRANSACTION_TOTAL_RANGE = np.array([(20,120), (120,600), (600,3000)])

TRANSACTION_TOTAL_DISTRIBUTION = [0.7,0.25,0.05]

#INVENTORY TABLE
SHRINKAGE_RATE_Y1 = 0.02
SHRINKAGE_RATE_Y2 = 0.04
SHRINKAGE_RATE_Y3 = 0.06

INVENTORY_START_ID = 1_000_001

# FACT SALE
SALES_START_ID = 12_000_363
TRANSACTION_START_ID = 8_000_125
SESSION_START_ID = 9_000_862


MONTH_NUMBERS = [1,2,3,4,5,6,7,8,9,10,11,12]

MONTH_WEIGHTS_ONLINE_Y1 = [
    0.82, 0.86, 0.92, 1.00,
    1.05, 1.10, 1.08, 1.06,
    1.02, 1.12, 1.45, 1.70
]

MONTH_WEIGHTS_STORE_Y1 = [
    0.96, 0.97, 0.99, 1.02,
    1.05, 1.08, 1.10, 1.09,
    1.05, 1.12, 1.32, 1.55
]

MONTH_WEIGHTS_ONLINE_Y2 = [
    0.86, 0.88, 0.94, 1.02,
    1.08, 1.15, 1.14, 1.12,
    1.10, 1.25, 1.55, 1.85
]

MONTH_WEIGHTS_STORE_Y2 = [
    0.94, 0.95, 0.98, 1.00,
    1.03, 1.06, 1.08, 1.07,
    1.05, 1.10, 1.25, 1.45
]

MONTH_WEIGHTS_ONLINE_Y3 = [
    0.88, 0.90, 0.96, 1.05,
    1.12, 1.18, 1.16, 1.14,
    1.12, 1.30, 1.65, 2.00
]

MONTH_WEIGHTS_STORE_Y3 = [
    0.92, 0.93, 0.96, 0.98,
    1.00, 1.02, 1.04, 1.03,
    1.02, 1.08, 1.20, 1.35
]

PRODUCT_RANGES= ['Low','Mid','High']
PRODUCT_WEIGHTS = [0.4,0.35,0.25]



















import numpy as np
from datetime import timedelta, datetime, time, date


CURRENT_YEAR = datetime.now().year
CURRENT_DATE = datetime.now().date()
CURRENT_TIMESTAMP = datetime.now()
START_YEAR = CURRENT_YEAR - 3
BASE_TRANSACTION_TIME_STAMP_Y1 = datetime.combine(date(START_YEAR,1,1), time(0,0,0))
BASE_TRANSACTION_END_TIMESTAMP_Y1 = datetime.combine(date(START_YEAR,12,31), time(23,59,59))
BASE_TRANSACTION_TIME_STAMP_Y2 = datetime.combine(date(START_YEAR + 1,1,1), time(0,0,0))
BASE_TRANSACTION_END_TIMESTAMP_Y2 = datetime.combine(date(START_YEAR + 1,12,31), time(21,59,59))
BASE_TRANSACTION_TIME_STAMP_Y3 = datetime.combine(date(START_YEAR + 2,1,1), time(0,0,0))
BASE_TRANSACTION_END_TIMESTAMP_Y3 = datetime.combine(date(START_YEAR + 2,12,31), time(21,59,59))
Y1 = BASE_TRANSACTION_END_TIMESTAMP_Y1.year
Y2 = BASE_TRANSACTION_END_TIMESTAMP_Y2.year
Y3 = BASE_TRANSACTION_END_TIMESTAMP_Y3.year
COMPANY_START_TIMESTAMP = datetime.combine(date(2001,5,30), time(10,0,0))
COMPANY_START_DATE = date(2001,5,30)

#--------------------------- CUSTOMERS TABLE -----------------------------------------

PROVINCE_CITY_MAP = {
    "Ontario": {
        "cities": ["Toronto", "Ottawa", "Mississauga", "London", "Hamilton"],
        "location_type": ["Urban", "Urban", "Suburban", "Suburban", "Suburban"],
        "location_weights": [0.1, 0.07, 0.05, 0.04, 0.04]
    },

    "Quebec": {
        "cities": ["Montreal", "Quebec City", "Laval", "Gatineau"],
        "location_type": ["Urban", "Urban", "Suburban", "Suburban"],
        "location_weights": [0.1, 0.05, 0.03, 0.02]
    },

    "British Columbia": {
        "cities": ["Vancouver", "Surrey", "Burnaby", "Victoria"],
        "location_type": ["Urban", "Suburban", "Suburban", "Suburban"],
        "location_weights": [0.08, 0.03, 0.02, 0.02]
    },

    "Alberta": {
        "cities": ["Calgary", "Edmonton", "Red Deer"],
        "location_type": ["Urban", "Urban", "Rural"],
        "location_weights": [0.06, 0.06, 0.03]
    },

    "Manitoba": {
        "cities": ["Winnipeg", "Brandon"],
        "location_type": ["Urban", "Rural"],
        "location_weights": [0.04, 0.02]
    },

    "Saskatchewan": {
        "cities": ["Regina", "Saskatoon"],
        "location_type": ["Suburban", "Suburban"],
        "location_weights": [0.03, 0.01]
    },

    "Nova Scotia": {
        "cities": ["Halifax"],
        "location_type": ["Suburban"],
        "location_weights": [0.02]
    },

    "New Brunswick": {
        "cities": ["Fredericton", "Moncton"],
        "location_type": ["Rural", "Suburban"],
        "location_weights": [0.03, 0.02]
    },

    "Prince Edward Island": {
        "cities": ["Charlottetown"],
        "location_type": ["Rural"],
        "location_weights": [0.02]
    },

    "Newfoundland & Labrador": {
        "cities": ["St. John's"],
        "location_type": ["Suburban"],
        "location_weights": [0.01]
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

#------------------------------------------- CLICKSTREAMS ------------------------------------------------
SESSION_MINUTES = [0.5, 1, 2, 3, 5, 8, 12]
SESSION_WEIGHTS = [0.15, 0.20, 0.25, 0.20, 0.12, 0.06, 0.02]

DEVICE_TYPES = ["Mobile","Tablet","Desktop"]
DEVICE_WEIGHTS_Y1 = [0.45,0.3,0.25]
DEVICE_WEIGHTS_Y2 = [0.55,0.3,0.15]
DEVICE_WEIGHTS_Y3 = [0.55,0.2,0.25]

TRAFFIC_SOURCES = ["Organic", "Paid Search", "Direct", "Referral"]
TRAFFIC_WEIGHTS_Y1 = [0.40, 0.2, 0.22, 0.18]
TRAFFIC_WEIGHTS_Y2 = [0.35, 0.25, 0.25, 0.15]
TRAFFIC_WEIGHTS_Y3 = [0.30, 0.30, 0.25, 0.15]

PROB_OF_CUSTOMER_SESSION_Y1 = 0.65        # Known vs guest
PROB_OF_CUSTOMER_SESSION_Y2 = 0.70        # Known vs guest
PROB_OF_CUSTOMER_SESSION_Y3 = 0.65        # Known vs guest

PROB_OF_PURCHASE_INTENTION_Y1 = 0.35     # Browsing → cart intent
PROB_OF_PURCHASE_INTENTION_Y2 = 0.42     # Browsing → cart intent
PROB_OF_PURCHASE_INTENTION_Y3 = 0.50     # Browsing → cart intent

PROB_OF_PURCHASE_Y1 = 0.3                 # Cart → purchase
PROB_OF_PURCHASE_Y2 = 0.35                # Cart → purchase
PROB_OF_PURCHASE_Y3 = 0.40                # Cart → purchase

PROB_OF_CAMPAIGN_LINKED_Y1 = 0.35         # Attribution
PROB_OF_CAMPAIGN_LINKED_Y2 = 0.40         # Attribution
PROB_OF_CAMPAIGN_LINKED_Y3 = 0.45         # Attribution

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

TRANSACTION_WEIGHTS_Y1 = [0.92, 0.08]
TRANSACTION_WEIGHTS_Y2 = [0.90, 0.10]
TRANSACTION_WEIGHTS_Y3 = [0.88, 0.12]

TRANSACTION_TOTAL_RANGE = np.array([(20,120), (120,600), (600,3000)])

TRANSACTION_TOTAL_DISTRIBUTION = [0.7,0.25,0.05]

#INVENTORY TABLE
SHRINKAGE_RATE_Y1 = 0.02
SHRINKAGE_RATE_Y2 = 0.05
SHRINKAGE_RATE_Y3 = 0.75

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



















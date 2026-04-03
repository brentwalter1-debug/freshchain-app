import streamlit as st
import pandas as pd
import numpy as np
import math
import random
import datetime
import time
import html

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FreshChain Cold Logistics",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f0fdf4; } 
    
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stVerticalBlock"] > div[style*="background-color"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    /* BUTTON STYLING */
    button[kind="primary"] {
        background-color: #059669 !important;
        border-color: #059669 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.2s !important;
    }
    button[kind="primary"]:hover {
        background-color: #047857 !important;
        border-color: #047857 !important;
        transform: translateY(-1px);
    }
    
    button[kind="secondary"] {
        background-color: white !important;
        border: 1px solid #d1d5db !important;
        color: #374151 !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
    }
    button[kind="secondary"]:hover {
        border-color: #9ca3af !important;
        color: #111827 !important;
        background-color: #f9fafb !important;
    }
    
    .status-badge { padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; }
    .status-green { background-color: #d1fae5; color: #065f46; }
    .status-blue { background-color: #dbeafe; color: #1e40af; }
    .status-orange { background-color: #ffedd5; color: #9a3412; }
    .status-gray { background-color: #f3f4f6; color: #374151; }
    .status-purple { background-color: #f3e8ff; color: #6b21a8; }
    
    .tag { font-size: 11px; font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-right: 5px; }
    .tag-temp { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }

    .news-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 4px solid #059669; margin-bottom: 12px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Login Animation */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .login-container { animation: slideUp 0.6s ease-out; }
    </style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'user' not in st.session_state: st.session_state.user = None
if 'username' not in st.session_state: st.session_state.username = None
if 'skip_confirm' not in st.session_state: st.session_state.skip_confirm = False
if 'skip_acct_confirm' not in st.session_state: st.session_state.skip_acct_confirm = False
if 'skip_bid_confirm' not in st.session_state: st.session_state.skip_bid_confirm = False
if 'confirm_bid_adjust' not in st.session_state: st.session_state.confirm_bid_adjust = None
if 'pulp_log' not in st.session_state: st.session_state.pulp_log = [] 
if 'truck_search_active' not in st.session_state: st.session_state.truck_search_active = False
if 'load_search_active' not in st.session_state: st.session_state.load_search_active = False
if 'expanded_convo' not in st.session_state: st.session_state.expanded_convo = None
if 'reply_error' not in st.session_state: st.session_state.reply_error = None
if 'confirming_acct_id' not in st.session_state: st.session_state.confirming_acct_id = None
if 'dash_prefs' not in st.session_state: st.session_state.dash_prefs = {'show_metrics': True, 'show_actions': True, 'show_activity': True, 'show_news': True}
if 'news_sites' not in st.session_state: st.session_state.news_sites = ["FreightWaves", "Produce Blue Book"]

# NEW DATE FORMAT CONSTANT (US Standard)
DATE_FMT = "%m/%d/%Y"

# Initialize inputs
widget_keys = [
    'so_drop', 'sd_drop', 'so_c', 'so_z', 'sd_c', 'sd_z',
    'fto_drop', 'ftd_drop', 'fto_c', 'fto_z', 'ftd_c', 'ftd_z',
    'pto_drop', 'ptd_drop', 'pto_c', 'pto_z', 'ptd_c', 'ptd_z',
    'plo_drop', 'pld_drop', 'plo_c', 'plo_z', 'pld_c', 'pld_z',
    'pl_comm', 'pl_min', 'pl_max', 'pl_weight', 'pl_rate', 'pl_notes',
    'pt_weight', 'pt_rate', 'pt_notes',
    'pl_appt_time'
]
QUICK_LIST = ["Select from List...", "Salinas, CA (939)", "Yuma, AZ (853)", "McAllen, TX (785)", "Nogales, AZ (856)", "Miami, FL (331)", "Chicago, IL (606)", "Bronx, NY (104)", "Atlanta, GA (303)", "Philadelphia, PA (191)"]
# Modified list for "Anywhere" destinations
ANYWHERE_LIST = ["Select...", "Anywhere", "Salinas, CA (939)", "Yuma, AZ (853)", "McAllen, TX (785)", "Nogales, AZ (856)", "Miami, FL (331)", "Chicago, IL (606)", "Bronx, NY (104)", "Atlanta, GA (303)", "Philadelphia, PA (191)"]

for k in widget_keys:
    if k not in st.session_state:
        if 'drop' in k: 
            # Default logic
            st.session_state[k] = QUICK_LIST[0]
        elif k in ['pl_min', 'pl_max', 'pl_weight', 'pl_rate', 'pt_weight', 'pt_rate']:
            # Skip numeric keys so Streamlit native number_input handles the type initialization properly
            pass
        else: 
            st.session_state[k] = ""

# --- MOCK DATABASE (PRODUCE FOCUSED) ---
ZIP_MAP = { "93": {"lat": 36.6, "lon": -121.6}, "85": {"lat": 32.6, "lon": -114.6}, "78": {"lat": 26.2, "lon": -98.2}, "33": {"lat": 25.7, "lon": -80.2}, "60": {"lat": 41.8, "lon": -87.6}, "10": {"lat": 40.8, "lon": -73.8}, "30": {"lat": 33.7, "lon": -84.4}, "19": {"lat": 39.9, "lon": -75.1} }

USERS = {
    # SECURITY NOTE: In production, passwords must be securely hashed using libraries like bcrypt or argon2. 
    "ship_pro": {"pass": "1234", "role": "Shipper", "name": "GreenValley Growers", "stars": 4.9, "verified": True, "contact": "Shipping Dept", "phone": "555-0101", "email": "shipping@greenvalley.com", "profile_pic": None},
    "truck_guy": {"pass": "1234", "role": "Carrier", "name": "Cool Runnings Logistics", "stars": 4.8, "verified": True, "contact": "Jamal Davis", "phone": "555-0202", "email": "dispatch@coolrunnings.com", "profile_pic": None},
}

if 'users_db' not in st.session_state:
    st.session_state.users_db = USERS

CARRIER_DETAILS = {
    "Cool Runnings Logistics": {
        "MC": "123456",
        "DOT": "9876542",
        "Dispatcher": "Jamal Davis",
        "Phone": "(555) 019-2834",
        "Email": "dispatch@coolrunnings.com",
        "Driver": "Marcus Miller",
        "Cell": "(555) 992-1102",
        "Truck": "#104 (Kenworth T680)",
        "Trailer": "#5302 (ThermoKing)",
        "Insurance": "Active ($1M Liability / $100k Cargo)"
    }
}

COMMODITIES_DB = {
    "Apples": {"Temp": "32-34°F", "Sens": "High (Ethylene Sensitive)", "Notes": "Keep away from onions/carrots.", "MktPrice": 1.20, "Vol": "High"},
    "Apricots": {"Temp": "32-34°F", "Sens": "High", "Notes": "Handle gently to avoid bruising.", "MktPrice": 2.10, "Vol": "Med"},
    "Asparagus": {"Temp": "32-35°F", "Sens": "High", "Notes": "Stand upright if possible. High respiration.", "MktPrice": 2.80, "Vol": "Low"},
    "Avocados (Hass)": {"Temp": "40-55°F", "Sens": "High (Chill Injury Risk)", "Notes": "Do not freeze. Vent required.", "MktPrice": 1.95, "Vol": "High"},
    "Bananas": {"Temp": "56-58°F", "Sens": "Very High", "Notes": "Turns black below 55°F. Ethylene producer.", "MktPrice": 0.60, "Vol": "Very High"},
    "Beans (Snap)": {"Temp": "40-45°F", "Sens": "High (Chill Injury)", "Notes": "Do not ice. Keep dry.", "MktPrice": 1.50, "Vol": "Med"},
    "Beef (Fresh)": {"Temp": "28-32°F", "Sens": "High", "Notes": "Standard meat protocol.", "MktPrice": 3.50, "Vol": "High"},
    "Beef (Frozen)": {"Temp": "0°F to -10°F", "Sens": "Medium", "Notes": "Must remain hard frozen.", "MktPrice": 3.20, "Vol": "High"},
    "Blackberries": {"Temp": "32-34°F", "Sens": "Extreme", "Notes": "Very short shelf life.", "MktPrice": 4.50, "Vol": "Low"},
    "Blueberries": {"Temp": "32-34°F", "Sens": "High", "Notes": "Pre-cooling essential.", "MktPrice": 3.80, "Vol": "Med"},
    "Broccoli": {"Temp": "32°F", "Sens": "High", "Notes": "Often packed in ice. Top icing common.", "MktPrice": 1.10, "Vol": "High"},
    "Brussels Sprouts": {"Temp": "32°F", "Sens": "High", "Notes": "High respiration rate.", "MktPrice": 1.80, "Vol": "Med"},
    "Butter": {"Temp": "35-40°F", "Sens": "Medium", "Notes": "Absorbs odors easily.", "MktPrice": 2.50, "Vol": "High"},
    "Cabbage": {"Temp": "32°F", "Sens": "Medium", "Notes": "Good storage life.", "MktPrice": 0.40, "Vol": "High"},
    "Cantaloupe": {"Temp": "36-40°F", "Sens": "High", "Notes": "Full slip requires specific handling.", "MktPrice": 0.50, "Vol": "High"},
    "Carrots": {"Temp": "32°F", "Sens": "Medium", "Notes": "Keep away from ethylene sources.", "MktPrice": 0.65, "Vol": "Very High"},
    "Cauliflower": {"Temp": "32°F", "Sens": "High", "Notes": "Handle with care.", "MktPrice": 1.25, "Vol": "Med"},
    "Celery": {"Temp": "32°F", "Sens": "High", "Notes": "Requires high humidity.", "MktPrice": 0.90, "Vol": "High"},
    "Cheese (Hard)": {"Temp": "34-40°F", "Sens": "Medium", "Notes": "Maintain consistent temp.", "MktPrice": 4.00, "Vol": "High"},
    "Cherries": {"Temp": "32°F", "Sens": "High", "Notes": "Pre-cool immediately.", "MktPrice": 3.50, "Vol": "Low"},
    "Chicken (Fresh)": {"Temp": "26-32°F", "Sens": "High", "Notes": "Raw meat protocols apply.", "MktPrice": 1.80, "Vol": "Very High"},
    "Chicken (Frozen)": {"Temp": "-10°F to 0°F", "Sens": "Medium", "Notes": "Must remain frozen hard.", "MktPrice": 1.50, "Vol": "Very High"},
    "Chocolate": {"Temp": "65-68°F", "Sens": "High", "Notes": "Bloom risk if too hot or cold.", "MktPrice": 5.00, "Vol": "Med"},
    "Corn (Sweet)": {"Temp": "32°F", "Sens": "High", "Notes": "Sugars turn to starch quickly if warm.", "MktPrice": 0.45, "Vol": "High"},
    "Cucumbers": {"Temp": "50-55°F", "Sens": "High (Chill Injury)", "Notes": "Pitting occurs below 50°F.", "MktPrice": 0.70, "Vol": "High"},
    "Eggplant": {"Temp": "46-54°F", "Sens": "High (Chill Injury)", "Notes": "Sensitive to pitting.", "MktPrice": 1.10, "Vol": "Med"},
    "Eggs": {"Temp": "33-40°F", "Sens": "Medium", "Notes": "Do not freeze.", "MktPrice": 1.30, "Vol": "Very High"},
    "Fish (Fresh)": {"Temp": "30-32°F", "Sens": "Extreme", "Notes": "Pack in ice.", "MktPrice": 8.00, "Vol": "Low"},
    "Fish (Frozen)": {"Temp": "-10°F or lower", "Sens": "High", "Notes": "Strict temp control needed.", "MktPrice": 6.00, "Vol": "Med"},
    "Flowers (Cut)": {"Temp": "33-35°F", "Sens": "High", "Notes": "Ethylene sensitive.", "MktPrice": 15.00, "Vol": "Med"},
    "Garlic": {"Temp": "32°F", "Sens": "Low", "Notes": "Low humidity required.", "MktPrice": 2.20, "Vol": "Med"},
    "Grapefruit": {"Temp": "50-60°F", "Sens": "Medium", "Notes": "Chill injury possible.", "MktPrice": 0.80, "Vol": "Med"},
    "Grapes": {"Temp": "32°F", "Sens": "High", "Notes": "SO2 pads often used.", "MktPrice": 2.00, "Vol": "High"},
    "Honeydew": {"Temp": "45-50°F", "Sens": "High", "Notes": "Chill injury below 45°F.", "MktPrice": 0.60, "Vol": "Med"},
    "Ice Cream": {"Temp": "-20°F", "Sens": "Extreme", "Notes": "Melts/crystallizes easily.", "MktPrice": 3.50, "Vol": "High"},
    "Kiwifruit": {"Temp": "32°F", "Sens": "High", "Notes": "Very ethylene sensitive.", "MktPrice": 1.80, "Vol": "Low"},
    "Lemons": {"Temp": "45-50°F", "Sens": "Medium", "Notes": "Moderate shelf life.", "MktPrice": 1.10, "Vol": "High"},
    "Lettuce": {"Temp": "34°F", "Sens": "High", "Notes": "Ethylene sensitive. Russet spotting.", "MktPrice": 0.80, "Vol": "Very High"},
    "Limes": {"Temp": "45-50°F", "Sens": "Medium", "Notes": "Skin discoloration if too cold.", "MktPrice": 1.20, "Vol": "Med"},
    "Mangoes": {"Temp": "55°F", "Sens": "High", "Notes": "Do not chill below 50°F.", "MktPrice": 1.30, "Vol": "High"},
    "Milk": {"Temp": "33-40°F", "Sens": "High", "Notes": "Spoilage risk if warm.", "MktPrice": 0.40, "Vol": "Very High"},
    "Mushrooms": {"Temp": "32°F", "Sens": "High", "Notes": "Do not stack too high.", "MktPrice": 3.00, "Vol": "Med"},
    "Onions (Dry)": {"Temp": "32°F", "Sens": "Low", "Notes": "Keep dry. Ventilation crucial.", "MktPrice": 0.50, "Vol": "High"},
    "Oranges": {"Temp": "38-48°F", "Sens": "Medium", "Notes": "Temp depends on variety.", "MktPrice": 0.90, "Vol": "High"},
    "Peaches": {"Temp": "31-32°F", "Sens": "High", "Notes": "Wooliness if kept at 36-40°F.", "MktPrice": 1.90, "Vol": "Med"},
    "Pears": {"Temp": "30-32°F", "Sens": "High", "Notes": "Ripen at room temp.", "MktPrice": 1.50, "Vol": "Med"},
    "Peppers (Bell)": {"Temp": "45-55°F", "Sens": "High (Chill Injury)", "Notes": "Pitting below 45°F.", "MktPrice": 1.40, "Vol": "High"},
    "Pineapples": {"Temp": "45-50°F", "Sens": "Medium", "Notes": "Black heart if too cold.", "MktPrice": 0.80, "Vol": "High"},
    "Plums": {"Temp": "32°F", "Sens": "High", "Notes": "Similar to peaches.", "MktPrice": 1.70, "Vol": "Med"},
    "Pork (Fresh)": {"Temp": "28-32°F", "Sens": "High", "Notes": "Standard meat protocol.", "MktPrice": 2.20, "Vol": "High"},
    "Potatoes": {"Temp": "45-50°F", "Sens": "Low", "Notes": "Darkens if too cold.", "MktPrice": 0.45, "Vol": "Very High"},
    "Raspberries": {"Temp": "32°F", "Sens": "Extreme", "Notes": "Very delicate. Do not shake.", "MktPrice": 5.00, "Vol": "Low"},
    "Spinach": {"Temp": "32°F", "Sens": "High", "Notes": "Rapid cooling needed.", "MktPrice": 1.60, "Vol": "Med"},
    "Squash (Summer)": {"Temp": "41-50°F", "Sens": "High (Chill Injury)", "Notes": "Pitting risk.", "MktPrice": 1.00, "Vol": "Med"},
    "Strawberries": {"Temp": "32-34°F", "Sens": "Extreme", "Notes": "Remove field heat immediately.", "MktPrice": 2.50, "Vol": "High"},
    "Tomatoes": {"Temp": "55-60°F", "Sens": "Medium", "Notes": "Flavor loss if too cold.", "MktPrice": 1.10, "Vol": "High"},
    "Watermelon": {"Temp": "50-60°F", "Sens": "Medium", "Notes": "Chill injury below 50°F.", "MktPrice": 0.30, "Vol": "High"},
    "Yogurt": {"Temp": "35-40°F", "Sens": "High", "Notes": "Keep upright.", "MktPrice": 1.20, "Vol": "High"}
}

if 'messages_db' not in st.session_state:
    st.session_state.messages_db = []

# --- REVIEWS DATABASE ---
if 'reviews_db' not in st.session_state:
    st.session_state.reviews_db = []

# Message Structure: { "id": "uuid", "To": "user", "From": "user", "Msg": "txt", "Time": "time", "Status": "read/unread", "Folder": "inbox/sent/trash/archive", "Context": "txt" }

# --- SELF-HEALING DATA FIXER ---
if 'loads_db' in st.session_state:
    today_str = datetime.date.today().strftime(DATE_FMT)
    for l in st.session_state.loads_db:
        if 'DateStart' not in l: l['DateStart'] = today_str
        if 'DateEnd' not in l: l['DateEnd'] = today_str
        if 'id' not in l: l['id'] = f"L-{random.randint(10000,99999)}"
        if 'TeamReq' not in l: l['TeamReq'] = False
        if 'Docs' not in l: l['Docs'] = []
        if 'CarrierReviewed' not in l: l['CarrierReviewed'] = False
        if 'ShipperReviewed' not in l: l['ShipperReviewed'] = False
        if 'NewBooking' not in l: l['NewBooking'] = False
        if 'BidAccepted' not in l: l['BidAccepted'] = False
        # NEW: Status Log
        if 'StatusLog' not in l: l['StatusLog'] = []

if 'trucks_db' in st.session_state:
    today_str = datetime.date.today().strftime(DATE_FMT)
    for t in st.session_state.trucks_db:
        if 'Equip' not in t: t['Equip'] = 'Reefer'
        if 'DateStart' not in t: t['DateStart'] = today_str
        if 'DateEnd' not in t: t['DateEnd'] = today_str
        if 'id' not in t: t['id'] = f"T-{random.randint(10000,99999)}"
        if 'TeamTruck' not in t: t['TeamTruck'] = False
        if 'EmptyNow' not in t: t['EmptyNow'] = False

# FIX FOR KEY ERROR: Ensure all messages have IDs
if 'messages_db' in st.session_state:
    for m in st.session_state.messages_db:
        if 'id' not in m: m['id'] = f"MSG-{random.randint(10000, 99999)}"
        if 'Folder' not in m: m['Folder'] = 'inbox'
        if 'Status' not in m: m['Status'] = 'unread'
        if 'is_vip' not in m: m['is_vip'] = False
        if 'Context' not in m: m['Context'] = None

# --- MOCK DATA INIT ---
if 'loads_db' not in st.session_state:
    today_str = datetime.date.today().strftime(DATE_FMT)
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_FMT)
    st.session_state.loads_db = [
        {"id": "L-83921", "Origin City": "Salinas, CA", "Origin Zip": "93901", "Dest City": "Bronx, NY", "Dest Zip": "10474", "Commodity": "Strawberries", "Temp": "32-34 (Continuous)", "Weight": 38000, "Rate": 6500, "BookNow": True, "Status": "Open", "Shipper": "ship_pro", "Bids": [], "POD": False, "ETracks": False, "TeamReq": True, "Comments": "Handle with care.", "Docs": [], "DateStart": today_str, "DateEnd": today_str, "StatusLog": []},
        {"id": "L-29104", "Origin City": "McAllen, TX", "Origin Zip": "78501", "Dest City": "Chicago, IL", "Dest Zip": "60601", "Commodity": "Avocados", "Temp": "40-42 (Continuous)", "Weight": 42000, "Rate": 3200, "BookNow": False, "Status": "Open", "Shipper": "ship_pro", "Bids": [], "POD": False, "ETracks": False, "TeamReq": False, "Comments": "Check in at Gate 2.", "Docs": [], "DateStart": today_str, "DateEnd": tomorrow_str, "StatusLog": []},
    ]

if 'trucks_db' not in st.session_state:
    today_str = datetime.date.today().strftime(DATE_FMT)
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=2)).strftime(DATE_FMT)
    st.session_state.trucks_db = [{"id": "T-50192", "Origin City": "Yuma, AZ", "Origin Zip": "85364", "Dest City": "Anywhere", "Dest Zip": "", "Commodity": "Any Produce", "Weight": 44000, "Rate": 3.00, "RateType": "RPM", "Carrier": "truck_guy", "Comments": "Team drivers available.", "Equip": "Reefer", "DateStart": today_str, "DateEnd": tomorrow_str, "TeamTruck": True, "EmptyNow": True}]

# --- HELPERS ---
def get_coords(zip_code):
    if not zip_code: return {"lat": 39.8, "lon": -98.5}
    p2 = zip_code[:2]
    if p2 in ZIP_MAP: return ZIP_MAP[p2]
    return {"lat": 39.8, "lon": -98.5}

def get_dist_zips(z1, z2):
    if not z1 or not z2: return 9999
    c1, c2 = get_coords(z1), get_coords(z2)
    R = 3959
    a = 0.5 - math.cos(math.radians(c2['lat']-c1['lat']))/2 + math.cos(math.radians(c1['lat'])) * math.cos(math.radians(c2['lat'])) * (1-math.cos(math.radians(c2['lon']-c1['lon'])))/2
    return R * 2 * math.asin(math.sqrt(a))

def calculate_co2(miles, weight):
    tons = weight / 2000
    co2_kg = (miles * tons * 161.8) / 1000
    return f"{int(co2_kg)} kg"

def render_location_input(label_prefix, key_prefix, allow_anywhere=False):
    c1, c2 = st.columns([1,1])
    # Choose list based on allow_anywhere
    current_list = ANYWHERE_LIST if allow_anywhere else QUICK_LIST
    
    with c1: 
        choice = st.selectbox(f"{label_prefix}", current_list, key=f"{key_prefix}_drop", label_visibility="visible", 
                              on_change=lambda: st.session_state.update({'truck_search_active': False}))
    with c2:
        manual = (choice == "Select from List...") or (choice == "Anywhere")
        d_city, d_zip = ("", "")
        if not manual:
            try: d_city, d_zip = choice.split(" (")[0], choice.split(" (")[1].replace(")", "")
            except: pass
        
        # If Anywhere selected, pass "Anywhere" as city
        if choice == "Anywhere":
            d_city = "Anywhere"
            
        city = st.text_input("City", value=d_city if not manual else d_city, key=f"{key_prefix}_c", disabled=not manual or choice=="Anywhere", placeholder="City",
                             on_change=lambda: st.session_state.update({'truck_search_active': False}))
        zipc = st.text_input("Zip", value=d_zip if not manual else "", key=f"{key_prefix}_z", disabled=not manual or choice=="Anywhere", placeholder="Zip",
                             on_change=lambda: st.session_state.update({'truck_search_active': False}))
    
    # Return logic
    if choice == "Anywhere": return "Anywhere", ""
    if manual: return city, zipc
    else: return d_city, d_zip

def generate_code(prefix):
    return f"{prefix}-{random.randint(10000, 99999)}"

def format_date_range(s, e):
    if not s or s == 'N/A': return "Date N/A"
    if not e or e == 'N/A': return s
    if s == e: return s
    return f"{s} → {e}"

def check_overlap(search_start, search_end, item_start_str, item_end_str):
    try:
        if not item_start_str or item_start_str == 'N/A': return True 
        # Parse using the new Format
        i_start = datetime.datetime.strptime(item_start_str, DATE_FMT).date()
        if not item_end_str or item_end_str == 'N/A': i_end = i_start
        else: i_end = datetime.datetime.strptime(item_end_str, DATE_FMT).date()
        return (search_start <= i_end) and (search_end >= i_start)
    except:
        return True 

def submit_bid(load_id, amount, comment):
    user_name = st.session_state.user['name']
    # NEW: CONFIRMATION LOGIC FOR BID ADJUST
    
    if st.session_state.get('confirm_bid_adjust') == load_id:
        # User confirmed adjustment
        for l in st.session_state.loads_db:
            if l['id'] == load_id:
                existing_bid = next((b for b in l['Bids'] if b['Carrier'] == user_name), None)
                if existing_bid:
                    existing_bid['Amount'] = amount
                    existing_bid['Comment'] = comment
                    st.toast(f"✏️ Bid updated to ${amount}!")
        st.session_state.confirm_bid_adjust = None
        return

    # Check first
    found_existing = False
    for l in st.session_state.loads_db:
        if l['id'] == load_id:
            existing_bid = next((b for b in l['Bids'] if b['Carrier'] == user_name), None)
            if existing_bid:
                found_existing = True
                break
    
    if found_existing:
        if st.session_state.skip_bid_confirm:
             # Skip logic, just update
             st.session_state.confirm_bid_adjust = load_id # Hack to reuse logic
             submit_bid(load_id, amount, comment) # Recurse once
        else:
             st.warning("You already have a bid. Update it?")
             c_yes, c_no = st.columns(2)
             if c_yes.button("Yes, Update", key=f"yes_bid_{load_id}"):
                 st.session_state.confirm_bid_adjust = load_id
                 st.rerun()
             if c_no.button("Cancel", key=f"no_bid_{load_id}"):
                 st.session_state.confirm_bid_adjust = None
                 st.rerun()
             
             if st.checkbox("Don't ask me again", key=f"da_bid_{load_id}"):
                 st.session_state.skip_bid_confirm = True
    else:
        # New bid
        for l in st.session_state.loads_db:
            if l['id'] == load_id:
                l['Bids'].append({
                    "Carrier": user_name, 
                    "Amount": amount,
                    "Comment": comment
                })
                st.toast(f"📨 Offer Sent!")

def reset_search_criteria(prefixes):
    for p in prefixes:
        st.session_state[f"{p}_drop"] = QUICK_LIST[0]
        st.session_state[f"{p}_c"] = ""
        st.session_state[f"{p}_z"] = ""
    # Reset both latches
    if 'truck_search_active' in st.session_state:
        st.session_state.truck_search_active = False
    if 'load_search_active' in st.session_state:
        st.session_state.load_search_active = False

def render_docs_section(load):
    with st.expander(f"📂 Documents ({len(load.get('Docs', []))})"):
        if load.get('Docs'):
            for doc in load['Docs']:
                st.caption(f"{doc['date']} | {doc['user']}")
                st.write(f"📄 **{doc['name']}** ({doc['type']})")
                st.divider()
        else:
            st.caption("No documents attached.")
        
        new_doc = st.file_uploader("Attach Document (BOL, Pulp, Photo)", key=f"doc_up_{load['id']}")
        if new_doc:
            if st.button("Save Attachment", key=f"save_doc_{load['id']}"):
                timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
                load['Docs'].append({
                    "name": new_doc.name,
                    "type": new_doc.type,
                    "date": timestamp,
                    "user": st.session_state.user['name']
                })
                st.toast("Document Saved!")
                time.sleep(1)
                st.rerun()

# --- CALLBACKS ---
def handle_swap(p1, p2):
    st.session_state[f"{p1}_drop"], st.session_state[f"{p2}_drop"] = st.session_state[f"{p2}_drop"], st.session_state[f"{p1}_drop"]
    st.session_state[f"{p1}_c"], st.session_state[f"{p2}_c"] = st.session_state[f"{p2}_c"], st.session_state[f"{p1}_c"]
    st.session_state[f"{p1}_z"], st.session_state[f"{p2}_z"] = st.session_state[f"{p2}_z"], st.session_state[f"{p1}_z"]

def get_status_badge(status):
    if status == "Open": return f"<span class='status-badge status-blue'>Open</span>"
    if status == "Booked": return f"<span class='status-badge status-orange'>Booked</span>"
    if status in ["Loading", "In Transit", "Unloading"]: return f"<span class='status-badge status-orange'>{status}</span>"
    if status == "Delayed": return f"<span class='status-badge status-orange' style='background-color:#fee2e2; color:#b91c1c;'>Delayed</span>"
    if status == "Delivered": return f"<span class='status-badge status-green'>Delivered</span>"
    if status == "Paid": return f"<span class='status-badge status-green'>Paid</span>"
    if status == "SentToAccounting": return f"<span class='status-badge status-purple'>Sent to Accounting</span>"
    return f"<span class='status-badge status-gray'>{status}</span>"

def generate_rate_con_text(load):
    dates = format_date_range(load.get('DateStart', 'N/A'), load.get('DateEnd', 'N/A'))
    return f"FRESH TRANSPORT AGREEMENT\nLoad: {load['id']}\nDates: {dates}\nTemp: {load['Temp']}F\nCommodity: {load['Commodity']}\nRate: ${load['Rate']}\nOrigin: {load['Origin City']}\nDest: {load['Dest City']}"

def book_load(load_id):
    for l in st.session_state.loads_db:
        if l['id'] == load_id:
            l['Status'] = "Booked"
            l['Carrier'] = st.session_state.user['name']
            l['NewBooking'] = True # NOTIFICATION FLAG
            st.toast(f"✅ Booked! Temp set to {l['Temp']}°F")
            time.sleep(1)
            st.rerun()

def accept_bid(load_id, bid):
    for l in st.session_state.loads_db:
        if l['id'] == load_id:
            l['Status'] = "Booked"
            l['Carrier'] = bid['Carrier']
            l['Rate'] = bid['Amount']
            l['Bids'] = []
            l['BidAccepted'] = True # NOTIFICATION FLAG
            st.success("Bid Accepted!")
            st.rerun()

# --- REPLY CALLBACK (V67: Auto-Clear) ---
def send_reply_callback(sender, from_user, key_name, context=None):
    msg_content = st.session_state[key_name]
    if not msg_content.strip():
        st.toast("⚠️ Cannot send empty message")
    else:
        # V71: Add Folder/Status info to message structure
        st.session_state.messages_db.append({
            "id": generate_code("MSG"),
            "To": sender, 
            "From": from_user,
            "Msg": msg_content, 
            "Time": datetime.datetime.now().strftime("%H:%M"),
            "Folder": "inbox", # Default for recipient (conceptually)
            "Status": "unread",
            "Context": context
        })
        # Note: The above appends to the global DB. 
        # For the sender, this is a "Sent" message. 
        # In a real app, we'd store a copy for sender and receiver. 
        # Here we filter by From/To dynamically.
        
        st.session_state.expanded_convo = sender
        st.session_state.reply_error = None
        st.session_state[key_name] = "" # Auto-clear
        st.toast("Reply Sent!")

def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12: return "Good Morning"
    elif hour < 18: return "Good Afternoon"
    else: return "Good Evening"

# =========================================================
#  PAGE FUNCTIONS
# =========================================================

def page_dashboard():
    u = st.session_state.user
    greeting = get_greeting()
    
    st.markdown(f"## 👋 {greeting}, {u['name']}")
    st.write("") 
    
    # --- ALERTS SECTION (NEW) ---
    alerts = []
    if u['role'] == "Shipper":
        for l in st.session_state.loads_db:
            if l['Shipper'] == u['name'] and l.get('NewBooking'):
                alerts.append({"type": "booking", "msg": f"Load {l['id']} booked by {l['Carrier']}!", "id": l['id']})
    else: # Carrier
        for l in st.session_state.loads_db:
            if l.get('Carrier') == u['name'] and l.get('BidAccepted'):
                alerts.append({"type": "accepted", "msg": f"Bid Accepted for Load {l['id']}!", "id": l['id']})
    
    if alerts:
        with st.container(border=True):
            st.subheader("🔔 Alerts")
            for a in alerts:
                c_a1, c_a2 = st.columns([4, 1])
                c_a1.success(a['msg'])
                if c_a2.button("Dismiss", key=f"dsm_{a['id']}"):
                    for l in st.session_state.loads_db:
                        if l['id'] == a['id']:
                            if a['type'] == 'booking': l['NewBooking'] = False
                            if a['type'] == 'accepted': l['BidAccepted'] = False
                    st.rerun()
        st.write("")

    if st.session_state.dash_prefs['show_metrics']:
        if u['role'] == "Carrier":
            my_loads = [l for l in st.session_state.loads_db if l.get('Carrier') == u['name']]
            pending_pay = sum([l['Rate'] for l in my_loads if l['Status'] in ["Booked", "Delivered", "Loading", "In Transit", "Unloading", "SentToAccounting"]])
            c1, c2, c3 = st.columns(3)
            c1.metric("Accounts Receivable", f"${pending_pay:,.2f}", "Owed")
            c2.metric("Active Loads", f"{len([l for l in my_loads if l['Status'] not in ['Paid', 'Delivered', 'SentToAccounting']])}", "In Transit")
            c3.metric("Avg Reefer Rate", "$3.45/mi", "+15 cents")
        else: 
            my_loads = [l for l in st.session_state.loads_db if l['Shipper'] == u['name']]
            # V64 FIX: Only count booked loads
            payable = sum([l['Rate'] for l in my_loads if l['Status'] not in ["Open", "Paid"]])
            
            # REVERTED BUTTONS - JUST METRICS
            c1, c2, c3 = st.columns(3)
            c1.metric("Accounts Payable", f"${payable:,.2f}", "Unpaid")
            c2.metric("Active Loads", f"{len([l for l in my_loads if l['Status'] == 'Booked'])}", "In Transit")
            c3.metric("Cold Capacity", "Tight", "High Demand")
    st.divider()

    col_main, col_feed = st.columns([2, 1])
    with col_main:
        if st.session_state.dash_prefs['show_actions']:
            st.subheader("⚡ Quick Actions")
            b1, b2, b3, b4 = st.columns(4)
            if u['role'] == "Carrier":
                if b1.button("Find Loads 🔍", type="primary", use_container_width=True): st.session_state.nav_selection = "Find Loads"; st.rerun()
                if b2.button("Inbox 📬", type="primary", use_container_width=True): st.session_state.nav_selection = "Inbox"; st.rerun()
                if b3.button("My Trucks 🚛", type="primary", use_container_width=True): st.session_state.nav_selection = "My Trucks"; st.rerun()
            else:
                if b1.button("Post Loads 📦", type="primary", use_container_width=True): st.session_state.nav_selection = "Post Load"; st.rerun()
                if b2.button("Find Reefers 🚚", type="primary", use_container_width=True): st.session_state.nav_selection = "Find Trucks"; st.rerun()
                if b3.button("Inbox 📬", type="primary", use_container_width=True): st.session_state.nav_selection = "Inbox"; st.rerun()
            st.write("")

        if st.session_state.dash_prefs['show_activity']:
            st.subheader("📅 Recent Activity")
            my_loads = [l for l in st.session_state.loads_db if (l.get('Carrier') == u['name'] if u['role'] == 'Carrier' else l['Shipper'] == u['name'])]
            visible_recent = [l for l in my_loads if l['Status'] != 'SentToAccounting']
            if not visible_recent: st.info("No recent activity found.")
            else:
                for l in visible_recent[-3:]:
                    ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                    with st.expander(f"{l['id']} • {l['Origin City']} ➝ {l['Dest City']}"):
                        st.caption(f"📅 {ldate}") 
                        st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                        shipper_name = st.session_state.users_db.get(l['Shipper'], {}).get('name', l['Shipper'])
                        st.write(f"**With:** {shipper_name}")
                        c1, c2 = st.columns(2)
                        c1.write(f"**Commodity:** {l['Commodity']}")
                        c1.write(f"**Temp:** {l['Temp']}")
                        c2.write(f"**Rate:** ${l['Rate']}")
                        c2.write(f"**Weight:** {l['Weight']:,} lbs")
                        if l.get('Comments'): st.info(l['Comments'])

    with col_feed:
        if st.session_state.dash_prefs['show_news']:
            st.subheader("📰 Market Insights")
            
            # NEWS UPDATE: Custom Inputs
            new_site = st.text_input("Add News Source", placeholder="e.g. freightwaves.com")
            if st.button("Add Source"):
                if new_site and len(st.session_state.news_sites) < 5:
                    st.session_state.news_sites.append(new_site)
                    st.toast("Source Added!")
            
            st.caption(f"Showing top articles from {len(st.session_state.news_sites)} sources.")
            
            # MOCK ARTICLE GENERATOR
            for i, site in enumerate(st.session_state.news_sites[:5]):
                st.markdown(f"""
                <div class='news-card'><b>📰 News from {html.escape(site)}</b><br>
                <small style='color:grey'>Market trends analysis and spot rate updates.</small></div>
                """, unsafe_allow_html=True)

# --- NEW: PROFILE PAGE ---
def page_profile():
    u = st.session_state.user
    st.markdown("## ✏️ Edit Profile")
    
    # Calculate Rating
    reviews = [r for r in st.session_state.reviews_db if r['To'] == u['name']]
    avg_rating = 0
    if reviews:
        avg_rating = sum([r['Stars'] for r in reviews]) / len(reviews)
    
    c_rating, c_info = st.columns([1, 3])
    with c_rating:
        st.metric("Reputation Score", f"{avg_rating:.1f} ⭐", f"{len(reviews)} Reviews")
        st.caption("Grades public after 3 months.")
        # FEATURE: Verification Badge
        if u.get('verified'):
            st.markdown("<span class='status-badge status-green'>✅ FMCSA Verified</span>", unsafe_allow_html=True)
        else:
            st.warning("Not Verified")
    
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
             st.info("Public Info (Locked)")
             st.text_input("Company", value=u['name'], disabled=True)
             if u['role'] == "Carrier":
                 st.text_input("MC#", value="123456", disabled=True)
        with c2:
             st.info("Contact Details (Editable)")
             new_contact = st.text_input("Contact Name", value=u.get('contact', ''))
             new_phone = st.text_input("Phone", value=u.get('phone', ''))
             new_email = st.text_input("Email", value=u.get('email', ''))
        
        st.markdown("---")
        # FEATURE: TRUST & SAFETY
        st.subheader("🛡️ Trust & Safety")
        c_ts1, c_ts2 = st.columns(2)
        with c_ts1:
            st.file_uploader("Upload ID / Driver's License", type=['png', 'jpg', 'pdf'])
        with c_ts2:
             st.write("Get verified to increase visibility and trust.")
             if st.button("Submit for Verification"):
                 st.toast("ID Submitted for Review!")

        st.markdown("---")
        # FEATURE: NOTIFICATION SETTINGS
        st.subheader("🔔 Notification Settings")
        c_n1, c_n2 = st.columns(2)
        c_n1.checkbox("SMS Alerts (New Loads)", value=True)
        c_n1.checkbox("SMS Alerts (Bid Updates)", value=True)
        c_n2.checkbox("Email Summaries", value=False)
        c_n2.text_input("Alert Mobile Number", value=u.get('phone', ''))

        st.markdown("---")
        new_pic = st.file_uploader("Upload New Profile Picture", type=['png', 'jpg'])
        
        if st.button("Save Profile", type="primary"):
            u['contact'] = new_contact
            u['phone'] = new_phone
            u['email'] = new_email
            if new_pic:
                u['profile_pic'] = new_pic
            
            if 'users_db' in st.session_state and st.session_state.username:
                 st.session_state.users_db[st.session_state.username] = u

            st.toast("Profile Updated!")
            time.sleep(1)
            st.rerun()
            
    if reviews:
        st.subheader("Recent Feedback")
        for r in reviews:
            with st.container(border=True):
                st.write(f"**{'⭐' * r['Stars']}** - {r['Date']}")
                st.write(f"\"{r['Comment']}\"")

# --- NEW: DIRECTORY PAGE (V73) ---
def page_directory():
    st.markdown("## 📖 Company Directory")
    search = st.text_input("Search Company Name or MC#")
    if search:
        found = False
        # Mock Search in USERS and CARRIER_DETAILS
        for uid, udata in USERS.items():
            if search.lower() in udata['name'].lower():
                found = True
                with st.container(border=True):
                    st.subheader(udata['name'])
                    st.caption(f"Role: {udata['role']}")
                    if udata['role'] == 'Carrier':
                         # Get details
                         details = CARRIER_DETAILS.get(udata['name'])
                         if not details: details = CARRIER_DETAILS.get("Cool Runnings Logistics") # Fallback for demo
                         
                         c1, c2 = st.columns(2)
                         c1.write(f"**MC:** {details.get('MC', 'N/A')}")
                         c1.write(f"**DOT:** {details.get('DOT', 'N/A')}")
                         c2.write(f"**Contact:** {details.get('Dispatcher', 'N/A')}")
                         c2.write(f"**Phone:** {details.get('Phone', 'N/A')}")
                         st.info(f"Insurance: {details.get('Insurance', 'N/A')}")
                    else:
                        st.write(f"**Contact:** {udata.get('contact', 'N/A')}")
                        st.write(f"**Phone:** {udata.get('phone', 'N/A')}")
        if not found:
            st.warning("No companies found.")

def page_inbox():
    st.markdown("## 📬 Message Center")
    u = st.session_state.user
    
    # 1. Define Tabs
    tab_inbox, tab_vip, tab_sent, tab_archive, tab_trash = st.tabs(["📥 Inbox", "⭐ VIP", "📤 Sent", "📦 Archive", "🗑️ Trash"])
    
    # 2. Filter Messages
    all_msgs = st.session_state.messages_db
    my_inbox = []
    my_vip = []
    my_sent = []
    my_archive = []
    my_trash = []
    
    for m in all_msgs:
        if 'Folder' not in m: m['Folder'] = 'inbox'
        if 'Status' not in m: m['Status'] = 'unread'
        if 'is_vip' not in m: m['is_vip'] = False
        
        # LOGIC
        if m['To'] == u['name'] or m['To'] == st.session_state.username:
            if m.get('deleted_by_receiver'):
                my_trash.append(m)
            elif m.get('archived_by_receiver'):
                my_archive.append(m)
            else:
                if m.get('is_vip'):
                    my_vip.append(m)
                my_inbox.append(m)
        
        elif m['From'] == u['name'] or m['From'] == st.session_state.username:
             my_sent.append(m)

    # 3. Render Tabs
    
    # INBOX TAB
    with tab_inbox:
        if not my_inbox:
            st.info("Inbox is empty.")
        else:
            for m in reversed(my_inbox): # Newest first
                c1, c2, c3 = st.columns([6, 2, 1])
                c1.markdown(f"**From:** {m['From']}")
                if m.get('is_vip'): c1.caption("⭐ VIP Contact")
                c1.write(m['Msg'])
                c2.caption(f"{m['Time']}")
                
                # Actions
                if c3.button("⭐", key=f"vip_{m['id']}", help="Mark as VIP"):
                    m['is_vip'] = not m['is_vip']
                    st.rerun()
                if c3.button("📦", key=f"arc_{m['id']}"):
                    m['archived_by_receiver'] = True
                    st.rerun()
                if c3.button("🗑️", key=f"del_{m['id']}"):
                    m['deleted_by_receiver'] = True
                    st.rerun()
                
                # Quick Reply
                with st.expander("Reply"):
                    reply_key = f"rep_{m['id']}"
                    st.text_input("Message", key=reply_key)
                    # Pass message content as context
                    st.button("Send", key=f"s_{m['id']}", on_click=send_reply_callback, args=(m['From'], u['name'], reply_key, m['Msg']))
                
                st.divider()

    # VIP TAB
    with tab_vip:
        if not my_vip:
            st.info("No VIP messages.")
        else:
            for m in reversed(my_vip):
                st.markdown(f"**From:** {m['From']}")
                st.write(m['Msg'])
                st.caption(f"{m['Time']}")
                st.divider()

    # SENT TAB
    with tab_sent:
        if not my_sent:
            st.info("No sent messages.")
        else:
             for m in reversed(my_sent):
                st.markdown(f"**To:** {m['To']}")
                # SHOW CONTEXT IF AVAILABLE
                if m.get('Context'):
                    st.caption(f"Replying to: \"{m['Context']}\"")
                
                st.write(f"**You said:** {m['Msg']}")
                st.caption(f"Sent: {m['Time']}")
                
                # Reply Again Logic
                with st.expander("Reply Again"):
                    st.info(f"Replying to {m['To']}")
                    sent_reply_key = f"sent_rep_{m['id']}"
                    st.text_input("Message", key=sent_reply_key)
                    # Context for a follow up is your own previous message? Or their last one?
                    # Simplified: No context for "Reply Again" from sent folder for now
                    st.button("Send", key=f"btn_sent_rep_{m['id']}", on_click=send_reply_callback, args=(m['To'], u['name'], sent_reply_key, m['Msg']))
                st.divider()

    # ARCHIVE TAB
    with tab_archive:
        if not my_archive:
            st.write("No archived messages.")
        else:
            for m in reversed(my_archive):
                c1, c2 = st.columns([8,1])
                c1.write(f"**From:** {m['From']}")
                c1.write(m['Msg'])
                if c2.button("📥", help="Move back to Inbox", key=f"unarc_{m['id']}"):
                    m['archived_by_receiver'] = False
                    st.rerun()
                st.divider()

    # TRASH TAB
    with tab_trash:
        if st.button("Empty Trash", type="primary"):
            st.session_state.messages_db = [msg for msg in st.session_state.messages_db if not msg.get('deleted_by_receiver')]
            st.rerun()
            
        if not my_trash:
            st.write("Trash is empty.")
        else:
             for m in reversed(my_trash):
                c1, c2 = st.columns([8,1])
                c1.write(f"**From:** {m['From']}")
                c1.write(m['Msg'])
                if c2.button("♻️", help="Restore", key=f"rest_{m['id']}"):
                    m['deleted_by_receiver'] = False
                    st.rerun()
                st.divider()

def page_general_search():
    st.markdown("## 🔎 Global Search")
    u = st.session_state.user
    query = st.text_input("Enter keyword, Load ID, or Commodity").strip().lower()
    
    # Minimum Character Check
    if len(query) < 2 and query != "":
        st.warning("Please enter at least 2 characters to search.")
        return

    if query:
        st.divider()
        found = False
        
        # 1. Commodity Intel (Both)
        matched_commodities = []
        for name, data in COMMODITIES_DB.items():
            # EXACT SEARCH FIX: Check if query matches start of any word
            keywords = name.lower().split()
            if any(k.startswith(query) for k in keywords):
                matched_commodities.append((name, data))
        
        if matched_commodities:
            found = True
            st.markdown(f"### 🥦 Commodity Intelligence ({len(matched_commodities)})")
            for name, data in matched_commodities:
                with st.container(border=True):
                    st.subheader(f"❄️ {name}")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Set Point", data['Temp'])
                    c2.metric("Market Price", f"${data['MktPrice']}/lb", "Avg Spot")
                    c3.metric("Volume", data['Vol'])
                    c4.metric("Sensitivity", "High" if "High" in data['Sens'] else "Med")
                    st.info(f"**Handling Notes:** {data['Notes']}")
                    st.divider()

        # 2. Load Results (Shipper Only) - V62 FIX
        if u['role'] == "Shipper":
            results = []
            for l in st.session_state.loads_db:
                carrier_user = l.get('Carrier', '')
                c_data = st.session_state.users_db.get(carrier_user, {})
                carrier_name = c_data.get('name', carrier_user)
                ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                search_str = f"{l['id']} {ldate} {l['Origin City']} {l['Dest City']} {carrier_name} {l['Commodity']} {l['Status']}".lower()
                if query in search_str: results.append(l)
            
            if results:
                found = True
                st.markdown(f"### 📦 Produce Loads ({len(results)})")
                for l in results:
                    ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                    with st.expander(f"📦 {ldate} • {l['Origin City']} ➝ {l['Dest City']} ({l['id']})", expanded=False):
                        c1, c2, c3 = st.columns(3)
                        c1.markdown("#### Cargo")
                        c1.write(f"**Commodity:** {l['Commodity']}")
                        c1.write(f"**Temp:** {l['Temp']}")
                        c1.write(f"**Weight:** {l['Weight']:,} lbs")
                        c2.markdown("#### Logistics")
                        c2.write(f"**Rate:** ${l['Rate']}")
                        c2.write(f"**Status:** {l['Status']}")
                        if l.get('TeamReq'): c2.error("🚛 Team Drivers Required")
                        if l.get('ETracks'): c2.warning("⚠️ E-Tracks Required")
                        c3.markdown("#### Participants & Info")
                        s_name = st.session_state.users_db.get(l['Shipper'], {}).get('name', l['Shipper'])
                        c_name = st.session_state.users_db.get(l.get('Carrier'), {}).get('name', 'Not Assigned')
                        c3.write(f"**Shipper:** {s_name}")
                        c3.write(f"**Carrier:** {c_name}")
                        if l.get('Comments'): st.info(f"📝 **Notes:** {l['Comments']}")
                        render_docs_section(l)

        if not found: st.warning("No results found.")

def page_find_loads():
    st.markdown("## 🔍 Find Loads")
    
    found = []
    
    col_ui_1, col_ui_2 = st.columns([6, 1])
    with col_ui_1:
        with st.container(border=True):
            st.markdown("#### Lane Criteria")
            c1, c2, c3 = st.columns([10, 1, 10])
            with c1: 
                st.caption("📍 Pick Up")
                oc, oz = render_location_input("Origin", "so")
            with c2:
                st.write("")
                st.write("")
                st.button("⇄", on_click=handle_swap, args=("so", "sd"))
            with c3: 
                st.caption("🏁 Drop Off")
                dc, dz = render_location_input("Dest", "sd", allow_anywhere=True)
            st.write("")
            c_eq, c_rad = st.columns(2)
            st.info("❄️ Searching Refrigerated Loads Only")
            rad = c_rad.selectbox("Radius (mi)", [50, 100, 150, 200, 250, 300], index=2)
            st.write("")
            search_dates = st.date_input("Filter by Pickup Window (Required)", value=[datetime.date.today(), datetime.date.today()], min_value=datetime.date.today(), format="MM/DD/YYYY")
            team_only = st.checkbox("Search for Team Loads")
            st.write("")
            if st.button("Search Loads", type="primary", use_container_width=True):
                st.session_state.load_search_active = True

    with col_ui_2:
        st.write("")
        st.write("")
        st.write("")
        st.button("🔄 Reset", on_click=reset_search_criteria, args=(['so', 'sd'],), type="secondary")

    map_points = []
    if st.session_state.load_search_active:
        # DESTINATION REQUIRED CHECK
        if not oc: st.error("⚠️ **Origin** is required.")
        elif not dc: st.error("⚠️ **Destination** is required.")
        elif not search_dates: st.error("⚠️ **Date Window** is required.")
        else:
            for l in st.session_state.loads_db:
                if l['Status'] != "Open": continue
                
                # ORIGIN FILTER
                do = get_dist_zips(oz, l['Origin Zip'])
                if do > rad: continue
                
                # DESTINATION FILTER (Skip if "Anywhere")
                if dc != "Anywhere":
                    if l['Dest City'] != dc and get_dist_zips(dz, l['Dest Zip']) > rad:
                        continue

                if len(search_dates) == 2:
                    s_start = search_dates[0]
                    s_end = search_dates[1]
                    l_s_str = l.get('DateStart', 'N/A')
                    l_e_str = l.get('DateEnd', 'N/A')
                    if not check_overlap(s_start, s_end, l_s_str, l_e_str): continue
                elif len(search_dates) == 1:
                    s_start = s_end = search_dates[0]
                    l_s_str = l.get('DateStart', 'N/A')
                    l_e_str = l.get('DateEnd', 'N/A')
                    if not check_overlap(s_start, s_end, l_s_str, l_e_str): continue

                l['DH'] = int(do)
                if team_only and l.get('TeamReq'):
                    found.insert(0, l)
                else:
                    found.append(l)
                
                coord = get_coords(l['Origin Zip'])
                map_points.append({"lat": coord['lat'], "lon": coord['lon']})

            if found:
                st.success(f"Found {len(found)} results.")
                for l in found:
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                        with c1:
                            ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                            st.markdown(f"**{ldate}** • **{l['Origin City']}** ➝ **{l['Dest City']}**")
                            wt = l.get('Weight', 40000)
                            st.caption(f"**{l['id']}** • DH: {l['DH']}mi • {wt:,} lbs • **{l['Commodity']}**")
                            st.markdown(f"<span class='tag tag-temp'>🌡️ {html.escape(str(l['Temp']))}</span>", unsafe_allow_html=True)
                            if l.get('TeamReq'): st.error("🚛 Team Required")
                            if l.get('Comments'): st.caption(f"📝 {l['Comments']}")
                        with c2: st.markdown(f"#### ${l['Rate']}")
                        with c3:
                            if l['BookNow']: st.info("⚡ Instant")
                            else: st.warning("📞 Call")
                        with c4:
                            # NEW: BID ADJUST LOGIC
                            user_has_bid = any(b['Carrier'] == st.session_state.user['name'] for b in l['Bids'])
                            
                            if l['BookNow']: 
                                agreed = st.checkbox("Agree to Terms", key=f"tos_{l['id']}")
                                if st.button("Book Now", key=f"bk_{l['id']}", disabled=not agreed): 
                                    book_load(l['id'])
                            with st.expander("Make Offer" if not user_has_bid else "Adjust Bid"):
                                bid_amt = st.number_input("Bid ($)", value=l['Rate'], key=f"bid_val_{l['id']}")
                                bid_comment = st.text_input("Comment (Max 50 words)", max_chars=300, key=f"bid_com_{l['id']}")
                                if st.button("Submit Bid" if not user_has_bid else "Update Bid", key=f"sub_bid_{l['id']}"):
                                    submit_bid(l['id'], bid_amt, bid_comment)
                        
                        # NEW: Shipper Contact Info
                        with st.expander("📞 Shipper Contact Info"):
                            # FIX: Fallback logic for demo user "ship_pro"
                            shipper_data = USERS.get(l['Shipper'], {})
                            if not shipper_data and l['Shipper'] == "ship_pro": 
                                shipper_data = USERS['ship_pro']
                                
                            st.write(f"**Company:** {shipper_data.get('name', l['Shipper'])}")
                            st.write(f"**Phone:** {shipper_data.get('phone', 'N/A')}")
                            st.write(f"**Email:** {shipper_data.get('email', 'N/A')}")

            else: st.warning("No loads match criteria.")
            
            if map_points:
                st.markdown("### 🗺️ Live Map View")
                st.map(pd.DataFrame(map_points), size=20, color='#059669', use_container_width=True)

def page_post_truck():
    st.markdown("## 📢 Post Capacity")
    
    # RESET LATCH CHECK
    if st.session_state.get('reset_truck_form'):
        st.session_state['pto_drop'] = QUICK_LIST[0]
        st.session_state['ptd_drop'] = QUICK_LIST[0]
        st.session_state['pto_c'] = ""
        st.session_state['pto_z'] = ""
        st.session_state['ptd_c'] = ""
        st.session_state['ptd_z'] = ""
        st.session_state['pt_weight'] = 44000
        st.session_state['pt_rate'] = 3.00
        st.session_state['pt_notes'] = ""
        st.session_state['reset_truck_form'] = False

    with st.container(border=True):
        c1, c2, c3 = st.columns([10, 1, 10])
        with c1: st.caption("Empty Location"); oc, oz = render_location_input("Empty", "pto")
        with c2:
            st.write("")
            st.write("")
            st.button("⇄", key="swap_pt", on_click=handle_swap, args=("pto", "ptd"))
        with c3: st.caption("Desired Destination"); dc, dz = render_location_input("Dest", "ptd")
        
        c4, c5 = st.columns(2)
        st.info("❄️ Equipment: 53' Refrigerated Trailer (Default)")
        weight = c5.number_input("Max Wt", 44000, key="pt_weight")
        truck_dates = st.date_input("Availability Window", [datetime.date.today(), datetime.date.today()], min_value=datetime.date.today(), format="MM/DD/YYYY")
        c6, c7 = st.columns(2)
        rate_type = c6.selectbox("Rate Type", ["Flat Rate ($)", "RPM ($/mi)"])
        default_rate = 3.00 if "RPM" in rate_type else 2000.0
        rt = c7.number_input("Amount", value=default_rate, key="pt_rate")
        team_truck = st.checkbox("Team Truck Available", value=False)
        # V63 ADDITION
        empty_now = st.checkbox("Empty Now", value=False)
        comments = st.text_area("Driver Notes / Preferences", placeholder="e.g. Looking for backhaul...", key="pt_notes")
        
        if st.button("Post Truck", type="primary", use_container_width=True):
            if not oc: st.error("⚠️ Origin required")
            else:
                if len(truck_dates) == 2: s_date, e_date = truck_dates
                else: s_date = e_date = truck_dates[0]
                st.session_state.trucks_db.append({
                    "id": generate_code("T"), "Origin City": oc, "Origin Zip": oz, 
                    "Dest City": dc, "Dest Zip": dz, "Equip": "Reefer", "Weight": weight, 
                    "Rate": rt, "RateType": "RPM" if "RPM" in rate_type else "FLAT",
                    "Carrier": st.session_state.user['name'], "Comments": comments,
                    "TeamTruck": team_truck,
                    "EmptyNow": empty_now,
                    "DateStart": s_date.strftime(DATE_FMT), "DateEnd": e_date.strftime(DATE_FMT)
                })
                st.success("Truck Posted!")
                st.session_state['reset_truck_form'] = True
                time.sleep(1)
                st.rerun()

def page_my_trucks():
    st.markdown("## 🚛 Fleet Management")
    # NEW TAB: ACTIVE BIDS
    tab_posted, tab_bids, tab_active, tab_history = st.tabs(["📢 Posted Trucks", "💸 Active Bids", "🚚 Active Loads", "✅ Load History"])
    all_loads = [l for l in st.session_state.loads_db if l.get('Carrier') == st.session_state.user['name']]
    
    with tab_posted:
        my_trucks = [t for t in st.session_state.trucks_db if t['Carrier'] == st.session_state.user['name']]
        if not my_trucks: st.info("No trucks posted.")
        else:
            for t in my_trucks:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1: 
                        t_date = format_date_range(t.get('DateStart', 'N/A'), t.get('DateEnd', 'N/A'))
                        st.write(f"**{t_date}** • **{t['Origin City']}** ➝ **{t['Dest City'] or 'Anywhere'}**")
                        rtype = t.get('RateType', 'FLAT')
                        unit = "/mi" if rtype == "RPM" else ""
                        eq = t.get('Equip', 'Reefer')
                        st.caption(f"**{t['id']}** • {eq} • {t['Rate']}{unit}")
                        if t.get('Comments'): st.caption(f"📝 {t['Comments']}")
                    with c2: 
                        val_step = 0.10 if t.get('RateType', 'RPM') == 'RPM' else 50.0
                        new_val = st.number_input("Rate", value=float(t['Rate']), step=val_step, key=f"er_{t['id']}")
                        if new_val != t['Rate']:
                            if st.session_state.skip_confirm:
                                t['Rate'] = new_val
                                st.rerun()
                            else:
                                st.warning(f"Update to ${new_val}?")
                                col_y, col_n = st.columns(2)
                                dont = col_y.checkbox("Don't ask again", key=f"da_t_{t['id']}")
                                if col_y.button("Confirm", key=f"yes_t_{t['id']}"):
                                    if dont: st.session_state.skip_confirm = True
                                    t['Rate'] = new_val
                                    st.rerun()
                    with c3:
                        if st.button("Cancel", key=f"del_trk_{t['id']}"):
                            st.session_state.trucks_db.remove(t)
                            st.rerun()

    # ACTIVE BIDS TAB (NEW)
    with tab_bids:
        # LOGIC: Check for "Lost" bids (Booked by other)
        lost_bids = []
        for l in st.session_state.loads_db:
             if l['Status'] != 'Open' and l.get('Carrier') != st.session_state.user['name']:
                 my_bid = next((b for b in l['Bids'] if b['Carrier'] == st.session_state.user['name']), None)
                 if my_bid:
                     lost_bids.append((l, my_bid))
        
        # Process Lost Bids
        for l, bid in lost_bids:
             l['Bids'].remove(bid)
             st.session_state.messages_db.append({
                "id": generate_code("MSG"),
                "To": st.session_state.user['name'], "From": "System",
                "Msg": f"Your bid on Load {l['id']} was not selected. The load has been booked.", 
                "Time": datetime.datetime.now().strftime("%H:%M"),
                "Folder": "inbox", "Status": "unread"
             })
        
        # Display Active Bids
        active_bids = []
        for l in st.session_state.loads_db:
            if l['Status'] == 'Open':
                my_bid = next((b for b in l['Bids'] if b['Carrier'] == st.session_state.user['name']), None)
                if my_bid:
                    active_bids.append((l, my_bid))
        
        if not active_bids:
            st.info("No active bids placed.")
        else:
            for load, bid in active_bids:
                with st.container(border=True):
                    # Show full details
                    ldate = format_date_range(load.get('DateStart', 'N/A'), load.get('DateEnd', 'N/A'))
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{load['Origin City']}** ➝ **{load['Dest City']}**")
                        st.caption(f"Load: {load['id']} | Dates: {ldate}")
                        st.write(f"**Commodity:** {load['Commodity']}")
                        st.write(f"**Temp:** {load['Temp']}")
                        st.write(f"**My Bid:** ${bid['Amount']}")
                    with c2:
                        st.info("Pending")
                        if st.button("Cancel Bid", key=f"cancel_bid_{load['id']}"):
                             load['Bids'].remove(bid)
                             st.toast("Bid Cancelled")
                             st.rerun()

    with tab_active:
        c_sort1, c_sort2, c_filter = st.columns(3)
        sort_by = c_sort1.selectbox("Sort By", ["Loading Date", "Delivery Date", "Load ID"], key="sort_mt")
        order = c_sort2.radio("Order", ["Ascending", "Descending"], horizontal=True, key="order_mt")
        status_filter = c_filter.multiselect("Filter Status", ["Booked", "Loading", "In Transit", "Unloading", "Delayed"], default=[])

        active_loads = [l for l in all_loads if l['Status'] in ["Booked", "Loading", "In Transit", "Unloading", "Delayed"]]
        if status_filter: active_loads = [l for l in active_loads if l['Status'] in status_filter]
        reverse = True if order == "Descending" else False
        if sort_by == "Load ID": active_loads.sort(key=lambda x: x['id'], reverse=reverse)
        elif sort_by == "Delivery Date": active_loads.sort(key=lambda x: x.get('DateEnd', ''), reverse=reverse)
        else: active_loads.sort(key=lambda x: x.get('DateStart', ''), reverse=reverse)

        if not active_loads: st.info("No trucks currently dispatched.")
        else:
            for l in active_loads:
                # COMPACT UI
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                    c1.write(f"**{l['Origin City']}** ➝ **{l['Dest City']}**")
                    c1.caption(f"{l['id']} • {ldate}")
                    c2.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    
                    with st.expander("📦 Load Details & Updates"):
                        d1, d2 = st.columns(2)
                        # CARRIER MY TRUCKS FIX: SHIPPER NAME LOOKUP
                        s_real_name = USERS.get(l['Shipper'], {'name': l['Shipper']})['name']
                        d1.write(f"🏢 **Shipper:** {s_real_name}")
                        # Phone logic (mock)
                        s_phone = USERS.get(l['Shipper'], {}).get('phone', 'N/A')
                        d1.write(f"📞 {s_phone}")
                        d2.write(f"📦 {l['Commodity']} ({l['Weight']:,} lbs)")
                        d2.write(f"🌡️ {l['Temp']}")
                        d2.write(f"**Rate:** ${l['Rate']}")
                        
                        st.markdown("---")
                        
                        # STATUS UPDATE
                        new_status = st.selectbox("Update Status", ["Booked", "Loading", "In Transit", "Unloading", "Delivered", "Delayed"], key=f"stat_sel_{l['id']}", index=0)
                        status_note = st.text_input("Note", key=f"sn_{l['id']}")
                        if st.button("Update", key=f"conf_s_{l['id']}"):
                            l['Status'] = new_status
                            if status_note:
                                timestamp = datetime.datetime.now().strftime("%m/%d %H:%M")
                                if 'StatusLog' not in l: l['StatusLog'] = []
                                l['StatusLog'].append({'time': timestamp, 'status': new_status, 'note': status_note})
                                l['LatestStatusNote'] = status_note
                            
                            # FEATURE: CARRIER PRE-COOL CHECK
                            if new_status == "Loading":
                                st.session_state.pulp_log.append({
                                    "Time": datetime.datetime.now().strftime(DATE_FMT + " %H:%M"),
                                    "Product": "Pre-Cool Check",
                                    "Temp": f"Set Point Check",
                                    "LoadID": l['id'],
                                    "Photo_Data": None
                                })
                                st.toast("Status updated. Please log Pre-Cool Temp in Tools.")

                            st.toast(f"Status updated to: {new_status}")
                            time.sleep(1)
                            st.rerun()
                        
                        # NOTE HISTORY
                        if l.get('LatestStatusNote'): st.info(f"🚚 **Latest Note:** {l['LatestStatusNote']}")
                        if l.get('StatusLog'):
                            with st.expander("📜 View Note History"):
                                for entry in reversed(l['StatusLog']):
                                    st.write(f"**{entry['time']}** - {entry['note']}")
                        
                        render_docs_section(l)

                    # REVIEW POP-UP (Carrier Reviewing Shipper)
                    if l['Status'] == "Delivered" and not l.get('CarrierReviewed'):
                        st.divider()
                        st.warning("🌟 Please rate your experience with this Shipper")
                        with st.form(key=f"rev_form_c_{l['id']}"):
                            stars = st.slider("Rating", 1, 5, 5)
                            comment = st.text_input("Comment (Optional)")
                            if st.form_submit_button("Submit Review"):
                                st.session_state.reviews_db.append({
                                    "From": st.session_state.user['name'],
                                    "To": l['Shipper'],
                                    "Stars": stars,
                                    "Comment": comment,
                                    "Date": datetime.date.today().strftime("%Y-%m-%d")
                                })
                                l['CarrierReviewed'] = True
                                st.success("Review Submitted!")
                                time.sleep(1)
                                st.rerun()

    with tab_history:
        # Carrier Find Trucks Updates: Sort History & Undo Delivery
        c_sort1, c_sort2 = st.columns(2)
        sort_hist_by = c_sort1.selectbox("Sort History By", ["Loading Date", "Delivery Date", "Load ID", "Rate"], key="sort_h_mt")
        order_hist = c_sort2.radio("Order", ["Descending", "Ascending"], horizontal=True, key="order_h_mt")
        
        # HISTORY FILTER: NO PAID LOADS
        history = [l for l in all_loads if l['Status'] in ["Delivered", "SentToAccounting"]]
        
        # Sort Logic
        rev_hist = True if order_hist == "Descending" else False
        if sort_hist_by == "Load ID": history.sort(key=lambda x: x['id'], reverse=rev_hist)
        elif sort_hist_by == "Rate": history.sort(key=lambda x: x['Rate'], reverse=rev_hist)
        elif sort_hist_by == "Delivery Date": history.sort(key=lambda x: x.get('DateEnd', ''), reverse=rev_hist)
        else: history.sort(key=lambda x: x.get('DateStart', ''), reverse=rev_hist)

        if not history: st.info("No completed load history.")
        else:
            for l in history:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1: 
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.write(f"**{l['id']}** • **{l['Origin City']}** ➝ **{l['Dest City']}**")
                        st.caption(f"📅 {ldate}")
                        carrier_display = l.get('Carrier', 'Unknown')
                        st.caption(f"Carrier: **{carrier_display}**")
                    with c2: 
                        st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                        if l['Status'] == "Delivered":
                            if st.button("Undo Delivery", key=f"undo_{l['id']}", help="Move back to Active Loads"):
                                l['Status'] = "In Transit"
                                st.rerun()
                    with c3: st.write(f"**${l['Rate']}**")
                    render_docs_section(l)

def page_wallet():
    st.markdown("## 📊 Financial Ledger")
    u = st.session_state.user
    role = u['role']
    if role == "Carrier":
        st.info("ℹ️ Payments processed after POD + accessories upload.")
        my_loads = [l for l in st.session_state.loads_db if l.get('Carrier') == u['name']]
        
        # CARRIER WALLET UPDATE: Only show Delivered/SentToAccounting
        all_unpaid = [l for l in my_loads if l['Status'] in ["Delivered", "SentToAccounting"]]
        owed = sum([l['Rate'] for l in all_unpaid])
        paid = sum([l['Rate'] for l in my_loads if l['Status'] == 'Paid'])
        
        c1, c2 = st.columns(2)
        c1.metric("Outstanding Invoices", f"${owed:,.2f}")
        c2.metric("Total Paid (YTD)", f"${paid:,.2f}")
        st.divider()
        
        st.subheader("Invoice Management")
        
        # Wallet Updates: Sorting for Carrier
        c_sort1, c_sort2 = st.columns(2)
        sort_w_by = c_sort1.selectbox("Sort By", ["Date", "Load ID", "Rate"], key="sort_w")
        order_w = c_sort2.radio("Order", ["Descending", "Ascending"], horizontal=True, key="order_w")
        
        rev_w = True if order_w == "Descending" else False
        if sort_w_by == "Load ID": all_unpaid.sort(key=lambda x: x['id'], reverse=rev_w)
        elif sort_w_by == "Rate": all_unpaid.sort(key=lambda x: x['Rate'], reverse=rev_w)
        else: all_unpaid.sort(key=lambda x: x.get('DateEnd', ''), reverse=rev_w)

        if not all_unpaid: st.write("No active invoices on board.")
        with st.container(height=500, border=True):
            for job in all_unpaid:
                ldate = format_date_range(job.get('DateStart', 'N/A'), job.get('DateEnd', 'N/A'))
                shipper_name = USERS.get(job['Shipper'], {'name': job['Shipper']})['name']
                
                with st.expander(f"🧾 {job['id']} • {job['Origin City']} ➝ {job['Dest City']} • {shipper_name}"):
                    st.caption(f"📅 {ldate}")
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Commodity:** {job['Commodity']}")
                    c1.write(f"**Temp:** {job['Temp']}")
                    c1.write(f"**Weight:** {job['Weight']:,} lbs")
                    c2.write(f"**Shipper:** {shipper_name}")
                    # NEW: Show Rate & Truck Info
                    c2.write(f"**Rate:** ${job['Rate']}")
                    # Get Truck info if available
                    truck_info = CARRIER_DETAILS.get(u['name'], {}).get('Truck', 'N/A')
                    c2.write(f"**Truck:** {truck_info}")
                    
                    c2.markdown(get_status_badge(job['Status']), unsafe_allow_html=True)
                    
                    with c3:
                        render_docs_section(job)
                        if job['Status'] == "Booked":
                            # Carrier cannot invoice until marked Delivered in My Trucks
                            st.warning("Mark load as Delivered in 'My Trucks' to invoice.")
                        elif job['Status'] == "Delivered":
                            claim_flag = st.checkbox("🚩 Flag for Claim", key=f"claim_{job['id']}")
                            
                            # NEW: Confirmation Logic
                            if st.session_state.skip_acct_confirm:
                                if st.button("📤 Send to Accounting", key=f"acct_{job['id']}", disabled=claim_flag):
                                    job['Status'] = "SentToAccounting"
                                    st.toast("✅ Invoice forwarded to Accounting.")
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                if st.button("📤 Send to Accounting", key=f"pre_acct_{job['id']}", disabled=claim_flag):
                                    st.session_state.confirming_acct_id = job['id']
                                    st.rerun()
                            
                            if st.session_state.confirming_acct_id == job['id']:
                                st.warning("Are you sure? This cannot be undone.")
                                c_yes, c_no = st.columns(2)
                                if c_yes.button("Yes, Send", key=f"yes_acct_{job['id']}"):
                                    job['Status'] = "SentToAccounting"
                                    st.session_state.confirming_acct_id = None
                                    st.rerun()
                                if c_no.button("Cancel", key=f"no_acct_{job['id']}"):
                                    st.session_state.confirming_acct_id = None
                                    st.rerun()
                                
                                if st.checkbox("Don't ask me again for this session", key=f"da_acct_{job['id']}"):
                                    st.session_state.skip_acct_confirm = True
                            
                            # FEATURE: FACTORING
                            st.divider()
                            if st.button("⚡ Get Paid Now (Factoring)", key=f"factor_{job['id']}"):
                                st.toast("Request sent to Factoring Partner (3% fee).")

                        if claim_flag:
                             st.warning("Resolve claim before sending.")
                    elif job['Status'] == "SentToAccounting":
                        st.info("Awaiting Payment from Shipper.")
    else:
        st.info("ℹ️ Track freight spend.")
        my_loads = [l for l in st.session_state.loads_db if l['Shipper'] == u['name']]
        # SHIPPER WALLET UPDATE: Filter only Delivered/SentToAccounting (Not Paid)
        valid_status = ['Delivered', 'SentToAccounting']
        unpaid_loads = [l for l in my_loads if l['Status'] in valid_status]
        
        unpaid = sum([l['Rate'] for l in unpaid_loads])
        
        st.metric("Total Accounts Payable", f"${unpaid:,.2f}")
        
        # FEATURE: QUICKBOOKS
        if st.button("📥 Export to QuickBooks"):
            st.toast("Exporting CSV...")
        
        st.divider()
        
        # SHIPPER WALLET UPDATE: Search & Sort
        col_search, col_sort = st.columns(2)
        search_inv = col_search.text_input("Search Load #")
        sort_inv = col_sort.selectbox("Sort By", ["Loaded Date", "Rate", "Load ID"])
        
        # Apply Search
        if search_inv:
            unpaid_loads = [l for l in unpaid_loads if search_inv in l['id']]
            
        # Apply Sort
        if sort_inv == "Rate": unpaid_loads.sort(key=lambda x: x['Rate'], reverse=True)
        elif sort_inv == "Load ID": unpaid_loads.sort(key=lambda x: x['id'], reverse=True)
        else: unpaid_loads.sort(key=lambda x: x.get('DateStart', ''), reverse=True)

        st.subheader("Invoices Due")
        
        if not unpaid_loads: st.write("No invoices due.")
        
        # SHIPPER WALLET UPDATE: Scrollable Container
        with st.container(height=500, border=True):
            for l in unpaid_loads:
                carrier_display = USERS.get(l.get('Carrier'), {'name': 'Unknown'})['name']
                # SHIPPER WALLET: Show Range
                ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                with st.expander(f"🧾 {l['id']} • {l['Origin City']} ➝ {l['Dest City']} • {carrier_display}"):
                    st.caption(f"📅 {ldate}")
                    c1, c2 = st.columns(2)
                    # NEW: Expanded Details for Shipper
                    c1.write(f"**Load #:** {l['id']}")
                    c1.write(f"**Carrier:** {carrier_display}")
                    # Carrier Contact
                    c_details = CARRIER_DETAILS.get(l.get('Carrier'))
                    if not c_details: c_details = CARRIER_DETAILS.get("Cool Runnings Logistics")
                    if c_details:
                        c1.caption(f"📞 {c_details['Phone']} | 📧 {c_details['Email']}")
                    
                    c1.write(f"**Commodity:** {l['Commodity']}")
                    c1.write(f"**Dates:** {ldate}")
                    c1.write(f"**Rate:** ${l['Rate']}")
                    c2.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    render_docs_section(l)
                    
                    # NEW: Claim Flag & Logic
                    claim_flag = st.checkbox("🚩 Flag for Claim / Dispute", key=f"s_claim_{l['id']}")
                    
                    # LOGIC CLARIFICATION: "SentToAccounting" means Carrier sent it. Shipper needs to pay.
                    if l['Status'] == "Delivered" or l['Status'] == "SentToAccounting":
                        if st.button("📤 Send to AP Dept", key=f"mp_{l['id']}", disabled=claim_flag):
                            l['Status'] = "Paid"
                            st.toast("✅ Sent to AP for final processing.")
                            time.sleep(1)
                            st.rerun()
                    
                    if claim_flag:
                        st.error("Claim active. Payment frozen.")

def page_find_trucks():
    st.markdown("## 🚚 Find Capacity")
    
    col_ui_1, col_ui_2 = st.columns([6, 1])

    with col_ui_1:
        with st.container(border=True):
            c1, c2, c3 = st.columns([10, 1, 10]) 
            with c1: oc, oz = render_location_input("Origin", "fto") 
            with c2:
                st.write("")
                st.button("⇄", key="swap_ft", on_click=handle_swap, args=("fto", "ftd"))
            # SHIPPPER FIND TRUCKS: DESTINATION "ANYWHERE" SUPPORT + REQUIRED CHECK
            with c3: dc, dz = render_location_input("Dest", "ftd", allow_anywhere=True)
            
            rad = st.selectbox("Radius (mi)", [50, 100, 150, 200, 250, 300], index=2)
            st.write("")
            # UPDATED: Min date is today (Strict)
            search_dates = st.date_input("Filter by Availability (Required)", value=[datetime.date.today(), datetime.date.today()], min_value=datetime.date.today(), format="MM/DD/YYYY")
            
            # V63 FILTERS
            st.write("")
            prioritize_team = st.checkbox("Prioritize Team")
            prioritize_empty = st.checkbox("Prioritize Empty Now")
            
            st.write("")
            if st.button("Search Trucks", type="primary", use_container_width=True):
                st.session_state.truck_search_active = True
    
    with col_ui_2:
        st.write("")
        st.write("")
        st.write("")
        st.button("🔄 Reset", on_click=reset_search_criteria, args=(['fto', 'ftd'],), type="secondary")
            
    if st.session_state.truck_search_active: # V64 FIX: Strict Latch
        if not oc: st.error("Origin required.")
        elif not dc: st.error("Destination required.")
        elif not search_dates: st.error("Date Window required.") 
        else:
            found = []
            for t in st.session_state.trucks_db:
                if get_dist_zips(oz, t['Origin Zip']) > rad: continue
                
                # DESTINATION FILTER (Skip if "Anywhere")
                if dc != "Anywhere":
                    truck_dest_city = t.get('Dest City', '')
                    # If truck has specific dest and user has specific dest, must match
                    if truck_dest_city and truck_dest_city != dc:
                        continue

                if len(search_dates) == 2:
                    s_start = search_dates[0]
                    s_end = search_dates[1]
                    t_s_str = t.get('DateStart', 'N/A')
                    t_e_str = t.get('DateEnd', 'N/A')
                    if not check_overlap(s_start, s_end, t_s_str, t_e_str): continue
                elif len(search_dates) == 1:
                     s_start = s_end = search_dates[0]
                     t_s_str = t.get('DateStart', 'N/A')
                     t_e_str = t.get('DateEnd', 'N/A')
                     if not check_overlap(s_start, s_end, t_s_str, t_e_str): continue

                found.append(t)
            
            # SORTING V63
            found.sort(key=lambda x: (
                not (prioritize_empty and x.get('EmptyNow')),
                not (prioritize_team and x.get('TeamTruck'))
            ))

            if found:
                st.success(f"Found {len(found)} trucks.")
                for t in found:
                    # NEW COMPACT UI for SHIPPER FIND TRUCKS
                    with st.container(border=True):
                        # Row 1: Main Details (Dense)
                        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                        t_date = format_date_range(t.get('DateStart', 'N/A'), t.get('DateEnd', 'N/A'))
                        c1.markdown(f"**{t_date}**")
                        c1.caption(f"{t['Origin City']} ➝ {t.get('Dest City') or 'Anywhere'}")
                        
                        carrier_name = USERS.get(t['Carrier'], {'name': t['Carrier']})['name']
                        c2.write(f"**{carrier_name}**")
                        if t.get('TeamTruck'): c2.caption("🚛 Team")
                        
                        eq = t.get('Equip', 'Reefer')
                        rtype = t.get('RateType', 'FLAT')
                        unit = "/mi" if rtype == "RPM" else ""
                        c3.write(f"**${t['Rate']}{unit}**")
                        c3.caption(f"{eq}")

                        with c4:
                            # Contact Popover
                            with st.popover("📞 Contact"):
                                details = CARRIER_DETAILS.get(t['Carrier'])
                                if not details and t['Carrier'] in USERS:
                                    details = CARRIER_DETAILS.get(USERS[t['Carrier']]['name'])
                                if not details: details = CARRIER_DETAILS.get("Cool Runnings Logistics")
                                
                                if details:
                                    st.write(f"**MC#:** {details.get('MC', 'N/A')}")
                                    st.write(f"**Phone:** {details['Phone']}")
                                    st.write(f"**Email:** {details['Email']}")
                                    st.write(f"**Ins:** {details['Insurance']}")
                                    st.divider()
                                    
                                    # AUTO INQUIRY BUTTON
                                    if st.button("⚡ Is truck available?", key=f"auto_inq_st_{t['id']}"):
                                         msg_txt = f"Is your truck in {t['Origin City']} still available for {t_date}?"
                                         st.session_state.messages_db.append({
                                            "id": generate_code("MSG"),
                                            "To": t['Carrier'], "From": st.session_state.user['name'],
                                            "Msg": msg_txt, "Time": datetime.datetime.now().strftime("%H:%M"),
                                            "Folder": "inbox", "Status": "unread"
                                         })
                                         st.toast("📨 Sent!")
                                else:
                                    st.warning("No contact info.")
            else: st.warning("No trucks found matching criteria.")

# --- COLD CHAIN TOOLS (EXPANDED COMMODITIES) ---
def page_tools_shipper():
    st.markdown("## 🧰 Shipper Toolkit")
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Commodity Temp Search", "📡 National Freight Market", "📦 Incoterms", "❄️ Specs"])
    with tab1:
        st.subheader("Cold Chain Temperature Guide")
        st.caption("Search or select a commodity to view USDA recommended transport conditions.")
        search_choice = st.selectbox("Search Commodity", ["Select..."] + sorted(list(COMMODITIES_DB.keys())))
        if search_choice != "Select...":
            data = COMMODITIES_DB[search_choice]
            c1, c2, c3 = st.columns(3)
            c1.metric("Set Point", data['Temp'])
            c2.metric("Sensitivity", "See Notes", data['Sens'])
            st.info(f"**Handling Notes:** {data['Notes']}")
        else: st.info("👈 Select a commodity above to see requirements.")
    
    with tab2:
        st.subheader("National Freight Market Indicators")
        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Diesel (Nat'l)", "$3.85/gal", "-0.04")
        c2.metric("Load-to-Truck (Reefer)", "5.2 : 1", "+0.4")
        c3.metric("Tender Rejection Rate", "4.8%", "+0.2%")
        st.markdown("#### Spot vs Contract Rates (National Avg)")
        chart_data = pd.DataFrame(np.random.randn(20, 2) + [3.2, 2.8], columns=['Spot Rate', 'Contract Rate'])
        st.area_chart(chart_data)
        
    with tab3:
        st.markdown("### Incoterms Guide")
        term = st.selectbox("Select Term", ["EXW", "FCA", "CPT", "CIP", "DAP", "DPU", "DDP", "FAS", "FOB", "CFR", "CIF"])
        definitions = {
            "EXW": "Ex Works: Seller makes goods available at their premises. Buyer handles everything.",
            "FCA": "Free Carrier: Seller delivers goods to carrier at named place. Buyer handles main carriage.",
            "CPT": "Carriage Paid To: Seller pays for carriage to named destination. Risk transfers upon handing to carrier.",
            "CIP": "Carriage and Insurance Paid To: Seller pays for carriage and insurance to destination.",
            "DAP": "Delivered at Place: Seller delivers when goods are placed at disposal of buyer at named destination.",
            "DPU": "Delivered at Place Unloaded: Seller delivers and unloads at named place. Only term where seller unloads.",
            "DDP": "Delivered Duty Paid: Seller handles everything including import duties/taxes to buyer's door.",
            "FAS": "Free Alongside Ship: Seller places goods alongside the ship. Buyer handles loading and main carriage (Sea only).",
            "FOB": "Free On Board: Seller loads goods on board the ship. Risk transfers then (Sea only).",
            "CFR": "Cost and Freight: Seller pays costs and freight to destination port. Risk transfers on loading (Sea only).",
            "CIF": "Cost, Insurance and Freight: Seller pays costs, freight and insurance to destination port (Sea only)."
        }
        st.info(definitions.get(term, "Standard international trade term."))
    with tab4: 
        st.markdown("### Standard 53' Reefer Specs")
        st.markdown("""
        | Spec | Value |
        |---|---|
        | Internal Length | 52' 6" |
        | Internal Width | 97-98" |
        | Internal Height | 100-110" |
        | Door Height | 104" |
        | Max Payload | 43,000 - 44,000 lbs |
        | Pallets (48x40) | 26-28 Single, 52-56 Double |
        """)

def page_tools_driver():
    st.markdown("## 🧰 Driver Toolkit")
    t1, t2, t3, t4 = st.tabs(["💰 Profit Calculator", "📝 Pulp Check Log", "⛽ IFTA Calc", "📍 Smart Routing"])
    with t1:
        st.subheader("Profit Calculator")
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            rate = c1.number_input("Rate ($)", 2500)
            miles = c2.number_input("Miles", 600)
            fuel = c3.number_input("Fuel + Reefer Fuel ($)", 400)
            if st.button("Calc Profit"): st.metric("Net Profit", f"${rate - fuel}")
    with t2:
        st.subheader("Pulp Temperature Log")
        
        # Link to Load
        my_active = [l for l in st.session_state.loads_db if l.get('Carrier') == st.session_state.user['name'] and l['Status'] in ["Booked", "Loading", "In Transit"]]
        load_choice = st.selectbox("Link to Load (Optional)", ["None"] + [f"{l['id']} - {l['Commodity']}" for l in my_active])
        
        c1, c2 = st.columns(2)
        prod = st.text_input("Product", "Strawberries")
        # CARRIER TOOLS UPDATE: SINGLE TEMP INPUT
        temp_reading = st.number_input("Temperature (°F)", 34)
        
        pphoto = st.file_uploader("Upload Thermometer Photo", type=['png', 'jpg', 'jpeg'])

        if st.button("Save Record"):
            timestamp = datetime.datetime.now().strftime(DATE_FMT + " %H:%M")
            lid = "N/A"
            if load_choice != "None":
                lid = load_choice.split(" - ")[0]

            new_entry = {
                "Time": timestamp,
                "Product": prod,
                "Temp": f"{temp_reading}°F",
                "Photo_Data": pphoto,
                "LoadID": lid
            }
            st.session_state.pulp_log.append(new_entry)
            
            # Smart Save to Load Docs
            if lid != "N/A":
                for l in st.session_state.loads_db:
                    if l['id'] == lid:
                        l['Docs'].append({
                            "name": f"Pulp Check {timestamp}",
                            "type": "Pulp Log",
                            "date": timestamp,
                            "user": st.session_state.user['name']
                        })
            
            st.success("Record Saved!")
            time.sleep(1)
            st.rerun() # UPDATED V61: Auto Refresh
        
        if st.session_state.pulp_log:
            st.markdown("### 📋 History Log")
            c_filter1, c_filter2 = st.columns(2)
            pulp_filter = c_filter1.text_input("🔍 Search (Product/Temp)", placeholder="e.g. 34 or Strawberries")
            date_filter = c_filter2.date_input("📅 Filter by Date", value=[], format="MM/DD/YYYY")
            
            filtered_log = st.session_state.pulp_log
            if pulp_filter:
                filtered_log = [e for e in filtered_log if pulp_filter.lower() in e['Temp'].lower() or pulp_filter.lower() in e['Product'].lower()]
            if len(date_filter) == 2:
                s_date, e_date = date_filter
                valid_entries = []
                for e in filtered_log:
                    try:
                        date_str = e['Time'].split(' ')[0] 
                        entry_date = datetime.datetime.strptime(date_str, DATE_FMT).date()
                        if s_date <= entry_date <= e_date:
                            valid_entries.append(e)
                    except ValueError: continue
                filtered_log = valid_entries

            with st.container(height=400, border=True):
                if not filtered_log:
                    st.caption("No records found matching filter.")
                else:
                    for i, entry in enumerate(reversed(filtered_log)):
                        with st.container(border=True):
                            c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
                            c1.markdown(f"**🕒 {entry['Time']}**")
                            c2.markdown(f"📦 {entry['Product']}")
                            c3.markdown(f"🌡️ {entry['Temp']}")
                            # KEY ERROR FIX: Get LoadID safely
                            lid_val = entry.get('LoadID', 'N/A')
                            if lid_val != "N/A":
                                c3.caption(f"🔗 {lid_val}")
                            with c4:
                                if entry.get('Photo_Data'):
                                    with st.expander("✅ Uploaded"):
                                        st.image(entry['Photo_Data'], use_container_width=True)
                                else:
                                    st.caption("No Photo")

    with t3:
        st.subheader("IFTA Estimator")
        miles = st.number_input("Quarterly Miles", 25000)
        st.metric("Est. Tax Savings", f"${miles * 0.05:.2f}")
    with t4:
        st.subheader("Route Optimizer")
        st.info("Routing features coming soon.")

# --- PAGE: POST LOAD (COLD CHAIN) ---
def page_post_load():
    st.markdown("## 📦 Post Loads")
    
    # RESET LATCH CHECK (V62: Add reset logic)
    if st.session_state.get('reset_load_form'):
        st.session_state['plo_drop'] = QUICK_LIST[0]
        st.session_state['pld_drop'] = QUICK_LIST[0]
        st.session_state['plo_c'] = ""
        st.session_state['plo_z'] = ""
        st.session_state['pld_c'] = ""
        st.session_state['pld_z'] = ""
        st.session_state['pl_comm'] = "Fresh Produce"
        st.session_state['pl_min'] = 34
        st.session_state['pl_max'] = 36
        st.session_state['pl_weight'] = 40000
        st.session_state['pl_rate'] = 2500
        st.session_state['pl_notes'] = ""
        st.session_state['pl_appt_time'] = "" # Reset Time
        st.session_state['reset_load_form'] = False

    with st.container(border=True):
        c1, c2, c3 = st.columns([10, 1, 10])
        with c1: oc, oz = render_location_input("Origin", "plo")
        with c2:
            st.write("")
            st.button("⇄", key="swap_pl", on_click=handle_swap, args=("plo", "pld"))
        with c3: dc, dz = render_location_input("Dest", "pld")
        
        c4, c5, c6 = st.columns(3)
        comm = c4.text_input("Commodity", "Fresh Produce", key="pl_comm")
        # UPDATED: Temp Range
        c5a, c5b = c5.columns(2)
        temp_min = c5a.number_input("Min Temp", value=34, key="pl_min")
        temp_max = c5b.number_input("Max Temp", value=36, key="pl_max")
        
        weight = c6.number_input("Weight (lbs)", value=40000, key="pl_weight")
        
        # SHIPPER POST LOAD UPDATES:
        c_dates, c_opts = st.columns([2, 2])
        
        # 2. Checkboxes (Define first for logic flow)
        with c_opts:
            appt_type = st.radio("Appointment Type", ["Open / Flexible", "First Come First Serve (FCFS)", "Strict Appointment"], horizontal=True)

        # 1. Dates + Appt Time (Dependent on appt_type)
        with c_dates:
            # FIX: Only 2 columns logic for c_dates context
            cd1, cd2 = st.columns([2, 1])
            load_dates = cd1.date_input("Pickup Window", [datetime.date.today(), datetime.date.today()], min_value=datetime.date.today(), format="MM/DD/YYYY")
            
            with cd2:
                if appt_type == "Strict Appointment":
                    appt_time = st.text_input("Appt Time (00:00)", placeholder="14:00", key="pl_appt_time")
                else:
                    appt_time = ""
                    st.write("") # Spacer

        # UPDATED: Team Req UNDER E-Tracks
        st.write("")
        c9, c10 = st.columns(2)
        etracks = c9.checkbox("E-Tracks Required", value=False)
        team_req = c10.checkbox("Team Drivers Required", value=False)
        
        # NEW: Optional Book Now
        book_now = st.checkbox("Allow Instant Booking (Book Now)", value=True)
        # NEW: Private Network Checkbox
        private_network = st.checkbox("🔒 Post to Private Network (Trusted Carriers Only)", value=False)

        comments = st.text_area("Special Instructions", placeholder="e.g. Check in at Gate 3, Must have load bars...", key="pl_notes")
        
        if st.button("Post Load", type="primary", use_container_width=True):
            if not oc or not dc: st.error("⚠️ Origin & Dest required")
            elif rt <= 0: st.error("⚠️ Rate must be > $0")
            else:
                if len(load_dates) == 2: s_date, e_date = load_dates
                else: s_date = e_date = load_dates[0]
                
                # UPDATED V60: Continuous Temp
                temp_range_str = f"{temp_min}-{temp_max} (Continuous)"
                
                # Appt String Construction
                appt_str = ""
                if appt_type == "Strict Appointment" and appt_time:
                    appt_str = f"Strict: {appt_time}"
                elif appt_type == "First Come First Serve (FCFS)":
                    appt_str = "FCFS"
                
                final_comments = f"{appt_str} | {comments}" if appt_str else comments
                if private_network: final_comments = f"[PRIVATE POST] {final_comments}"
                
                st.session_state.loads_db.append({
                    "id": generate_code("L"), "Origin City": oc, "Origin Zip": oz, 
                    "Dest City": dc, "Dest Zip": dz, "Equip": "Reefer", "Weight": weight,
                    "Commodity": comm, "Temp": temp_range_str, 
                    "Rate": rt, "ETracks": etracks, "TeamReq": team_req, 
                    "Comments": final_comments,
                    "BookNow": book_now, "Status": "Open", 
                    "Shipper": st.session_state.user['name'], "Bids": [], "POD": False,
                    "Docs": [], 
                    "DateStart": s_date.strftime(DATE_FMT), "DateEnd": e_date.strftime(DATE_FMT)
                })
                st.success("Load Posted!")
                st.session_state['reset_load_form'] = True
                time.sleep(1)
                st.rerun() 

def page_my_loads():
    st.markdown("## 📋 Active Loads")
    tab_open, tab_active, tab_history = st.tabs(["📢 Open Posts", "🚚 In Transit", "✅ Load History"])
    all_loads = [l for l in st.session_state.loads_db if l['Shipper'] == st.session_state.user['name']]
    
    with tab_open:
        open_loads = [l for l in all_loads if l['Status'] == 'Open']
        if not open_loads: st.info("No open posts.")
        else:
            for l in open_loads:
                # SHIPPER MY LOADS UPDATE: Better Organization
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    with c1:
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.markdown(f"**{ldate}**")
                        st.write(f"{l['Origin City']} ➝ {l['Dest City']}")
                        st.caption(f"**{l['id']}**")
                    with c2:
                         st.write(f"**{l['Commodity']}**")
                         st.write(f"{l['Temp']}°F")
                    with c3:
                        new_rate = st.number_input(f"Rate ($)", value=int(l['Rate']), step=50, key=f"edit_load_{l['id']}")
                        if new_rate != l['Rate']:
                            if st.session_state.skip_confirm:
                                l['Rate'] = new_rate
                                st.rerun()
                            else:
                                st.warning(f"Update to ${new_rate}?")
                                col_y, col_n = st.columns(2)
                                dont = col_y.checkbox("Don't ask again", key=f"da_l_{l['id']}")
                                if col_y.button("Confirm", key=f"yes_l_{l['id']}"):
                                    if dont: st.session_state.skip_confirm = True
                                    l['Rate'] = new_rate
                                    st.rerun()
                    with c4:
                        if st.button("Cancel", key=f"del_{l['id']}"):
                            st.session_state.loads_db.remove(l)
                            st.rerun()
                    
                    if l.get('Comments'): 
                        st.info(f"📝 {l['Comments']}")

                if l['Bids']:
                    with st.expander(f"📬 {len(l['Bids'])} New Offer(s) Received", expanded=True):
                        for bid in l['Bids']:
                            with st.container(border=True):
                                bc1, bc2, bc3 = st.columns([2,1,1])
                                bc1.write(f"**{bid['Carrier']}** offered **${bid['Amount']}**")
                                if bid.get('Comment'):
                                    bc1.caption(f"💬 \"{bid['Comment']}\"")
                                
                                c_stats = CARRIER_DETAILS.get(bid['Carrier'])
                                if not c_stats and bid['Carrier'] in USERS: c_stats = CARRIER_DETAILS.get(USERS[bid['Carrier']]['name'])
                                if not c_stats: c_stats = CARRIER_DETAILS.get("Cool Runnings Logistics")
                                
                                bc2.caption(f"MC: {c_stats.get('MC', 'N/A')}")
                                bc2.caption(f"Ins: {c_stats.get('Insurance', 'N/A')}")

                                if bc3.button("Accept", key=f"acc_{l['id']}_{bid['Carrier']}"):
                                    accept_bid(l['id'], bid)

    with tab_active:
        c_filter, = st.columns(1)
        status_filter = c_filter.multiselect("Filter Status", ["Booked", "Loading", "In Transit", "Unloading", "Delayed"], default=[])
        
        active_loads = [l for l in all_loads if l['Status'] in ["Booked", "Loading", "In Transit", "Unloading", "Delayed"]]
        if status_filter:
            active_loads = [l for l in active_loads if l['Status'] in status_filter]

        if not active_loads: st.info("No loads in transit.")
        else:
            for l in active_loads:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    with c1:
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.markdown(f"**{ldate}** • **{l['Origin City']}** ➝ **{l['Dest City']}**")
                        st.caption(f"**{l['id']}** • {l['Commodity']} @ {l['Temp']}°F")
                        if l.get('Comments'): st.caption(f"📝 {l['Comments']}")
                    with c2: st.markdown(f"**${l['Rate']}**")
                    with c3: st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    with c4:
                        rc_text = generate_rate_con_text(l)
                        st.download_button("📄 Rate Con", data=rc_text, file_name=f"RateCon_{l['id']}.txt", key=f"src_{l['id']}")
                        st.write("")
                        if st.button("📲 Req. Tracking", key=f"trk_{l['id']}"):
                            st.toast("📲 Digital Tracking Request sent to Driver!")
                    if l.get('Carrier'):
                         with st.expander("🚛 View Carrier & Dispatch Info"):
                             details = CARRIER_DETAILS.get("Cool Runnings Logistics") 
                             if details:
                                 cd1, cd2 = st.columns(2)
                                 cd1.write(f"**Carrier:** {l['Carrier']}")
                                 cd1.write(f"**Dispatcher:** {details['Dispatcher']}")
                                 cd1.write(f"**Phone:** {details['Phone']}")
                                 cd2.write(f"**Driver:** {details['Driver']}")
                                 cd2.write(f"**Truck:** {details['Truck']}")
                                 st.info(f"Insurance: {details['Insurance']}")
                    # NEW: Live IoT Temp Simulation
                    if l['Status'] in ["Loading", "In Transit"]:
                         st.markdown(f"**❄️ Live IoT Temp:** `{random.randint(33, 35)}°F` (Updated: Just now)")
                    
                    if l.get('LatestStatusNote'): st.info(f"🚚 **Current Driver Note:** {l['LatestStatusNote']}")
                    if l.get('StatusLog'):
                        with st.expander("📜 View Past Status Notes"):
                            for entry in reversed(l['StatusLog']):
                                st.write(f"**{entry['time']} - {entry['status']}**: {entry['note']}")
                    # DOCS
                    render_docs_section(l)
                    
                    # REVIEW POP-UP (Shipper Reviewing Carrier)
                    if l['Status'] == "Delivered" and not l.get('ShipperReviewed'):
                        st.divider()
                        st.warning(f"🌟 Please rate your experience with {l.get('Carrier', 'the Carrier')}")
                        with st.form(key=f"rev_form_s_{l['id']}"):
                            stars = st.slider("Rating", 1, 5, 5)
                            comment = st.text_input("Comment (Optional)")
                            if st.form_submit_button("Submit Review"):
                                st.session_state.reviews_db.append({
                                    "From": st.session_state.user['name'],
                                    "To": l.get('Carrier'),
                                    "Stars": stars,
                                    "Comment": comment,
                                    "Date": datetime.date.today().strftime("%Y-%m-%d")
                                })
                                l['ShipperReviewed'] = True
                                st.success("Review Submitted!")
                                time.sleep(1)
                                st.rerun()

    with tab_history:
        # SHIPPER MY LOADS UPDATE: Remove "Paid" from history
        history = [l for l in all_loads if l['Status'] in ["Delivered", "SentToAccounting"]] # NOT PAID
        if not history: st.info("No completed load history.")
        else:
            for l in history:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1: 
                        # UPDATED: Add Load ID and Carrier
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.write(f"**{l['id']}** • **{l['Origin City']}** ➝ **{l['Dest City']}**")
                        st.caption(f"📅 {ldate}")
                        carrier_display = l.get('Carrier', 'Unknown')
                        st.caption(f"Carrier: **{carrier_display}**")
                    with c2: st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    with c3: st.write(f"**${l['Rate']}**")
                    render_docs_section(l)

# =========================================================
#  MAIN APP
# =========================================================
if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<br><br><h1 style='text-align: center;'>❄️ FreshChain</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                st.write("")
                if st.form_submit_button("Sign In", type="primary", use_container_width=True):
                    if u in USERS and USERS[u]['pass'] == p:
                        st.session_state.authenticated = True
                        st.session_state.user = USERS[u]
                        st.session_state.username = u 
                        st.session_state.nav_selection = "Dashboard"
                        st.balloons() # DOPAMINE RUSH
                        time.sleep(0.5) 
                        st.rerun()
                    else: st.error("Invalid Credentials")
            st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Demo: truck_guy | ship_pro (pass: 1234)")
else:
    u = st.session_state.user
    with st.sidebar:
        # PROFILE HEADER (Persistent from DB)
        current_u = st.session_state.users_db.get(st.session_state.username, u)
        
        c_p1, c_p2 = st.columns([1, 3])
        with c_p1:
            if current_u.get('profile_pic'):
                st.image(current_u['profile_pic'], use_container_width=True)
            else:
                st.markdown("## 👤")
        with c_p2:
            st.markdown(f"**{current_u['name']}**")
            if current_u['verified']: st.caption("✅ Verified Partner")
        
        st.divider()
        
        # STANDARD MENU WITH NOTIFICATION BADGE
        # V60: Calculate Badge Count
        msg_count = len([m for m in st.session_state.messages_db if (m['To'] == st.session_state.username or m['To'] == u['name']) and m.get('Status') == 'unread'])
        inbox_label = f"Inbox ({msg_count})" if msg_count > 0 else "Inbox"

        if u['role'] == "Carrier":
            options = ["Dashboard", "Find Loads", "Post Truck", "My Trucks", inbox_label, "Wallet", "Search", "Tools", "Profile"]
            # Map back for logic
            real_opts = ["Dashboard", "Find Loads", "Post Truck", "My Trucks", "Inbox", "Wallet", "Search", "Tools", "Profile"]
        else:
            options = ["Dashboard", "Post Load", "My Loads", "Find Trucks", inbox_label, "Wallet", "Search", "Tools", "Profile"]
            real_opts = ["Dashboard", "Post Load", "My Loads", "Find Trucks", "Inbox", "Wallet", "Search", "Tools", "Profile"]
            
        # Handle Navigation State
        if 'nav_selection' not in st.session_state: st.session_state.nav_selection = "Dashboard"
        
        # If selection is "Inbox", map it to the labeled version for the radio index
        current_index = 0
        if st.session_state.nav_selection in real_opts:
            current_index = real_opts.index(st.session_state.nav_selection)
        
        sel = st.radio("Menu", options, index=current_index)
        
        # Map selection back to simple key
        mapped_sel = real_opts[options.index(sel)]

        if mapped_sel != st.session_state.nav_selection:
            st.session_state.nav_selection = mapped_sel
            st.rerun()
        
        st.divider()
        if st.button("Log Out"): 
            st.session_state.authenticated = False
            st.rerun()
    
    # NAVIGATION ROUTER
    if st.session_state.nav_selection == "Dashboard": page_dashboard()
    elif st.session_state.nav_selection == "Find Loads": page_find_loads()
    elif st.session_state.nav_selection == "Post Truck": page_post_truck()
    elif st.session_state.nav_selection == "My Trucks": page_my_trucks()
    elif st.session_state.nav_selection == "Wallet": page_wallet()
    elif st.session_state.nav_selection == "Search": page_general_search()
    elif st.session_state.nav_selection == "Tools": 
        if u['role'] == "Carrier": page_tools_driver()
        else: page_tools_shipper()
    elif st.session_state.nav_selection == "Post Load": page_post_load()
    elif st.session_state.nav_selection == "My Loads": page_my_loads()
    elif st.session_state.nav_selection == "Find Trucks": page_find_trucks()
    elif st.session_state.nav_selection == "Inbox": page_inbox()
    elif st.session_state.nav_selection == "Profile": page_profile()
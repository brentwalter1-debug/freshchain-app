"""
FreshChain Cold Logistics Marketplace
Production Release V1.0
Features: Secure Authentication, SaaS Monetization, Role-Based Access Control, Load Board
"""

import streamlit as st
import pandas as pd
import numpy as np
import math
import random
import datetime
import time
import html
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="FreshChain | Premium Cold Logistics",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLING (SaaS Polish) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; } 
    
    div[data-testid="stVerticalBlock"] > div[style*="background-color"] {
        background-color: white; padding: 24px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); 
        border: 1px solid #e2e8f0; transition: transform 0.2s, box-shadow 0.2s;
    }
    div[data-testid="stVerticalBlock"] > div[style*="background-color"]:hover {
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }
    
    button[kind="primary"] {
        background-color: #059669 !important; border-color: #059669 !important;
        color: white !important; font-weight: 600 !important; border-radius: 8px !important;
        padding: 10px 24px !important; transition: all 0.2s !important;
    }
    button[kind="primary"]:hover {
        background-color: #047857 !important; transform: translateY(-1px);
    }
    
    button[kind="secondary"] {
        background-color: white !important; border: 1px solid #d1d5db !important;
        color: #374151 !important; font-weight: 500 !important; border-radius: 8px !important;
    }
    button[kind="secondary"]:hover {
        border-color: #9ca3af !important; color: #111827 !important; background-color: #f9fafb !important;
    }
    
    .pro-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    
    .status-badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block;}
    .status-green { background-color: #d1fae5; color: #065f46; }
    .status-blue { background-color: #dbeafe; color: #1e40af; }
    .status-orange { background-color: #ffedd5; color: #9a3412; }
    .status-gray { background-color: #f1f5f9; color: #475569; }
    .status-purple { background-color: #f3e8ff; color: #6b21a8; }
    
    .tag-temp { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold;}
    
    .news-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border-left: 4px solid #059669; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .auth-container { animation: slideUp 0.5s ease-out; max-width: 450px; margin: 0 auto; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ROBUST STATE MANAGEMENT ---
DATE_FMT = "%m/%d/%Y"

# Initialize explicit defaults to prevent TypeError crashes between strings and floats
WIDGET_DEFAULTS = {
    'pl_min': 34, 'pl_max': 36, 'pl_weight': 40000, 'pl_rate': 2500,
    'pt_weight': 44000, 'pt_rate': 3.0, 'pl_notes': "", 'pt_notes': "",
    'pl_comm': "Fresh Produce", 'pl_appt_time': "", 'so_c': "", 'so_z': "",
    'sd_c': "", 'sd_z': "", 'fto_c': "", 'fto_z': "", 'ftd_c': "", 'ftd_z': "",
    'pto_c': "", 'pto_z': "", 'ptd_c': "", 'ptd_z': "", 'plo_c': "", 'plo_z': "",
    'pld_c': "", 'pld_z': ""
}

CORE_STATES = {
    'authenticated': False, 'user': None, 'username': None,
    'users_db': {}, 'loads_db': [], 'trucks_db': [], 'messages_db': [], 'reviews_db': [],
    'pulp_log': [], 'dash_prefs': {'show_metrics': True, 'show_actions': True, 'show_activity': True, 'show_news': True},
    'news_sites': ["FreightWaves", "Produce Blue Book"], 'skip_confirm': False,
    'skip_acct_confirm': False, 'skip_bid_confirm': False, 'confirm_bid_adjust': None,
    'truck_search_active': False, 'load_search_active': False, 'confirming_acct_id': None
}

for k, v in CORE_STATES.items():
    if k not in st.session_state:
        st.session_state[k] = v

for k, v in WIDGET_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

QUICK_LIST = ["Select from List...", "Salinas, CA (939)", "Yuma, AZ (853)", "McAllen, TX (785)", "Nogales, AZ (856)", "Miami, FL (331)", "Chicago, IL (606)", "Bronx, NY (104)", "Atlanta, GA (303)", "Philadelphia, PA (191)"]
ANYWHERE_LIST = ["Select...", "Anywhere", "Salinas, CA (939)", "Yuma, AZ (853)", "McAllen, TX (785)", "Nogales, AZ (856)", "Miami, FL (331)", "Chicago, IL (606)", "Bronx, NY (104)", "Atlanta, GA (303)", "Philadelphia, PA (191)"]

for k in ['so_drop', 'sd_drop', 'fto_drop', 'ftd_drop', 'pto_drop', 'ptd_drop', 'plo_drop', 'pld_drop']:
    if k not in st.session_state:
        st.session_state[k] = QUICK_LIST[0]

# --- 4. DATABASES & HELPERS ---
ZIP_MAP = { "93": {"lat": 36.6, "lon": -121.6}, "85": {"lat": 32.6, "lon": -114.6}, "78": {"lat": 26.2, "lon": -98.2}, "33": {"lat": 25.7, "lon": -80.2}, "60": {"lat": 41.8, "lon": -87.6}, "10": {"lat": 40.8, "lon": -73.8}, "30": {"lat": 33.7, "lon": -84.4}, "19": {"lat": 39.9, "lon": -75.1} }

if not st.session_state.users_db:
    # Seed mock accounts using secure hashes
    st.session_state.users_db = {
        "ship_pro": {"pass": generate_password_hash("1234"), "role": "Shipper", "name": "GreenValley Growers", "tier": "Pro", "stars": 4.9, "verified": True, "contact": "Shipping Dept", "phone": "555-0101", "email": "shipping@greenvalley.com", "profile_pic": None},
        "truck_guy": {"pass": generate_password_hash("1234"), "role": "Carrier", "name": "Cool Runnings Logistics", "tier": "Free", "stars": 4.8, "verified": True, "contact": "Jamal Davis", "phone": "555-0202", "email": "dispatch@coolrunnings.com", "profile_pic": None},
    }

CARRIER_DETAILS = {
    "Cool Runnings Logistics": {
        "MC": "123456", "DOT": "9876542", "Dispatcher": "Jamal Davis", "Phone": "(555) 019-2834",
        "Email": "dispatch@coolrunnings.com", "Driver": "Marcus Miller", "Cell": "(555) 992-1102",
        "Truck": "#104 (Kenworth T680)", "Trailer": "#5302 (ThermoKing)", "Insurance": "Active ($1M Liability / $100k Cargo)"
    }
}

COMMODITIES_DB = {
    "Apples": {"Temp": "32-34°F", "Sens": "High (Ethylene Sensitive)", "Notes": "Keep away from onions/carrots.", "MktPrice": 1.20, "Vol": "High"},
    "Apricots": {"Temp": "32-34°F", "Sens": "High", "Notes": "Handle gently to avoid bruising.", "MktPrice": 2.10, "Vol": "Med"},
    "Asparagus": {"Temp": "32-35°F", "Sens": "High", "Notes": "Stand upright if possible. High respiration.", "MktPrice": 2.80, "Vol": "Low"},
    "Avocados (Hass)": {"Temp": "40-55°F", "Sens": "High (Chill Injury Risk)", "Notes": "Do not freeze. Vent required.", "MktPrice": 1.95, "Vol": "High"},
    "Bananas": {"Temp": "56-58°F", "Sens": "Very High", "Notes": "Turns black below 55°F. Ethylene producer.", "MktPrice": 0.60, "Vol": "Very High"},
    "Beef (Fresh)": {"Temp": "28-32°F", "Sens": "High", "Notes": "Standard meat protocol.", "MktPrice": 3.50, "Vol": "High"},
    "Berries (All)": {"Temp": "32-34°F", "Sens": "Extreme", "Notes": "Very short shelf life. Pre-cool vital.", "MktPrice": 4.50, "Vol": "Medium"},
    "Chicken (Fresh)": {"Temp": "26-32°F", "Sens": "High", "Notes": "Raw meat protocols apply.", "MktPrice": 1.80, "Vol": "Very High"},
    "Lettuce": {"Temp": "34°F", "Sens": "High", "Notes": "Ethylene sensitive. Russet spotting.", "MktPrice": 0.80, "Vol": "Very High"},
    "Tomatoes": {"Temp": "55-60°F", "Sens": "Medium", "Notes": "Flavor loss if too cold.", "MktPrice": 1.10, "Vol": "High"}
}

if not st.session_state.loads_db:
    today_str = datetime.date.today().strftime(DATE_FMT)
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_FMT)
    st.session_state.loads_db = [
        {"id": "L-83921", "Origin City": "Salinas, CA", "Origin Zip": "93901", "Dest City": "Bronx, NY", "Dest Zip": "10474", "Commodity": "Strawberries", "Temp": "32-34 (Continuous)", "Weight": 38000, "Rate": 6500, "BookNow": True, "Status": "Open", "Shipper": "ship_pro", "Bids": [], "POD": False, "ETracks": False, "TeamReq": True, "Comments": "Handle with care.", "Docs": [], "DateStart": today_str, "DateEnd": today_str, "StatusLog": []},
        {"id": "L-29104", "Origin City": "McAllen, TX", "Origin Zip": "78501", "Dest City": "Chicago, IL", "Dest Zip": "60601", "Commodity": "Avocados", "Temp": "40-42 (Continuous)", "Weight": 42000, "Rate": 3200, "BookNow": False, "Status": "Open", "Shipper": "ship_pro", "Bids": [], "POD": False, "ETracks": False, "TeamReq": False, "Comments": "Check in at Gate 2.", "Docs": [], "DateStart": today_str, "DateEnd": tomorrow_str, "StatusLog": []},
    ]

if not st.session_state.trucks_db:
    today_str = datetime.date.today().strftime(DATE_FMT)
    tomorrow_str = (datetime.date.today() + datetime.timedelta(days=2)).strftime(DATE_FMT)
    st.session_state.trucks_db = [{"id": "T-50192", "Origin City": "Yuma, AZ", "Origin Zip": "85364", "Dest City": "Anywhere", "Dest Zip": "", "Commodity": "Any Produce", "Weight": 44000, "Rate": 3.00, "RateType": "RPM", "Carrier": "truck_guy", "Comments": "Team drivers available.", "Equip": "Reefer", "DateStart": today_str, "DateEnd": tomorrow_str, "TeamTruck": True, "EmptyNow": True}]

def get_coords(zip_code):
    if not zip_code: return {"lat": 39.8, "lon": -98.5}
    p2 = zip_code[:2]
    return ZIP_MAP.get(p2, {"lat": 39.8, "lon": -98.5})

def get_dist_zips(z1, z2):
    if not z1 or not z2: return 9999
    c1, c2 = get_coords(z1), get_coords(z2)
    R = 3959
    a = 0.5 - math.cos(math.radians(c2['lat']-c1['lat']))/2 + math.cos(math.radians(c1['lat'])) * math.cos(math.radians(c2['lat'])) * (1-math.cos(math.radians(c2['lon']-c1['lon'])))/2
    return R * 2 * math.asin(math.sqrt(a))

def render_location_input(label_prefix, key_prefix, allow_anywhere=False):
    c1, c2 = st.columns([1,1])
    current_list = ANYWHERE_LIST if allow_anywhere else QUICK_LIST
    with c1: 
        choice = st.selectbox(f"{label_prefix}", current_list, key=f"{key_prefix}_drop", label_visibility="visible", on_change=lambda: st.session_state.update({'truck_search_active': False, 'load_search_active': False}))
    with c2:
        manual = (choice == "Select from List...") or (choice == "Anywhere")
        d_city, d_zip = ("", "")
        if not manual:
            try: d_city, d_zip = choice.split(" (")[0], choice.split(" (")[1].replace(")", "")
            except Exception: pass
        if choice == "Anywhere": d_city = "Anywhere"
        city = st.text_input("City", value=d_city if not manual else d_city, key=f"{key_prefix}_c", disabled=not manual or choice=="Anywhere", placeholder="City", on_change=lambda: st.session_state.update({'truck_search_active': False, 'load_search_active': False}))
        zipc = st.text_input("Zip", value=d_zip if not manual else "", key=f"{key_prefix}_z", disabled=not manual or choice=="Anywhere", placeholder="Zip", on_change=lambda: st.session_state.update({'truck_search_active': False, 'load_search_active': False}))
    if choice == "Anywhere": return "Anywhere", ""
    if manual: return city, zipc
    return d_city, d_zip

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
        i_start = datetime.datetime.strptime(item_start_str, DATE_FMT).date()
        if not item_end_str or item_end_str == 'N/A': i_end = i_start
        else: i_end = datetime.datetime.strptime(item_end_str, DATE_FMT).date()
        return (search_start <= i_end) and (search_end >= i_start)
    except Exception:
        return True 

def get_status_badge(status):
    badges = {
        "Open": "status-blue", "Booked": "status-orange", "Loading": "status-orange",
        "In Transit": "status-orange", "Unloading": "status-orange", 
        "Delivered": "status-green", "Paid": "status-green", "SentToAccounting": "status-purple",
        "Delayed": "status-orange"
    }
    css_class = badges.get(status, "status-gray")
    if status == "Delayed": 
        return f"<span class='status-badge {css_class}' style='background-color:#fee2e2; color:#b91c1c;'>{status}</span>"
    return f"<span class='status-badge {css_class}'>{status}</span>"

def requires_pro(feature_name):
    """SaaS Paywall Logic: Blocks access if user is on Free tier."""
    if st.session_state.user.get('tier', 'Free') != 'Pro':
        st.warning(f"🔒 **{feature_name}** is a Pro Feature.")
        if st.button("🚀 Upgrade to Pro", key=f"upg_{feature_name}"):
            st.session_state.nav_selection = "Subscription"
            st.rerun()
        return True
    return False

def handle_swap(p1, p2):
    st.session_state[f"{p1}_drop"], st.session_state[f"{p2}_drop"] = st.session_state[f"{p2}_drop"], st.session_state[f"{p1}_drop"]
    st.session_state[f"{p1}_c"], st.session_state[f"{p2}_c"] = st.session_state[f"{p2}_c"], st.session_state[f"{p1}_c"]
    st.session_state[f"{p1}_z"], st.session_state[f"{p2}_z"] = st.session_state[f"{p2}_z"], st.session_state[f"{p1}_z"]

def reset_search_criteria(prefixes):
    for p in prefixes:
        st.session_state[f"{p}_drop"] = QUICK_LIST[0]
        st.session_state[f"{p}_c"] = ""
        st.session_state[f"{p}_z"] = ""
    st.session_state.truck_search_active = False
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
            if st.button("Save Attachment & AI Scan", key=f"save_doc_{load['id']}"):
                with st.spinner("🤖 AI Analyzing Document..."):
                    time.sleep(1.5)
                    timestamp = datetime.datetime.now().strftime("%d/%m %H:%M")
                    ai_note = "Auto-Extracted: Verified signature & weight."
                    if "BOL" in new_doc.name.upper(): ai_note = f"AI Read: {load['Weight']} lbs, {load['Commodity']}"
                    
                    load['Docs'].append({
                        "name": new_doc.name, "type": new_doc.type,
                        "date": timestamp, "user": st.session_state.user['name']
                    })
                    if ai_note not in load.get('Comments', ''):
                        load['Comments'] = f"{load.get('Comments', '')} | 🤖 {ai_note}"
                
                st.success("Document Saved & Data Extracted!")
                time.sleep(1)
                st.rerun()

def send_reply_callback(sender, from_user, key_name, context=None):
    msg_content = st.session_state[key_name]
    if not msg_content.strip():
        st.toast("⚠️ Cannot send empty message")
    else:
        st.session_state.messages_db.append({
            "id": generate_code("MSG"), "To": sender, "From": from_user,
            "Msg": msg_content, "Time": datetime.datetime.now().strftime("%H:%M"),
            "Folder": "inbox", "Status": "unread", "Context": context
        })
        st.session_state.expanded_convo = sender
        st.session_state.reply_error = None
        st.session_state[key_name] = ""
        st.toast("Reply Sent!")

def submit_bid(load_id, amount, comment):
    user_name = st.session_state.user['name']
    if st.session_state.get('confirm_bid_adjust') == load_id:
        for l in st.session_state.loads_db:
            if l['id'] == load_id:
                existing_bid = next((b for b in l['Bids'] if b['Carrier'] == user_name), None)
                if existing_bid:
                    existing_bid['Amount'] = amount
                    existing_bid['Comment'] = comment
                    st.toast(f"✏️ Bid updated to ${amount}!")
        st.session_state.confirm_bid_adjust = None
        return

    found_existing = False
    for l in st.session_state.loads_db:
        if l['id'] == load_id:
            existing_bid = next((b for b in l['Bids'] if b['Carrier'] == user_name), None)
            if existing_bid:
                found_existing = True
                break
    
    if found_existing:
        if st.session_state.skip_bid_confirm:
             st.session_state.confirm_bid_adjust = load_id
             submit_bid(load_id, amount, comment)
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
        for l in st.session_state.loads_db:
            if l['id'] == load_id:
                l['Bids'].append({"Carrier": user_name, "Amount": amount, "Comment": comment})
                st.toast(f"📨 Offer Sent!")

def book_load(load_id):
    for l in st.session_state.loads_db:
        if l['id'] == load_id:
            l['Status'] = "Booked"
            l['Carrier'] = st.session_state.user['name']
            l['NewBooking'] = True
            st.toast(f"✅ Booked! Temp set to {l['Temp']}")
            time.sleep(1)
            st.rerun()

def accept_bid(load_id, bid):
    for l in st.session_state.loads_db:
        if l['id'] == load_id:
            l['Status'] = "Booked"
            l['Carrier'] = bid['Carrier']
            l['Rate'] = bid['Amount']
            l['Bids'] = []
            l['BidAccepted'] = True
            st.success("Bid Accepted!")
            st.rerun()

# --- 5. AUTHENTICATION MODULE ---
def auth_page():
    """Renders the secure Login and Signup portal."""
    st.markdown("<br><br><h1 style='text-align: center; color: #059669;'>❄️ FreshChain</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>The Premium Cold Logistics Network</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])
        
        with tab_login:
            with st.form("login_form"):
                l_user = st.text_input("Username").strip()
                l_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Access Dashboard", type="primary", use_container_width=True):
                    if l_user in st.session_state.users_db:
                        # Secure password check using hash
                        if check_password_hash(st.session_state.users_db[l_user]['pass'], l_pass):
                            st.session_state.authenticated = True
                            st.session_state.user = st.session_state.users_db[l_user]
                            st.session_state.username = l_user 
                            st.session_state.nav_selection = "Dashboard"
                            st.balloons()
                            time.sleep(0.5) 
                            st.rerun()
                        else:
                            st.error("Invalid password.")
                    else:
                        st.error("Account not found. Please sign up.")
                        
            st.caption("Demo accounts: ship_pro | truck_guy (pass: 1234)")

        with tab_signup:
            with st.form("signup_form"):
                st.info("Start your 14-Day Free Trial.")
                s_user = st.text_input("Choose Username").strip()
                s_pass = st.text_input("Choose Password", type="password")
                s_pass2 = st.text_input("Confirm Password", type="password")
                s_name = st.text_input("Company Name")
                s_role = st.selectbox("I am a:", ["Shipper", "Carrier"])
                
                if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                    if s_user in st.session_state.users_db:
                        st.error("Username already exists. Pick another.")
                    elif s_pass != s_pass2:
                        st.error("Passwords do not match.")
                    elif len(s_pass) < 4:
                        st.error("Password too short.")
                    elif not s_name or not s_user:
                        st.error("All fields are required.")
                    else:
                        # Securely hash the password before saving
                        hashed_pw = generate_password_hash(s_pass)
                        st.session_state.users_db[s_user] = {
                            "pass": hashed_pw,
                            "role": s_role,
                            "name": s_name,
                            "tier": "Free",
                            "stars": 5.0,
                            "verified": False,
                            "contact": "",
                            "phone": "",
                            "email": "",
                            "profile_pic": None
                        }
                        st.success("Account created securely! Please Log In.")
                        time.sleep(1.5)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CORE PAGES ---
def page_dashboard():
    u = st.session_state.user
    hour = datetime.datetime.now().hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
    
    col_hdr, col_badge = st.columns([4, 1])
    col_hdr.markdown(f"## 👋 {greeting}, {html.escape(u['name'])}")
    if u.get('tier') == 'Pro':
        col_badge.markdown("<br><span class='pro-badge'>PRO PLAN</span>", unsafe_allow_html=True)
    else:
        col_badge.markdown("<br><span class='status-badge status-gray'>FREE PLAN</span>", unsafe_allow_html=True)

    st.write("") 
    
    alerts = []
    if u['role'] == "Shipper":
        for l in st.session_state.loads_db:
            if l['Shipper'] == u['name'] and l.get('NewBooking'):
                alerts.append({"type": "booking", "msg": f"Load {l['id']} booked by {l['Carrier']}!", "id": l['id']})
    else:
        for l in st.session_state.loads_db:
            if l.get('Carrier') == u['name'] and l.get('BidAccepted'):
                alerts.append({"type": "accepted", "msg": f"Bid Accepted for Load {l['id']}!", "id": l['id']})
    
    if alerts:
        with st.container():
            st.subheader("🔔 Action Required")
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
            c1.metric("Accounts Receivable", f"${pending_pay:,.2f}")
            c2.metric("Active Loads", f"{len([l for l in my_loads if l['Status'] not in ['Paid', 'Delivered', 'SentToAccounting']])}")
            c3.metric("Avg Reefer Rate", "$3.45/mi", "+15 cents")
        else: 
            my_loads = [l for l in st.session_state.loads_db if l['Shipper'] == u['name']]
            payable = sum([l['Rate'] for l in my_loads if l['Status'] not in ["Open", "Paid"]])
            c1, c2, c3 = st.columns(3)
            c1.metric("Accounts Payable", f"${payable:,.2f}")
            c2.metric("Active Shipments", f"{len([l for l in my_loads if l['Status'] == 'Booked'])}")
            c3.metric("Cold Capacity", "Tight", "High Demand")
    st.divider()

    col_main, col_feed = st.columns([2, 1])
    with col_main:
        if st.session_state.dash_prefs['show_actions']:
            st.subheader("⚡ Quick Actions")
            b1, b2, b3 = st.columns(3)
            if u['role'] == "Carrier":
                if b1.button("Find Loads 🔍", type="primary", use_container_width=True): st.session_state.nav_selection = "Find Loads"; st.rerun()
                if b2.button("My Trucks 🚛", use_container_width=True): st.session_state.nav_selection = "My Trucks"; st.rerun()
                if b3.button("Wallet 💳", use_container_width=True): st.session_state.nav_selection = "Wallet"; st.rerun()
            else:
                if b1.button("Post Loads 📦", type="primary", use_container_width=True): st.session_state.nav_selection = "Post Load"; st.rerun()
                if b2.button("Find Reefers 🚚", use_container_width=True): st.session_state.nav_selection = "Find Trucks"; st.rerun()
                if b3.button("Directory 📖", use_container_width=True): st.session_state.nav_selection = "Directory"; st.rerun()
            st.write("")

        if st.session_state.dash_prefs['show_activity']:
            st.subheader("📅 Recent Activity")
            visible_recent = [l for l in my_loads if l['Status'] != 'SentToAccounting']
            if not visible_recent: st.info("No recent active shipments.")
            else:
                for l in visible_recent[-3:]:
                    ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                    with st.expander(f"{l['id']} • {html.escape(l['Origin City'])} ➝ {html.escape(l['Dest City'])}"):
                        st.caption(f"📅 {ldate}") 
                        st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                        shipper_name = st.session_state.users_db.get(l['Shipper'], {}).get('name', l['Shipper'])
                        st.write(f"**With:** {html.escape(shipper_name)}")
                        c1, c2 = st.columns(2)
                        c1.write(f"**Commodity:** {html.escape(l['Commodity'])}")
                        c1.write(f"**Temp:** {html.escape(str(l['Temp']))}")
                        c2.write(f"**Rate:** ${l['Rate']}")
                        c2.write(f"**Weight:** {l['Weight']:,} lbs")

    with col_feed:
        if st.session_state.dash_prefs['show_news']:
            st.subheader("📰 Market Insights")
            for site in st.session_state.news_sites[:3]:
                st.markdown(f"<div class='news-card'><b>📰 Top trend from {html.escape(site)}</b><br><small style='color:grey'>Capacity tightening in major produce regions.</small></div>", unsafe_allow_html=True)

def page_subscription():
    st.markdown("## 🚀 Unlock FreshChain Pro")
    st.write("Scale your logistics business with premium tools and zero restrictions.")
    current_tier = st.session_state.user.get('tier', 'Free')
    
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Free Tier")
            st.markdown("#### $0 / month")
            st.write("✔️ Basic Load/Truck Search")
            st.write("✔️ In-App Messaging")
            st.write("✔️ Standard Directory Profile")
            st.write("❌ No Factoring / QuickPay")
            st.write("❌ No Private Network Access")
            st.write("❌ No API Integrations")
            st.write("")
            if current_tier == 'Free': st.button("Current Plan", disabled=True, use_container_width=True)
            
    with c2:
        with st.container(border=True):
            st.markdown("### Pro Tier <span class='pro-badge'>POPULAR</span>", unsafe_allow_html=True)
            st.markdown("#### $49 / month")
            st.write("✔️ Unlimited Load/Truck Search")
            st.write("✔️ **Priority Load Postings**")
            st.write("✔️ **Private Carrier Network**")
            st.write("✔️ **Instant Factoring Access**")
            st.write("✔️ **Quickbooks Export**")
            st.write("")
            if current_tier == 'Pro': st.success("You are an active Pro member!")
            else:
                st.info("Simulated Checkout Gateway")
                if st.button("💳 Upgrade with Stripe", type="primary", use_container_width=True):
                    st.session_state.user['tier'] = 'Pro'
                    st.session_state.users_db[st.session_state.username]['tier'] = 'Pro'
                    st.balloons()
                    st.success("Payment Successful! Welcome to Pro.")
                    time.sleep(2)
                    st.rerun()

def page_post_load():
    st.markdown("## 📦 Post Loads")
    if st.session_state.get('reset_load_form'):
        for k in ['plo_c', 'plo_z', 'pld_c', 'pld_z', 'pl_notes', 'pl_appt_time']: st.session_state[k] = ""
        st.session_state['pl_comm'] = "Fresh Produce"
        st.session_state['pl_min'] = 34
        st.session_state['pl_max'] = 36
        st.session_state['pl_weight'] = 40000
        st.session_state['pl_rate'] = 2500
        st.session_state['reset_load_form'] = False

    with st.container(border=True):
        c1, c2, c3 = st.columns([10, 1, 10])
        with c1: oc, oz = render_location_input("Origin", "plo")
        with c2:
            st.write("")
            st.button("⇄", key="swap_pl", on_click=handle_swap, args=("plo", "pld"))
        with c3: dc, dz = render_location_input("Dest", "pld")
        
        c4, c5, c6 = st.columns(3)
        comm = c4.text_input("Commodity", st.session_state['pl_comm'], key="pl_comm")
        c5a, c5b = c5.columns(2)
        temp_min = c5a.number_input("Min Temp", value=st.session_state['pl_min'], key="pl_min")
        temp_max = c5b.number_input("Max Temp", value=st.session_state['pl_max'], key="pl_max")
        weight = c6.number_input("Weight (lbs)", value=st.session_state['pl_weight'], key="pl_weight")
        
        c_dates, c_opts = st.columns([2, 2])
        with c_opts:
            appt_type = st.radio("Appointment Type", ["Open / Flexible", "First Come First Serve (FCFS)", "Strict Appointment"], horizontal=True)
        with c_dates:
            cd1, cd2 = st.columns([2, 1])
            load_dates = cd1.date_input("Pickup Window", [datetime.date.today(), datetime.date.today()], min_value=datetime.date.today())
            with cd2:
                if appt_type == "Strict Appointment": appt_time = st.text_input("Appt Time (00:00)", key="pl_appt_time")
                else: appt_time = ""

        rt = st.number_input("Target Rate ($)", value=st.session_state['pl_rate'], key="pl_rate")
        
        c9, c10 = st.columns(2)
        etracks = c9.checkbox("E-Tracks Required")
        team_req = c10.checkbox("Team Required")
        book_now = st.checkbox("Allow Instant Booking", value=True)
        
        private_network = st.checkbox("🔒 Post to Private Network (Pro Only)")
        if private_network and requires_pro("Private Network"): private_network = False
        
        comments = st.text_area("Special Instructions", key="pl_notes")
        
        if st.button("Post Load", type="primary", use_container_width=True):
            if not oc or not dc: st.error("⚠️ Origin & Dest required")
            elif rt <= 0: st.error("⚠️ Rate must be > $0")
            else:
                s_date = load_dates[0] if isinstance(load_dates, tuple) else load_dates
                e_date = load_dates[1] if isinstance(load_dates, tuple) and len(load_dates)>1 else s_date
                
                appt_str = f"Strict: {appt_time}" if appt_type == "Strict Appointment" else appt_type
                final_comments = f"{appt_str} | {comments}" if appt_str != "Open / Flexible" else comments
                if private_network: final_comments = f"[PRIVATE POST] {final_comments}"
                
                st.session_state.loads_db.append({
                    "id": generate_code("L"), "Origin City": oc, "Origin Zip": oz, 
                    "Dest City": dc, "Dest Zip": dz, "Equip": "Reefer", "Weight": weight,
                    "Commodity": comm, "Temp": f"{temp_min}-{temp_max}", 
                    "Rate": rt, "ETracks": etracks, "TeamReq": team_req, 
                    "Comments": final_comments, "BookNow": book_now, "Status": "Open", 
                    "Shipper": st.session_state.user['name'], "Bids": [], "POD": False,
                    "Docs": [], "DateStart": s_date.strftime(DATE_FMT), "DateEnd": e_date.strftime(DATE_FMT)
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
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    with c1:
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.markdown(f"**{ldate}**")
                        st.write(f"{html.escape(l['Origin City'])} ➝ {html.escape(l['Dest City'])}")
                        st.caption(f"**{l['id']}**")
                    with c2:
                         st.write(f"**{html.escape(l['Commodity'])}**")
                         st.write(f"{html.escape(str(l['Temp']))}°F")
                    with c3:
                        new_rate = st.number_input(f"Rate ($)", value=float(l['Rate']), step=50.0, key=f"edit_load_{l['id']}")
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
                    if l.get('Comments'): st.info(f"📝 {html.escape(l['Comments'])}")

                if l['Bids']:
                    with st.expander(f"📬 {len(l['Bids'])} New Offer(s) Received", expanded=True):
                        for bid in l['Bids']:
                            with st.container(border=True):
                                bc1, bc2, bc3 = st.columns([2,1,1])
                                bc1.write(f"**{html.escape(bid['Carrier'])}** offered **${bid['Amount']}**")
                                if bid.get('Comment'): bc1.caption(f"💬 \"{html.escape(bid['Comment'])}\"")
                                c_stats = CARRIER_DETAILS.get(bid['Carrier'], CARRIER_DETAILS.get("Cool Runnings Logistics"))
                                bc2.caption(f"MC: {c_stats.get('MC', 'N/A')}")
                                bc2.caption(f"Ins: {c_stats.get('Insurance', 'N/A')}")
                                if bc3.button("Accept", key=f"acc_{l['id']}_{bid['Carrier']}"):
                                    accept_bid(l['id'], bid)

    with tab_active:
        c_filter, = st.columns(1)
        status_filter = c_filter.multiselect("Filter Status", ["Booked", "Loading", "In Transit", "Unloading", "Delayed"], default=[])
        active_loads = [l for l in all_loads if l['Status'] in ["Booked", "Loading", "In Transit", "Unloading", "Delayed"]]
        if status_filter: active_loads = [l for l in active_loads if l['Status'] in status_filter]

        if not active_loads: st.info("No loads in transit.")
        else:
            for l in active_loads:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                    with c1:
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.markdown(f"**{ldate}** • **{html.escape(l['Origin City'])}** ➝ **{html.escape(l['Dest City'])}**")
                        st.caption(f"**{l['id']}** • {html.escape(l['Commodity'])} @ {html.escape(str(l['Temp']))}")
                    with c2: st.markdown(f"**${l['Rate']}**")
                    with c3: st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    with c4:
                        rc_text = generate_rate_con_text(l)
                        st.download_button("📄 Rate Con", data=rc_text, file_name=f"RateCon_{l['id']}.txt", key=f"src_{l['id']}")
                        st.write("")
                        if st.button("📲 Track", key=f"trk_{l['id']}"): st.toast("Tracking Request sent!")
                    
                    if l['Status'] in ["Loading", "In Transit"]:
                         st.markdown(f"**❄️ Live IoT Temp:** `{random.randint(33, 35)}°F` (Updated: Just now)")
                    
                    if l.get('LatestStatusNote'): st.info(f"🚚 **Note:** {html.escape(l['LatestStatusNote'])}")
                    render_docs_section(l)
                    
                    if l['Status'] == "Delivered" and not l.get('ShipperReviewed'):
                        st.divider()
                        st.warning(f"🌟 Please rate {html.escape(l.get('Carrier', 'Carrier'))}")
                        with st.form(key=f"rev_form_s_{l['id']}"):
                            stars = st.slider("Rating", 1, 5, 5)
                            comment = st.text_input("Comment (Optional)")
                            if st.form_submit_button("Submit Review"):
                                st.session_state.reviews_db.append({"From": u['name'], "To": l.get('Carrier'), "Stars": stars, "Comment": comment, "Date": datetime.date.today().strftime("%Y-%m-%d")})
                                l['ShipperReviewed'] = True
                                st.success("Review Submitted!")
                                time.sleep(1)
                                st.rerun()

    with tab_history:
        history = [l for l in all_loads if l['Status'] in ["Delivered", "SentToAccounting"]]
        if not history: st.info("No completed load history.")
        else:
            for l in history:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1: 
                        ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                        st.write(f"**{l['id']}** • **{html.escape(l['Origin City'])}** ➝ **{html.escape(l['Dest City'])}**")
                        st.caption(f"📅 {ldate} | Carrier: {html.escape(l.get('Carrier', 'Unknown'))}")
                    with c2: st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    with c3: st.write(f"**${l['Rate']}**")
                    render_docs_section(l)

def page_wallet():
    """Financial Ledger ensuring strict indentation and logic isolation."""
    st.markdown("## 📊 Financial Ledger")
    u = st.session_state.user
    
    if u['role'] == "Carrier":
        st.info("ℹ️ Payments processed after POD verification.")
        my_loads = [l for l in st.session_state.loads_db if l.get('Carrier') == u['name']]
        all_unpaid = [l for l in my_loads if l['Status'] in ["Delivered", "SentToAccounting"]]
        owed = sum([l['Rate'] for l in all_unpaid])
        paid = sum([l['Rate'] for l in my_loads if l['Status'] == 'Paid'])
        
        c1, c2 = st.columns(2)
        c1.metric("Outstanding Invoices", f"${owed:,.2f}")
        c2.metric("Total Paid (YTD)", f"${paid:,.2f}")
        st.divider()
        st.subheader("Invoice Management")

        if not all_unpaid: 
            st.write("No active invoices.")
            
        with st.container(height=500, border=True):
            for job in all_unpaid:
                ldate = format_date_range(job.get('DateStart', 'N/A'), job.get('DateEnd', 'N/A'))
                shipper_name = st.session_state.users_db.get(job['Shipper'], {}).get('name', job['Shipper'])
                
                with st.expander(f"🧾 {job['id']} • {html.escape(job['Origin City'])} ➝ {html.escape(job['Dest City'])}"):
                    st.caption(f"📅 {ldate} | Shipper: {html.escape(shipper_name)}")
                    st.markdown(get_status_badge(job['Status']), unsafe_allow_html=True)
                    st.write(f"**Rate:** ${job['Rate']}")
                    render_docs_section(job)
                    
                    # STRICT ELIF LOGIC FIX:
                    if job['Status'] == "Booked":
                        st.warning("Mark load as Delivered in 'My Trucks' to invoice.")
                    elif job['Status'] == "Delivered":
                        claim_flag = st.checkbox("🚩 Flag for Claim", key=f"claim_{job['id']}")
                        if st.button("📤 Send to Accounting", key=f"acct_{job['id']}", disabled=claim_flag):
                            job['Status'] = "SentToAccounting"
                            st.toast("✅ Invoice forwarded.")
                            time.sleep(1)
                            st.rerun()
                            
                        st.divider()
                        if st.button("⚡ Get Paid Now (Factoring)", key=f"factor_{job['id']}"):
                            if not requires_pro("Instant Factoring"):
                                st.success("Factoring request sent. Funds will clear in 24h.")
                    elif job['Status'] == "SentToAccounting":
                        st.info("Awaiting Payment from Shipper.")

    else:
        st.info("ℹ️ Track freight spend.")
        my_loads = [l for l in st.session_state.loads_db if l['Shipper'] == u['name']]
        unpaid_loads = [l for l in my_loads if l['Status'] in ['Delivered', 'SentToAccounting']]
        unpaid = sum([l['Rate'] for l in unpaid_loads])
        st.metric("Total Accounts Payable", f"${unpaid:,.2f}")
        
        if st.button("📥 Export to QuickBooks"):
            if not requires_pro("Quickbooks Integration"):
                st.success("CSV Data compiled and ready for download.")
                
        st.divider()
        st.subheader("Invoices Due")
        
        if not unpaid_loads: 
            st.write("No invoices due.")
            
        with st.container(height=500, border=True):
            for l in unpaid_loads:
                carrier_display = l.get('Carrier', 'Unknown')
                ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                with st.expander(f"🧾 {l['id']} • {html.escape(l['Origin City'])} ➝ {html.escape(l['Dest City'])}"):
                    st.write(f"**Carrier:** {html.escape(carrier_display)} | **Rate:** ${l['Rate']}")
                    st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    render_docs_section(l)
                    
                    if l['Status'] == "Delivered" or l['Status'] == "SentToAccounting":
                        claim_flag = st.checkbox("🚩 Flag for Dispute", key=f"s_claim_{l['id']}")
                        if st.button("📤 Send to AP Dept (Pay)", key=f"mp_{l['id']}", disabled=claim_flag):
                            l['Status'] = "Paid"
                            st.toast("✅ Payment Processed.")
                            time.sleep(1)
                            st.rerun()
                        if claim_flag:
                            st.error("Payment frozen due to dispute.")

def page_find_trucks():
    st.markdown("## 🚚 Find Capacity")
    col_ui_1, col_ui_2 = st.columns([6, 1])

    with col_ui_1:
        with st.container(border=True):
            c1, c2, c3 = st.columns([10, 1, 10]) 
            with c1: oc, oz = render_location_input("Origin", "fto") 
            with c2:
                st.write(""); st.button("⇄", key="swap_ft", on_click=handle_swap, args=("fto", "ftd"))
            with c3: dc, dz = render_location_input("Dest", "ftd", allow_anywhere=True)
            
            rad = st.selectbox("Radius (mi)", [50, 100, 150, 200, 250, 300], index=2)
            search_dates = st.date_input("Filter by Availability", value=[datetime.date.today(), datetime.date.today()], min_value=datetime.date.today())
            
            st.write("")
            prioritize_team = st.checkbox("Prioritize Team")
            prioritize_empty = st.checkbox("Prioritize Empty Now")
            
            st.write("")
            if st.button("Search Trucks", type="primary", use_container_width=True):
                st.session_state.truck_search_active = True
    
    with col_ui_2:
        st.write(""); st.write(""); st.write("")
        st.button("🔄 Reset", on_click=reset_search_criteria, args=(['fto', 'ftd'],), type="secondary")
            
    if st.session_state.truck_search_active:
        if not oc: st.error("Origin required.")
        elif not dc: st.error("Destination required.")
        elif not search_dates: st.error("Date Window required.") 
        else:
            found = []
            for t in st.session_state.trucks_db:
                if get_dist_zips(oz, t['Origin Zip']) > rad: continue
                if dc != "Anywhere" and t.get('Dest City') and t.get('Dest City') != dc: continue
                
                s_start = search_dates[0] if isinstance(search_dates, tuple) else search_dates
                s_end = search_dates[1] if isinstance(search_dates, tuple) and len(search_dates)>1 else s_start
                if not check_overlap(s_start, s_end, t.get('DateStart'), t.get('DateEnd')): continue

                found.append(t)
            
            found.sort(key=lambda x: (not (prioritize_empty and x.get('EmptyNow')), not (prioritize_team and x.get('TeamTruck'))))

            if found:
                st.success(f"Found {len(found)} trucks.")
                for t in found:
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                        t_date = format_date_range(t.get('DateStart', 'N/A'), t.get('DateEnd', 'N/A'))
                        c1.markdown(f"**{t_date}**")
                        c1.caption(f"{html.escape(t['Origin City'])} ➝ {html.escape(t.get('Dest City', 'Anywhere'))}")
                        
                        carrier_name = st.session_state.users_db.get(t['Carrier'], {}).get('name', t['Carrier'])
                        c2.write(f"**{html.escape(carrier_name)}**")
                        if t.get('TeamTruck'): c2.caption("🚛 Team")
                        
                        c3.write(f"**${t['Rate']}{'/mi' if t.get('RateType') == 'RPM' else ''}**")
                        c3.caption(f"{html.escape(t.get('Equip', 'Reefer'))}")

                        with c4:
                            with st.popover("📞 Contact"):
                                details = CARRIER_DETAILS.get(carrier_name, CARRIER_DETAILS.get("Cool Runnings Logistics"))
                                st.write(f"**MC#:** {details.get('MC', 'N/A')}")
                                st.write(f"**Phone:** {details['Phone']}")
                                if st.button("⚡ Is truck available?", key=f"auto_inq_st_{t['id']}"):
                                     msg_txt = f"Is your truck in {t['Origin City']} available for {t_date}?"
                                     st.session_state.messages_db.append({"id": generate_code("MSG"), "To": t['Carrier'], "From": u['name'], "Msg": msg_txt, "Time": datetime.datetime.now().strftime("%H:%M"), "Folder": "inbox", "Status": "unread"})
                                     st.toast("📨 Sent!")
            else: st.warning("No trucks found matching criteria.")

def page_post_truck():
    st.markdown("## 📢 Post Capacity")
    if st.session_state.get('reset_truck_form'):
        for k in ['pto_c', 'pto_z', 'ptd_c', 'ptd_z', 'pt_notes']: st.session_state[k] = ""
        st.session_state['pt_weight'] = 44000
        st.session_state['pt_rate'] = 3.00
        st.session_state['reset_truck_form'] = False

    with st.container(border=True):
        c1, c2, c3 = st.columns([10, 1, 10])
        with c1: oc, oz = render_location_input("Empty", "pto")
        with c2: st.write(""); st.write(""); st.button("⇄", key="swap_pt", on_click=handle_swap, args=("pto", "ptd"))
        with c3: dc, dz = render_location_input("Dest", "ptd")
        
        c4, c5 = st.columns(2)
        weight = c5.number_input("Max Wt", value=st.session_state['pt_weight'], key="pt_weight")
        truck_dates = st.date_input("Availability Window", [datetime.date.today(), datetime.date.today()], min_value=datetime.date.today())
        c6, c7 = st.columns(2)
        rate_type = c6.selectbox("Rate Type", ["Flat Rate ($)", "RPM ($/mi)"])
        rt = c7.number_input("Amount", value=st.session_state['pt_rate'], key="pt_rate")
        team_truck = st.checkbox("Team Truck Available", value=False)
        empty_now = st.checkbox("Empty Now", value=False)
        comments = st.text_area("Driver Notes", key="pt_notes")
        
        if st.button("Post Truck", type="primary", use_container_width=True):
            if not oc: st.error("⚠️ Origin required")
            else:
                s_date = truck_dates[0] if isinstance(truck_dates, tuple) else truck_dates
                e_date = truck_dates[1] if isinstance(truck_dates, tuple) and len(truck_dates)>1 else s_date
                st.session_state.trucks_db.append({
                    "id": generate_code("T"), "Origin City": oc, "Origin Zip": oz, 
                    "Dest City": dc, "Dest Zip": dz, "Equip": "Reefer", "Weight": weight, 
                    "Rate": rt, "RateType": "RPM" if "RPM" in rate_type else "FLAT",
                    "Carrier": st.session_state.user['name'], "Comments": comments,
                    "TeamTruck": team_truck, "EmptyNow": empty_now,
                    "DateStart": s_date.strftime(DATE_FMT), "DateEnd": e_date.strftime(DATE_FMT)
                })
                st.success("Truck Posted!")
                st.session_state['reset_truck_form'] = True
                time.sleep(1)
                st.rerun()

def page_my_trucks():
    st.markdown("## 🚛 Fleet Management")
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
                        st.write(f"**{t_date}** • **{html.escape(t['Origin City'])}** ➝ **{html.escape(t['Dest City'] or 'Anywhere')}**")
                        st.caption(f"**{t['id']}** • {t.get('Equip', 'Reefer')} • ${t['Rate']}{'/mi' if t.get('RateType') == 'RPM' else ''}")
                    with c2: 
                        new_val = st.number_input("Rate", value=float(t['Rate']), step=0.10 if t.get('RateType') == 'RPM' else 50.0, key=f"er_{t['id']}")
                        if new_val != t['Rate']:
                            t['Rate'] = new_val
                            st.rerun()
                    with c3:
                        if st.button("Cancel", key=f"del_trk_{t['id']}"):
                            st.session_state.trucks_db.remove(t)
                            st.rerun()

    with tab_bids:
        active_bids = [ (l, next((b for b in l['Bids'] if b['Carrier'] == st.session_state.user['name']), None)) for l in st.session_state.loads_db if l['Status'] == 'Open' and any(b['Carrier'] == st.session_state.user['name'] for b in l['Bids']) ]
        if not active_bids: st.info("No active bids placed.")
        else:
            for load, bid in active_bids:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{html.escape(load['Origin City'])}** ➝ **{html.escape(load['Dest City'])}**")
                        st.write(f"**My Bid:** ${bid['Amount']}")
                    with c2:
                        st.info("Pending")
                        if st.button("Cancel Bid", key=f"cancel_bid_{load['id']}"):
                             load['Bids'].remove(bid)
                             st.rerun()

    with tab_active:
        active_loads = [l for l in all_loads if l['Status'] in ["Booked", "Loading", "In Transit", "Unloading", "Delayed"]]
        if not active_loads: st.info("No trucks currently dispatched.")
        else:
            for l in active_loads:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    ldate = format_date_range(l.get('DateStart', 'N/A'), l.get('DateEnd', 'N/A'))
                    c1.write(f"**{html.escape(l['Origin City'])}** ➝ **{html.escape(l['Dest City'])}**")
                    c2.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)
                    
                    with st.expander("📦 Updates"):
                        s_real_name = st.session_state.users_db.get(l['Shipper'], {}).get('name', l['Shipper'])
                        st.write(f"🏢 **Shipper:** {html.escape(s_real_name)}")
                        st.write(f"**Rate:** ${l['Rate']}")
                        
                        new_status = st.selectbox("Status", ["Booked", "Loading", "In Transit", "Unloading", "Delivered", "Delayed"], key=f"stat_sel_{l['id']}", index=0)
                        if st.button("Update", key=f"conf_s_{l['id']}"):
                            l['Status'] = new_status
                            st.rerun()
                        render_docs_section(l)

    with tab_history:
        history = [l for l in all_loads if l['Status'] in ["Delivered", "SentToAccounting"]]
        if not history: st.info("No completed load history.")
        else:
            for l in history:
                with st.container(border=True):
                    st.write(f"**{l['id']}** • **{html.escape(l['Origin City'])}** ➝ **{html.escape(l['Dest City'])}**")
                    st.markdown(get_status_badge(l['Status']), unsafe_allow_html=True)

def page_general_search():
    st.markdown("## 🔎 Global Search")
    query = st.text_input("Enter keyword").strip().lower()
    if len(query) < 2 and query != "":
        st.warning("Enter at least 2 characters.")
        return
    if query:
        st.divider()
        found = False
        matched_commodities = [(name, data) for name, data in COMMODITIES_DB.items() if any(k.startswith(query) for k in name.lower().split())]
        if matched_commodities:
            found = True
            st.markdown(f"### 🥦 Commodity Intelligence")
            for name, data in matched_commodities:
                with st.container(border=True):
                    st.subheader(f"❄️ {html.escape(name)}")
                    st.metric("Set Point", html.escape(data['Temp']))
        if not found: st.warning("No results found.")

def page_tools_shipper():
    st.markdown("## 🧰 Shipper Toolkit")
    st.subheader("Cold Chain Temperature Guide")
    search_choice = st.selectbox("Search Commodity", ["Select..."] + sorted(list(COMMODITIES_DB.keys())))
    if search_choice != "Select...":
        data = COMMODITIES_DB[search_choice]
        c1, c2 = st.columns(2)
        c1.metric("Set Point", html.escape(data['Temp']))
        c2.metric("Sensitivity", "See Notes", html.escape(data['Sens']))
        st.info(f"**Handling Notes:** {html.escape(data['Notes'])}")

def page_tools_driver():
    st.markdown("## 🧰 Driver Toolkit")
    st.subheader("Profit Calculator")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        rate = c1.number_input("Rate ($)", 2500)
        fuel = c3.number_input("Fuel ($)", 400)
        if st.button("Calc Profit"): st.metric("Net Profit", f"${rate - fuel}")

def page_inbox():
    st.markdown("## 📬 Message Center")
    u = st.session_state.user
    my_inbox = [m for m in st.session_state.messages_db if m['To'] == u['name'] or m['To'] == st.session_state.username]
    if not my_inbox: st.info("Inbox is empty.")
    else:
        for m in reversed(my_inbox):
            st.markdown(f"**From:** {html.escape(m['From'])}")
            st.write(html.escape(m['Msg']))
            with st.expander("Reply"):
                reply_key = f"rep_{m['id']}"
                st.text_input("Message", key=reply_key)
                st.button("Send", key=f"s_{m['id']}", on_click=send_reply_callback, args=(m['From'], u['name'], reply_key, m['Msg']))
            st.divider()

def page_directory():
    st.markdown("## 📖 Company Directory")
    search = st.text_input("Search Company Name or MC#")
    if search:
        found = False
        for uid, udata in st.session_state.users_db.items():
            if search.lower() in udata['name'].lower():
                found = True
                with st.container(border=True):
                    st.subheader(html.escape(udata['name']))
                    st.caption(f"Role: {html.escape(udata['role'])}")
        if not found: st.warning("No companies found.")

# --- 7. ROUTING & MAIN EXECUTION ---
if not st.session_state.authenticated:
    auth_page()
else:
    u = st.session_state.user
    with st.sidebar:
        st.markdown(f"### {html.escape(u['name'])}")
        tier_color = "#f59e0b" if u.get('tier') == 'Pro' else "#94a3b8"
        st.markdown(f"<span style='color: white; background: {tier_color}; padding: 2px 6px; border-radius: 4px; font-size: 12px;'>{html.escape(u.get('tier', 'Free'))} Plan</span>", unsafe_allow_html=True)
        st.divider()
        
        msg_count = len([m for m in st.session_state.messages_db if m['To'] == u['name'] and m.get('Status') == 'unread'])
        inbox_label = f"Inbox ({msg_count})" if msg_count > 0 else "Inbox"

        if u['role'] == "Carrier":
            options = ["Dashboard", "Find Loads", "Post Truck", "My Trucks", inbox_label, "Wallet", "Tools", "Subscription", "Directory", "Profile"]
            real_opts = ["Dashboard", "Find Loads", "Post Truck", "My Trucks", "Inbox", "Wallet", "Tools", "Subscription", "Directory", "Profile"]
        else:
            options = ["Dashboard", "Post Load", "My Loads", "Find Trucks", inbox_label, "Wallet", "Tools", "Subscription", "Directory", "Profile"]
            real_opts = ["Dashboard", "Post Load", "My Loads", "Find Trucks", "Inbox", "Wallet", "Tools", "Subscription", "Directory", "Profile"]
            
        current_index = real_opts.index(st.session_state.nav_selection) if st.session_state.nav_selection in real_opts else 0
        sel = st.radio("Menu", options, index=current_index)
        mapped_sel = real_opts[options.index(sel)]

        if mapped_sel != st.session_state.nav_selection:
            st.session_state.nav_selection = mapped_sel
            st.rerun()
        
        st.divider()
        if st.button("Log Out"): 
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Route Handler
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
    elif st.session_state.nav_selection == "Directory": page_directory()
    elif st.session_state.nav_selection == "Subscription": page_subscription()
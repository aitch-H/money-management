import streamlit as st
import pandas as pd
import datetime
import os
import plotly.express as px
import plotly.graph_objects as go
import requests
import time

# --- 1. Page Config ---
st.set_page_config(page_title="SU-MAL", page_icon="💰", layout="wide")

# --- 2. Initialize Session States ---
if 'language' not in st.session_state: st.session_state.language = 'my'
if 'base_currency' not in st.session_state: st.session_state.base_currency = 'MMK'
if 'exchange_rates' not in st.session_state:
    st.session_state.exchange_rates = {'THB': 145.0, 'USD': 3500.0, 'EUR': 3800.0, 'SGD': 2600.0, 'MMK': 1.0}

# --- 3. Translations & Categories ---
TRANSLATIONS = {
    "en": {
        "app_title": "SU-MAL _ BUDGET TRACKER", "dashboard": "📊 Dashboard", "income": "Income", 
        "expense": "Expense", "transfer": "Transfer", "saved": "Saved", "type": "Type",
        "cat": "Category", "amt": "Amount", "note": "Note", "save": "Add Record", "history": "History"
    },
    "my": {
        "app_title": "SU-MAL _ ငွေစာရင်း စီမံခန့်ခွဲမှု", "dashboard": "📊 Dashboard", "income": "ဝင်ငွေ", 
        "expense": "အသုံးစရိတ်", "transfer": "ပို့ငွေ", "saved": "လက်ကျန်", "type": "အမျိုးအစား",
        "cat": "အုပ်စု", "amt": "ပမာဏ", "note": "မှတ်ချက်", "save": "စာရင်းသွင်းမည်", "history": "မှတ်တမ်း"
    },
    "th": {
        "app_title": "SU-MAL _ แอปจัดการเงิน", "dashboard": "📊 แดชบอร์ด", "income": "รายได้", 
        "expense": "ค่าใช้จ่าย", "transfer": "โอนเงิน", "saved": "เงินออม", "type": "ประเภท",
        "cat": "หมวดหมู่", "amt": "จำนวนเงิน", "note": "หมายเหตุ", "save": "บันทึก", "history": "ประวัติ"
    }
}

CATS = {
    "Income": ["Salary", "Bonus", "Gift", "Other"],
    "Expense": ["Food", "Transport", "Shopping", "Bills", "Health", "Other"],
    "Transfer": ["Family", "Bank", "Investment"]
}

def t(key): return TRANSLATIONS[st.session_state.language].get(key, key)

# --- 4. Live Exchange Rates ---
def update_live_rates():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        rates = requests.get(url).json().get("rates", {})
        st.session_state.exchange_rates.update({'THB': rates.get("THB", 35.0), 'USD': 1.0, 'MMK': 4500.0})
    except: pass

# --- 5. Custom CSS (For Sketch Look) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { font-size: 13px !important; }
    .stSelectbox label, .stNumberInput label { font-size: 12px !important; font-weight: bold; }
    h1 { font-family: 'Courier New', Courier, monospace; font-size: 26px !important; border-bottom: 2px solid black; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. Top Section: Header & Menu ---
col_head, col_menu = st.columns([4, 1])
col_head.title(t("app_title"))

with col_menu.popover("☰ Menu"):
    st.session_state.language = st.selectbox("🌐 Language", ["my", "en", "th"], index=["my", "en", "th"].index(st.session_state.language))
    st.session_state.base_currency = st.selectbox("💱 Currency", ["MMK", "THB", "USD"], index=["MMK", "THB", "USD"].index(st.session_state.base_currency))
    if st.button("🔄 Refresh Rates"): update_live_rates(); st.rerun()

# --- 7. Main Body Layout (Based on User Sketch) ---
DATA_FILE = "sumal_records.csv"
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "Type", "Category", "Amount_MMK", "Note", "Input_Currency", "Input_Amount"]).to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
rate = st.session_state.exchange_rates.get(st.session_state.base_currency, 1.0)
curr_s = {"USD": "$", "THB": "฿", "MMK": "K"}[st.session_state.base_currency]

# Row 1: Donut Chart & Drop Box Form
row1_col1, row1_col2 = st.columns([1.2, 2])

with row1_col1:
    st.subheader("Visual Analysis")
    if not df.empty:
        fig_donut = px.pie(df, values="Amount_MMK", names="Type", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_donut.update_layout(showlegend=False, height=220, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_donut, use_container_width=True)
    else: st.info("No records yet")

with row1_col2:
    st.markdown("**ENTER YOUR TRANSACTION**")
    with st.container(border=True):
        # Everything in Drop Box as requested
        f_col1, f_col2 = st.columns(2)
        trans_type_ui = f_col1.selectbox(t("type"), [t("income"), t("expense"), t("transfer")], index=1)
        
        # Internal logic for category filtering
        actual_type = "Income" if trans_type_ui == t("income") else "Expense" if trans_type_ui == t("expense") else "Transfer"
        category = f_col2.selectbox(t("cat"), CATS[actual_type])
        
        f_col3, f_col4 = st.columns(2)
        amt = f_col3.number_input(f"{t('amt')} ({curr_s})", min_value=0.0)
        entry_date = f_col4.date_input("Date", datetime.date.today())
        
        note = st.text_input(t("note"))
        if st.button(t("save"), type="primary", use_container_width=True):
            if amt > 0:
                mmk_val = amt if st.session_state.base_currency == 'MMK' else amt * st.session_state.exchange_rates.get(st.session_state.base_currency, 1.0)
                new_row = pd.DataFrame([[entry_date, actual_type, category, mmk_val, note, st.session_state.base_currency, amt]], 
                                        columns=["Date", "Type", "Category", "Amount_MMK", "Note", "Input_Currency", "Input_Amount"])
                new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success("Success!"); time.sleep(0.5); st.rerun()

# Row 2: Metric Icons
st.divider()
m1, m2, m3 = st.columns(3)
if not df.empty:
    inc_val = df[df["Type"] == "Income"]["Amount_MMK"].sum() / rate
    exp_val = df[df["Type"] == "Expense"]["Amount_MMK"].sum() / rate
    m1.metric(f"📥 {t('income')}", f"{curr_s}{inc_val:,.0f}")
    m2.metric(f"📤 {t('expense')}", f"{curr_s}{exp_val:,.0f}")
    m3.metric(f"💰 {t('saved')}", f"{curr_s}{(inc_val - exp_val):,.0f}")

# Row 3: Summary & History
st.divider()
row3_col1, row3_col2 = st.columns([1, 1.5])

with row3_col1:
    st.subheader("Summary")
    if not df.empty:
        df['Month'] = df['Date'].dt.strftime('%b')
        monthly = df.groupby('Month')['Amount_MMK'].sum().reset_index()
        # Horizontal Summary like the sketch
        st.dataframe(monthly.set_index('Month').T, use_container_width=True)

with row3_col2:
    st.subheader(t("history"))
    if not df.empty:
        # Show last 5 records neatly
        hist_df = df.sort_index(ascending=False).head(5)
        hist_df['Amount'] = (hist_df['Amount_MMK'] / rate).apply(lambda x: f"{curr_s}{x:,.0f}")
        st.table(hist_df[['Date', 'Type', 'Amount', 'Note']])
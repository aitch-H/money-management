import streamlit as st
import pandas as pd
import hashlib
import os
import datetime
import plotly.express as px
import time

# --- 1. Security & Data Setup ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

USER_DB, DATA_FILE = "users.csv", "sumal_records.csv"

# Settings သိမ်းဖို့ ကော်လံ (၂) ခု ထပ်တိုးထားပါတယ်
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["username", "password", "language", "currency"]).to_csv(USER_DB, index=False)
if not os.path.exists(DATA_FILE):
    pd.DataFrame(columns=["Date", "User", "Type", "Category", "Amount_MMK", "Note", "Input_Currency", "Input_Amount"]).to_csv(DATA_FILE, index=False)

# Preference တွေကို ဖိုင်ထဲမှာ သွားသိမ်းမယ့် function
def update_user_pref(u, lang, curr):
    users = pd.read_csv(USER_DB)
    users.loc[users['username'] == u, ['language', 'currency']] = [lang, curr]
    users.to_csv(USER_DB, index=False)

# --- 2. Page Config ---
st.set_page_config(page_title="SU-MAL", page_icon="💰", layout="wide")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'exchange_rates' not in st.session_state:
    st.session_state.exchange_rates = {'THB': 145.0, 'USD': 3500.0, 'MMK': 1.0}

# --- 3. Translations ---
TRANSLATIONS = {
    "en": {"app_title": "SU-MAL _ BUDGET TRACKER", "income": "Income", "expense": "Expense", "transfer": "Transfer", "saved": "Saved", "type": "Type", "cat": "Category", "amt": "Amount", "save": "Add Record", "history": "History"},
    "my": {"app_title": "SU-MAL _ ငွေစာရင်း စီမံခန့်ခွဲမှု", "income": "ဝင်ငွေ", "expense": "အသုံးစရိတ်", "transfer": "ပို့ငွေ", "saved": "လက်ကျန်", "type": "အမျိုးအစား", "cat": "အုပ်စု", "amt": "ပမာဏ", "save": "စာရင်းသွင်းမည်", "history": "မှတ်တမ်း"},
    "th": {"app_title": "SU-MAL _ แอปจัดการเงิน", "income": "รายได้", "expense": "ค่าใช้จ่าย", "transfer": "โอนเงิน", "saved": "เงินออม", "type": "ประเภท", "cat": "หมวดหมู่", "amt": "จำนวนเงิน", "save": "บันทึก", "history": "ประวัติ"}
}
CATS = {"Income": ["Salary", "Bonus", "Gift", "Other"], "Expense": ["Food", "Transport", "Shopping", "Bills", "Health", "Other"], "Transfer": ["Family", "Bank", "Investment"]}

def t(key): return TRANSLATIONS[st.session_state.language].get(key, key)

# --- 4. Login / Sign Up Page ---
if not st.session_state.logged_in:
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        st.title("💰 SU-MAL")
        auth_mode = st.tabs(["Login", "Sign Up"])
        
        with auth_mode[0]:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("Login", use_container_width=True):
                users = pd.read_csv(USER_DB)
                user_row = users[users['username'] == u]
                if not user_row.empty and check_hashes(p, user_row.iloc[0]['password']):
                    st.session_state.logged_in, st.session_state.user = True, u
                    # ဖိုင်ထဲက Settings တွေကို ဆွဲထုတ်မယ်
                    st.session_state.language = user_row.iloc[0]['language'] if pd.notna(user_row.iloc[0]['language']) else 'my'
                    st.session_state.base_currency = user_row.iloc[0]['currency'] if pd.notna(user_row.iloc[0]['currency']) else 'MMK'
                    st.rerun()
                else: st.error("Username သို့မဟုတ် Password မှားနေပါတယ်")
        
        with auth_mode[1]:
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password", type="password")
            if st.button("Create Account", use_container_width=True):
                users = pd.read_csv(USER_DB)
                if new_u and new_u not in users['username'].values:
                    # အကောင့်သစ်ဖွင့်ရင် Default settings တွေပါ တစ်ခါတည်းထည့်မယ်
                    pd.DataFrame([[new_u, make_hashes(new_p), 'my', 'MMK']]).to_csv(USER_DB, mode='a', header=False, index=False)
                    st.success("အကောင့်ဖွင့်ပြီးပါပြီ။ Login ပြန်ဝင်ပါ")
                else: st.warning("ဒီနာမည် ရှိပြီးသားပါ")

# --- 5. Main Dashboard ---
else:
    col_head, col_menu = st.columns([4, 1])
    col_head.title(t("app_title"))
    with col_menu.popover("☰ Menu"):
        st.write(f"👤 User: **{st.session_state.user}**")
        n_l = st.selectbox("🌐 Language", ["my", "en", "th"], index=["my", "en", "th"].index(st.session_state.language))
        n_c = st.selectbox("💱 Currency", ["MMK", "THB", "USD"], index=["MMK", "THB", "USD"].index(st.session_state.base_currency))
        
        # Setting ပြောင်းလိုက်တာနဲ့ ဖိုင်ထဲမှာပါ သွားသိမ်းမယ်
        if n_l != st.session_state.language or n_c != st.session_state.base_currency:
            st.session_state.language, st.session_state.base_currency = n_l, n_c
            update_user_pref(st.session_state.user, n_l, n_c)
            st.rerun()
            
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
    user_df = df[df["User"] == st.session_state.user]
    rate = st.session_state.exchange_rates.get(st.session_state.base_currency, 1.0)
    curr_s = {"USD": "$", "THB": "฿", "MMK": "K"}[st.session_state.base_currency]

    # Donut & Form
    row1_col1, row1_col2 = st.columns([1.2, 2])
    with row1_col1:
        st.subheader("Visual Analysis")
        if not user_df.empty:
            fig = px.pie(user_df, values="Amount_MMK", names="Type", hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False, height=220, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No records yet")

    with row1_col2:
        st.markdown("**ENTER YOUR TRANSACTION**")
        with st.container(border=True):
            f_col1, f_col2 = st.columns(2)
            t_ui = f_col1.selectbox(t("type"), [t("income"), t("expense"), t("transfer")])
            act_t = "Income" if t_ui == t("income") else "Expense" if t_ui == t("expense") else "Transfer"
            category = f_col2.selectbox(t("cat"), CATS[act_t])
            f_col3, f_col4 = st.columns(2)
            amt = f_col3.number_input(f"{t('amt')} ({curr_s})", min_value=0.0)
            entry_date = f_col4.date_input("Date", datetime.date.today())
            note = st.text_input(t("note"))
            if st.button(t("save"), type="primary", use_container_width=True):
                if amt > 0:
                    mmk_v = amt if st.session_state.base_currency == 'MMK' else amt * rate
                    new_row = pd.DataFrame([[entry_date, st.session_state.user, act_t, category, mmk_v, note, st.session_state.base_currency, amt]], columns=df.columns)
                    new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    st.success("Success!"); time.sleep(0.5); st.rerun()

    # Metrics
    st.divider()
    m1, m2, m3 = st.columns(3)
    if not user_df.empty:
        inc = user_df[user_df["Type"] == "Income"]["Amount_MMK"].sum() / rate
        exp = user_df[user_df["Type"] == "Expense"]["Amount_MMK"].sum() / rate
        m1.metric(f"📥 {t('income')}", f"{curr_s}{inc:,.0f}")
        m2.metric(f"📤 {t('expense')}", f"{curr_s}{exp:,.0f}")
        m3.metric(f"💰 {t('saved')}", f"{curr_s}{(inc - exp):,.0f}")

    # Summary & History
    st.divider()
    row3_col1, row3_col2 = st.columns([1, 1.5])
    with row3_col1:
        st.subheader("Summary")
        if not user_df.empty:
            user_df['Display_Amount'] = user_df['Amount_MMK'] / rate
            user_df['Month'] = user_df['Date'].dt.strftime('%b')
            monthly = user_df.groupby('Month')['Display_Amount'].sum().reset_index()
            monthly.columns = ['Month', f'Total ({curr_s})']
            st.dataframe(monthly.set_index('Month').T, use_container_width=True)
    with row3_col2:
        st.subheader(t("history"))
        if not user_df.empty:
            hist = user_df.sort_index(ascending=False).head(5)
            hist['Amount'] = (hist['Amount_MMK'] / rate).apply(lambda x: f"{curr_s}{x:,.0f}")
            st.table(hist[['Date', 'Type', 'Amount', 'Note']])
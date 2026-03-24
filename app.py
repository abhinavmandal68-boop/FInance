import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from datetime import datetime

# --- CONFIG & STYLING ---
st.set_page_config(page_title="WealthTrace AI", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION ---
MONGO_URI = st.secrets["MONGO_URI"]
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client["finance_analytics"]
collection = db["expenses"]

# --- APP LOGIC ---
st.title("📈 WealthTrace Analytics")
st.caption("Professional Grade Personal Finance Tracking")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Transaction", "📜 History"])

# --- TAB 2: DATA ENTRY ---
with tab2:
    st.subheader("New Entry")
    with st.container():
        col_a, col_b = st.columns(2)
        with col_a:
            date = st.date_input("Transaction Date", datetime.now())
            category = st.selectbox("Category", ["🏠 Rent", "🍔 Food", "⚡ Utilities", "🎬 Fun", "🚗 Transport", "🛍️ Shopping", "📦 Other"])
        with col_b:
            amount = st.number_input("Amount ($)", min_value=0.0)
            desc = st.text_input("Description (e.g., Starbucks)")

        if st.button("Securely Save Transaction"):
            if amount > 0:
                collection.insert_one({
                    "date": datetime(date.year, date.month, date.day),
                    "category": category,
                    "amount": amount,
                    "desc": desc
                })
                st.success("Transaction Synced to Cloud!")
                st.rerun()
            else:
                st.warning("Please enter an amount greater than 0.")

# --- LOAD DATA ---
data = list(collection.find())

if data:
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    with tab1:
        m1, m2, m3 = st.columns(3)
        total_spent = df['amount'].sum()
        m1.metric("Total Expenses", f"${total_spent:,.2f}")
        m2.metric("Avg. Transaction", f"${df['amount'].mean():,.2f}")
        m3.metric("Total Records", len(df))

        st.divider()

        c1, c2 = st.columns([1, 1])
        with c1:
            fig_pie = px.pie(df, values='amount', names='category',
                             title="Spending Distribution",
                             hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            df_trend = df.groupby('date')['amount'].sum().reset_index()
            fig_line = px.area(df_trend, x='date', y='amount', title="Daily Spending Trend",
                               line_shape='spline', color_discrete_sequence=['#007BFF'])
            st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("Transaction Ledger")
        display_df = df.drop(columns=['_id']).sort_values('date', ascending=False)
        st.dataframe(display_df, use_container_width=True)

        if st.button("Clear All Data (Careful!)"):
            collection.delete_many({})
            st.warning("Database Cleared.")
            st.rerun()

else:
    with tab1:
        st.info("The database is currently empty. Head over to the 'Add Transaction' tab to get started!")

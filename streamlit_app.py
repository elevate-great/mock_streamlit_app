# streamlit_app.py
import time
import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Sales Mini-Demo", page_icon="📈", layout="wide")
st.title("📈 Sales Mini-Demo")
st.caption("Tiny Streamlit app to demo charts, filters, and layout.")

# --- Sidebar controls
st.sidebar.header("Filters")
np.random.seed(42)
regions = ["North", "South", "East", "West"]
selected_regions = st.sidebar.multiselect("Regions", regions, default=regions)
n_months = st.sidebar.slider("Months of history", 6, 24, 12)

# --- Fake data
dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_months, freq="MS")
data = []
for r in regions:
    vals = np.maximum(0, np.random.normal(100_000, 20_000, size=n_months)).astype(int)
    data.append(pd.DataFrame({"date": dates, "region": r, "revenue": vals}))
df = pd.concat(data)
df = df[df["region"].isin(selected_regions)]

# --- KPIs
col1, col2, col3 = st.columns(3)
latest = df[df["date"] == df["date"].max()].groupby("region")["revenue"].sum().sum()
prev = df[df["date"] == df["date"].sort_values().unique()[-2]].groupby("region")["revenue"].sum().sum()
delta = (latest - prev) / prev * 100 if prev else 0
col1.metric("Latest month revenue", f"£{latest:,.0f}", f"{delta:+.1f}% vs prior")

rolling = df.groupby("date")["revenue"].sum().rolling(3).mean().iloc[-1]
col2.metric("3-mo rolling avg", f"£{rolling:,.0f}")

col3.metric("Active regions", f"{df['region'].nunique()}")

# --- Charts (built-ins are simplest)
st.subheader("Revenue trend")
trend = df.groupby("date")["revenue"].sum().reset_index().set_index("date")
st.line_chart(trend)

st.subheader("Revenue by region (latest month)")
latest_month = df["date"].max()
bars = df[df["date"] == latest_month].groupby("region")["revenue"].sum().sort_values(ascending=False)
st.bar_chart(bars)

# --- Simple interaction
st.subheader("Record viewer")
row = st.dataframe(df.sort_values(["date","region"]).reset_index(drop=True), use_container_width=True)
with st.expander("Simulate long-running task"):
    with st.spinner("Crunching numbers..."):
        time.sleep(1.5)
    st.success("Done!")

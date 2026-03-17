import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# טעינת נתונים
df = pd.read_csv("clients_data.csv")

# המרות
df["join_date"] = pd.to_datetime(df["join_date"])
df["churn_date"] = pd.to_datetime(df["churn_date"], errors="coerce")

# כותרת
st.title("📊 Customer Insights Dashboard")

# -----------------------
# פילטרים
# -----------------------
st.sidebar.header("Filters")

city = st.sidebar.multiselect("City", df["city"].unique(), default=df["city"].unique())
service = st.sidebar.multiselect("Service Type", df["service_type"].unique(), default=df["service_type"].unique())
status = st.sidebar.multiselect("Status", df["status"].unique(), default=df["status"].unique())

filtered_df = df[
    (df["city"].isin(city)) &
    (df["service_type"].isin(service)) &
    (df["status"].isin(status))
]

# -----------------------
# KPI
# -----------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Clients", len(filtered_df))
col2.metric("Avg Satisfaction", round(filtered_df["satisfaction"].mean(), 2))
col3.metric("Avg Response Time", round(filtered_df["response_time"].mean(), 2))

# -----------------------
# גרפים
# -----------------------

# נטישה לאורך זמן
churn_df = filtered_df.dropna(subset=["churn_date"])
churn_over_time = churn_df.groupby(churn_df["churn_date"].dt.to_period("M")).size().reset_index(name="count")
churn_over_time["churn_date"] = churn_over_time["churn_date"].astype(str)

fig1 = px.line(churn_over_time, x="churn_date", y="count", title="Churn Over Time")
st.plotly_chart(fig1, use_container_width=True)

# התפלגות שביעות רצון
fig2 = px.histogram(filtered_df, x="satisfaction", nbins=10, title="Satisfaction Distribution")
st.plotly_chart(fig2, use_container_width=True)

# Scatter
fig3 = px.scatter(filtered_df, x="response_time", y="satisfaction",
                  title="Response Time vs Satisfaction")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------
# כפתור תיקון client_id
# -----------------------
st.subheader("🔧 Fix Client IDs")

def fix_client_ids(data):
    fixed = data.sort_values(by="join_date").copy()
    fixed["client_id"] = ["C" + str(1000 + i) for i in range(len(fixed))]
    return fixed

if st.button("Generate Fixed Excel File"):
    fixed_df = fix_client_ids(df)
    fixed_df.to_excel("clients_data_fixed.xlsx", index=False)
    
    with open("clients_data_fixed.xlsx", "rb") as file:
        st.download_button(
            label="⬇️ Download Fixed File",
            data=file,
            file_name="clients_data_fixed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

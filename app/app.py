import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 לוח בקרה – נתוני לקוחות")

# -----------------------
# טעינת הנתונים
# -----------------------
df = pd.read_csv("clients_data.csv")

# המרה לתאריכים
df["תאריך_הצטרפות"] = pd.to_datetime(df["תאריך_הצטרפות"], errors="coerce")
df["תאריך_נטישה"] = pd.to_datetime(df["תאריך_נטישה"], errors="coerce")

# -----------------------
# פילטרים Sidebar
# -----------------------
st.sidebar.header("סינון")
city = st.sidebar.multiselect("עיר", df["עיר"].unique(), default=df["עיר"].unique())
service = st.sidebar.multiselect("סוג שירות", df["סוג_שירות"].unique(), default=df["סוג_שירות"].unique())
status = st.sidebar.multiselect("סטטוס", df["סטטוס"].unique(), default=df["סטטוס"].unique())

filtered_df = df[
    (df["עיר"].isin(city)) &
    (df["סוג_שירות"].isin(service)) &
    (df["סטטוס"].isin(status))
]

# -----------------------
# KPI
# -----------------------
col1, col2, col3 = st.columns(3)
col1.metric("סה״כ לקוחות", len(filtered_df))
col2.metric("שביעות רצון ממוצעת", round(filtered_df["שביעות_רצון"].mean(), 2))
col3.metric("זמן תגובה ממוצע (שעות)", round(filtered_df["זמן_תגובה_ממוצע_שעות"].mean(), 2))

# -----------------------
# גרפים
# -----------------------

# 1. נטישה לאורך זמן
churn_df = filtered_df.dropna(subset=["תאריך_נטישה"])
if not churn_df.empty:
    churn_over_time = churn_df.groupby(churn_df["תאריך_נטישה"].dt.to_period("M")).size().reset_index(name="count")
    churn_over_time["תאריך_נטישה"] = churn_over_time["תאריך_נטישה"].astype(str)
    fig1 = px.line(churn_over_time, x="תאריך_נטישה", y="count", title="נטישה לאורך זמן")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("אין נתוני נטישה עבור הסינון הנבחר.")

# 2. התפלגות שביעות רצון
fig2 = px.histogram(filtered_df, x="שביעות_רצון", nbins=10, title="התפלגות שביעות רצון")
st.plotly_chart(fig2, use_container_width=True)

# 3. Scatter: זמן תגובה מול שביעות רצון
fig3 = px.scatter(filtered_df, x="זמן_תגובה_ממוצע_שעות", y="שביעות_רצון",
                  title="זמן תגובה מול שביעות רצון")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------
# כפתור תיקון client_id
# -----------------------
st.subheader("🔧 תיקון מספרי לקוח (client_id) לפי סדר הצטרפות")

def fix_client_ids(data):
    fixed = data.sort_values(by="תאריך_הצטרפות").copy()
    fixed["client_id"] = ["C" + str(1000 + i) for i in range(len(fixed))]
    return fixed

if st.button("צור קובץ Excel מתוקן"):
    fixed_df = fix_client_ids(df)
    fixed_df.to_excel("clients_data_fixed.xlsx", index=False)
    
    with open("clients_data_fixed.xlsx", "rb") as file:
        st.download_button(
            label="⬇️ הורדת הקובץ המתוקן",
            data=file,
            file_name="clients_data_fixed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

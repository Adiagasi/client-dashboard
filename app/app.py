import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    layout="wide",
    page_title="לוח בקרה – נתוני לקוחות",
    page_icon="📊",
)

# RTL + Custom CSS
st.markdown("""
<style>
    html, body, [class*="css"] {
        direction: rtl;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main { background-color: #f0f2f6; }
    .block-container { padding-top: 1.5rem; }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        border-right: 5px solid;
        margin-bottom: 10px;
    }
    .kpi-card.blue  { border-color: #4361ee; }
    .kpi-card.green { border-color: #2ec4b6; }
    .kpi-card.orange{ border-color: #ff9f1c; }
    .kpi-card.red   { border-color: #e63946; }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1a1a2e; margin: 0; }
    .kpi-label { font-size: 0.85rem; color: #6c757d; margin: 0; }
    .kpi-icon  { font-size: 1.8rem; }
    
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 20px 0 8px 0;
        padding-right: 10px;
        border-right: 4px solid #4361ee;
    }
    
    /* Sidebar – light, readable */
    section[data-testid="stSidebar"] {
        background-color: #f8f9ff !important;
        border-left: 2px solid #e0e4ff;
    }
    section[data-testid="stSidebar"] * {
        color: #1a1a2e !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
        background-color: #4361ee !important;
    }
    section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {
        color: #ffffff !important;
    }

    /* Hide Streamlit Cloud "Manage App" + footer – all known selectors */
    #MainMenu                         { visibility: hidden !important; display: none !important; }
    footer                            { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"]         { visibility: hidden !important; display: none !important; }
    [data-testid="stDecoration"]      { visibility: hidden !important; display: none !important; }
    [data-testid="manage-app-button"] { visibility: hidden !important; display: none !important; }
    .stDeployButton                   { visibility: hidden !important; display: none !important; }
    .viewerBadge_container__1QSob     { visibility: hidden !important; display: none !important; }
    [class*="StatusWidget"]           { visibility: hidden !important; display: none !important; }
    [class*="toolbarActions"]         { visibility: hidden !important; display: none !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("clients_data.csv")
    df["תאריך_הצטרפות"] = pd.to_datetime(df["תאריך_הצטרפות"], dayfirst=True, errors="coerce")
    df["תאריך_נטישה"]    = pd.to_datetime(df["תאריך_נטישה"],    dayfirst=True, errors="coerce")
    df["שנת_הצטרפות"]    = df["תאריך_הצטרפות"].dt.year
    df["חודש_הצטרפות"]   = df["תאריך_הצטרפות"].dt.to_period("M").astype(str)
    return df

df = load_data()

# Plotly theme defaults
CHART_THEME   = "plotly_white"
COLOR_SEQ     = px.colors.qualitative.Vivid
COLOR_CHURN   = "#e63946"
COLOR_ACTIVE  = "#2ec4b6"

# -----------------------
# Sidebar Filters
# -----------------------
with st.sidebar:
    st.markdown("## 🔍 סינון נתונים")
    st.markdown("---")
    city    = st.multiselect("🏙️ עיר",        sorted(df["עיר"].unique()),          default=list(df["עיר"].unique()))
    service = st.multiselect("🛡️ סוג שירות",  sorted(df["סוג_שירות"].unique()),    default=list(df["סוג_שירות"].unique()))
    status  = st.multiselect("📌 סטטוס",       df["סטטוס"].unique(),               default=list(df["סטטוס"].unique()))
    st.markdown("---")
    st.caption("📁 clients_data.csv")

filtered_df = df[
    df["עיר"].isin(city) &
    df["סוג_שירות"].isin(service) &
    df["סטטוס"].isin(status)
]

# -----------------------
# Header
# -----------------------
st.markdown("## 📊 לוח בקרה – נתוני לקוחות")
st.caption(f"מציג **{len(filtered_df):,}** לקוחות מתוך {len(df):,} סה״כ")
st.markdown("---")

# -----------------------
# KPI Row
# -----------------------
total        = len(filtered_df)
active_pct   = (filtered_df["סטטוס"] == "פעיל").mean() * 100
avg_sat      = filtered_df["שביעות_רצון"].mean()
avg_response = filtered_df["זמן_תגובה_ממוצע_שעות"].mean()
churn_count  = (filtered_df["סטטוס"] == "לא פעיל").sum()

col1, col2, col3, col4 = st.columns(4)

def kpi_html(icon, value, label, color):
    return f"""
    <div class="kpi-card {color}">
        <div class="kpi-icon">{icon}</div>
        <p class="kpi-value">{value}</p>
        <p class="kpi-label">{label}</p>
    </div>"""

col1.markdown(kpi_html("👥", f"{total:,}", "סה״כ לקוחות", "blue"), unsafe_allow_html=True)
col2.markdown(kpi_html("✅", f"{active_pct:.1f}%", "לקוחות פעילים", "green"), unsafe_allow_html=True)
col3.markdown(kpi_html("⭐", f"{avg_sat:.2f}", "שביעות רצון ממוצעת", "orange"), unsafe_allow_html=True)
col4.markdown(kpi_html("⏱️", f"{avg_response:.1f}h", "זמן תגובה ממוצע", "red"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =======================
# ROW 1: Churn timeline + Status pie
# =======================
st.markdown('<p class="section-title">📉 ניתוח נטישה ופעילות</p>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    churn_df = filtered_df.dropna(subset=["תאריך_נטישה"])
    if not churn_df.empty:
        churn_over_time = (
            churn_df
            .groupby(churn_df["תאריך_נטישה"].dt.to_period("M"))
            .size()
            .reset_index(name="נטישות")
        )
        churn_over_time["תאריך"] = churn_over_time["תאריך_נטישה"].astype(str)
        fig_churn = px.area(
            churn_over_time, x="תאריך", y="נטישות",
            title="נטישה חודשית לאורך זמן",
            template=CHART_THEME,
            color_discrete_sequence=[COLOR_CHURN],
        )
        fig_churn.update_traces(line_width=2.5, fillcolor="rgba(230,57,70,0.15)")
        fig_churn.update_layout(
            title_font_size=15, hovermode="x unified",
            xaxis_title="חודש", yaxis_title="מספר נטישות",
            margin=dict(t=45, b=30, l=30, r=20),
        )
        st.plotly_chart(fig_churn, use_container_width=True)
    else:
        st.info("אין נתוני נטישה עבור הסינון הנבחר.")

with c2:
    status_counts = filtered_df["סטטוס"].value_counts().reset_index()
    status_counts.columns = ["סטטוס", "כמות"]
    fig_pie = px.pie(
        status_counts, names="סטטוס", values="כמות",
        title="פילוג סטטוס לקוחות",
        template=CHART_THEME,
        color="סטטוס",
        color_discrete_map={"פעיל": COLOR_ACTIVE, "לא פעיל": COLOR_CHURN},
        hole=0.45,
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label")
    fig_pie.update_layout(
        title_font_size=15,
        showlegend=False,
        margin=dict(t=45, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# =======================
# ROW 2: Satisfaction histogram + Service bar
# =======================
st.markdown('<p class="section-title">⭐ שביעות רצון ושירותים</p>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    fig_hist = px.histogram(
        filtered_df, x="שביעות_רצון", nbins=10,
        title="התפלגות שביעות רצון",
        template=CHART_THEME,
        color_discrete_sequence=["#4361ee"],
        text_auto=True,
    )
    fig_hist.update_layout(
        bargap=0.1, title_font_size=15,
        xaxis_title="ציון שביעות רצון (1–10)",
        yaxis_title="מספר לקוחות",
        margin=dict(t=45, b=30, l=30, r=20),
    )
    fig_hist.update_traces(marker_line_width=1, marker_line_color="white")
    st.plotly_chart(fig_hist, use_container_width=True)

with c4:
    service_sat = (
        filtered_df.groupby("סוג_שירות")["שביעות_רצון"]
        .mean()
        .reset_index()
        .sort_values("שביעות_רצון", ascending=True)
    )
    fig_bar = px.bar(
        service_sat, y="סוג_שירות", x="שביעות_רצון",
        orientation="h",
        title="שביעות רצון ממוצעת לפי סוג שירות",
        template=CHART_THEME,
        color="שביעות_רצון",
        color_continuous_scale="RdYlGn",
        range_color=[1, 10],
        text_auto=".2f",
    )
    fig_bar.update_layout(
        title_font_size=15, coloraxis_showscale=False,
        xaxis_title="ממוצע", yaxis_title="",
        margin=dict(t=45, b=30, l=10, r=20),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# =======================
# ROW 3: Scatter + City heatmap
# =======================
st.markdown('<p class="section-title">🔎 ניתוח מעמיק</p>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    bins   = [0, 15, 30, 50, 70, 101]
    labels = ["0-15", "15-30", "30-50", "50-70", "70+"]
    box_df = filtered_df.copy()
    box_df["טווח_תגובה"] = pd.cut(
        box_df["זמן_תגובה_ממוצע_שעות"], bins=bins, labels=labels, right=False
    )
    fig_box = px.box(
        box_df.dropna(subset=["טווח_תגובה"]),
        x="טווח_תגובה", y="שביעות_רצון",
        color="סטטוס",
        title="שביעות רצון לפי טווח זמן תגובה",
        template=CHART_THEME,
        color_discrete_map={"פעיל": COLOR_ACTIVE, "לא פעיל": COLOR_CHURN},
        points=False, notched=True,
        category_orders={"טווח_תגובה": labels},
    )
    fig_box.update_layout(
        title_font_size=15,
        xaxis_title="זמן תגובה (שעות)",
        yaxis_title="שביעות רצון (1-10)",
        legend_title_text="סטטוס",
        margin=dict(t=45, b=30, l=30, r=20),
    )
    st.plotly_chart(fig_box, use_container_width=True)


with c6:
    city_service = (
        filtered_df.groupby(["עיר", "סוג_שירות"])
        .size()
        .reset_index(name="כמות")
    )
    top_cities = filtered_df["עיר"].value_counts().head(8).index
    city_service_top = city_service[city_service["עיר"].isin(top_cities)]
    
    fig_heat = px.density_heatmap(
        city_service_top,
        x="סוג_שירות", y="עיר", z="כמות",
        title="התפלגות שירותים לפי עיר (TOP 8)",
        template=CHART_THEME,
        color_continuous_scale="Blues",
        text_auto=True,
    )
    fig_heat.update_layout(
        title_font_size=15,
        xaxis_title="סוג שירות",
        yaxis_title="עיר",
        margin=dict(t=45, b=60, l=30, r=20),
        xaxis_tickangle=-30,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# =======================
# ROW 4: Age distribution + Monthly joins
# =======================
st.markdown('<p class="section-title">📅 גיל ומגמות הצטרפות</p>', unsafe_allow_html=True)
c7, c8 = st.columns(2)

with c7:
    fig_age = px.histogram(
        filtered_df, x="גיל", nbins=12,
        color="מגדר",
        title="התפלגות גיל לפי מגדר",
        template=CHART_THEME,
        barmode="overlay",
        opacity=0.75,
        color_discrete_map={"זכר": "#4361ee", "נקבה": "#f72585"},
    )
    fig_age.update_layout(
        bargap=0.05, title_font_size=15,
        xaxis_title="גיל", yaxis_title="מספר לקוחות",
        legend_title_text="מגדר",
        margin=dict(t=45, b=30, l=30, r=20),
    )
    st.plotly_chart(fig_age, use_container_width=True)

with c8:
    joins_per_year = (
        filtered_df.groupby("שנת_הצטרפות")
        .size()
        .reset_index(name="הצטרפויות")
    )
    joins_per_year = joins_per_year.dropna(subset=["שנת_הצטרפות"])
    joins_per_year["שנת_הצטרפות"] = joins_per_year["שנת_הצטרפות"].astype(int)
    
    fig_joins = px.bar(
        joins_per_year, x="שנת_הצטרפות", y="הצטרפויות",
        title="הצטרפויות לפי שנה",
        template=CHART_THEME,
        color="הצטרפויות",
        color_continuous_scale="Blues",
        text_auto=True,
    )
    fig_joins.update_layout(
        title_font_size=15, coloraxis_showscale=False,
        xaxis_title="שנה", yaxis_title="מספר לקוחות",
        margin=dict(t=45, b=30, l=30, r=20),
    )
    st.plotly_chart(fig_joins, use_container_width=True)

# =======================
# Fix client_id section
# =======================
st.markdown("---")
st.markdown('<p class="section-title">🔧 תיקון מספרי לקוח</p>', unsafe_allow_html=True)

def fix_client_ids(data):
    fixed = data.sort_values(by="תאריך_הצטרפות").copy()
    fixed["client_id"] = ["C" + str(1000 + i) for i in range(len(fixed))]
    return fixed

if st.button("📥 צור קובץ Excel מתוקן", use_container_width=False):
    fixed_df = fix_client_ids(df)
    fixed_df.to_excel("clients_data_fixed.xlsx", index=False)
    with open("clients_data_fixed.xlsx", "rb") as file:
        st.download_button(
            label="⬇️ הורדת הקובץ המתוקן",
            data=file,
            file_name="clients_data_fixed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

st.markdown("<br><br>", unsafe_allow_html=True)

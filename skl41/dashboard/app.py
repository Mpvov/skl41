import streamlit as st
import plotly.express as px
import pandas as pd
from data_loader import load_data, filter_data, load_retention_csv, filter_retention_csv, load_roas_csv, filter_roas_csv, load_dau_csv, filter_dau_csv, load_changelog_v2
from metrics import (calculate_ad_revenue, calculate_ad_impressions, calculate_ecpm, calculate_dau,
                     calculate_retention_curve, calculate_ltv_curve, calculate_roas_curve,
                     get_kpi_at_day, calculate_sum_r, calculate_total_installs, calculate_total_ad_spend,
                     get_max_day_kpi, calculate_retention_by_date,
                     calculate_retention_kpis_from_csv, calculate_retention_by_date_from_csv,
                     calculate_ltv_kpis_from_csv, calculate_ltv_by_date_from_csv, calculate_roas_d30_kpis_v2, calculate_roas_d0_kpis_v2,
                     calculate_roas_by_date_from_csv, calculate_roas_d7_kpis_v2)

st.set_page_config(page_title="Game Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Enable drawing tools for all Plotly charts
PLOTLY_CONFIG = {
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
    'displayModeBar': True,
    'edits': {
        'shapePosition': True,
    }
}

# Update default shape layout to make drawn lines stand out (Red & thick)
def apply_drawing_layout(fig):
    fig.update_layout(
        newshape=dict(line_color='red', line_width=4, opacity=0.8)
    )
    return fig

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import streamlit as st
import plotly.express as px
import pandas as pd
from data_loader import load_data, filter_data, load_retention_csv, filter_retention_csv, load_roas_csv, filter_roas_csv, load_dau_csv, filter_dau_csv, load_changelog_v2
from metrics import (calculate_ad_revenue, calculate_ad_impressions, calculate_ecpm, calculate_dau,
                     calculate_retention_curve, calculate_ltv_curve, calculate_roas_curve,
                     get_kpi_at_day, calculate_sum_r, calculate_total_installs, calculate_total_ad_spend,
                     get_max_day_kpi, calculate_retention_by_date,
                     calculate_retention_kpis_from_csv, calculate_retention_by_date_from_csv,
                     calculate_ltv_kpis_from_csv, calculate_ltv_by_date_from_csv, calculate_roas_d30_kpis_v2, calculate_roas_d0_kpis_v2,
                     calculate_roas_by_date_from_csv, calculate_roas_d7_kpis_v2)

st.set_page_config(page_title="Game Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

# Enable drawing tools for all Plotly charts
PLOTLY_CONFIG = {
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
    'displayModeBar': True,
    'edits': {
        'shapePosition': True,
    }
}

# Update default shape layout to make drawn lines stand out (Red & thick)
def apply_drawing_layout(fig):
    fig.update_layout(
        newshape=dict(line_color='red', line_width=4, opacity=0.8)
    )
    return fig

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(BASE_DIR)

CSV_PATH = os.path.join(DATA_DIR, "dau_ad_imp_ad_rev_geo_channel.csv")
RETENTION_CSV_PATH = os.path.join(DATA_DIR, "retention&ltv.csv")
ROAS_CSV_PATH = os.path.join(DATA_DIR, "roas.csv")
DAU_CSV_PATH = os.path.join(DATA_DIR, "DAU.csv")
CHANGELOG_CSV_PATH = os.path.join(DATA_DIR, "changelog.csv")
AD_SPEND_CSV_PATH = os.path.join(DATA_DIR, "ad_spend.csv")
GAMEPLAY_CSV_PATH = os.path.join(DATA_DIR, "gameplay.csv")
TECHNICAL_CSV_PATH = os.path.join(DATA_DIR, "technical.csv")
LEVEL_A_CSV_PATH = os.path.join(DATA_DIR, "level_1_0_11.csv")
LEVEL_B_CSV_PATH = os.path.join(DATA_DIR, "level_1_1_0.csv")
HEART_CSV_PATH = os.path.join(DATA_DIR, "heart.csv")
PERCENT_DROP_CSV_PATH = os.path.join(DATA_DIR, "percent_drop_lose_heart.csv")

@st.cache_data
def get_unique_values(df, column_name):
    return sorted(df[column_name].dropna().unique().tolist())

def add_changelog_vlines(fig, changelog_df, x_min=None, x_max=None, show_ab_test=True, show_build=True):
    if changelog_df is None or changelog_df.empty:
        return
    for _, row in changelog_df.iterrows():
        date = row['Date live']
        types = str(row['Type']).lower()
        if pd.notnull(x_min) and date < pd.to_datetime(x_min):
            continue
        if pd.notnull(x_max) and date > pd.to_datetime(x_max):
            continue
            
        x_val = date.timestamp() * 1000
        if show_build and 'build' in types:
            fig.add_vline(x=x_val, line_width=1, line_dash="dash", line_color="red", annotation_text="Build", annotation_position="top left")
        if show_ab_test and ('a/b test' in types or 'off a/b test' in types):
            fig.add_vline(x=x_val, line_width=1, line_dash="dash", line_color="yellow", annotation_text=row['Type'], annotation_position="bottom left")

# Load data
with st.spinner('Loading data...'):
    raw_df = load_data(CSV_PATH)
    retention_raw_df = load_retention_csv(RETENTION_CSV_PATH)
    roas_raw_df = load_roas_csv(ROAS_CSV_PATH)
    dau_raw_df = load_dau_csv(DAU_CSV_PATH)
    changelog_df = load_changelog_v2(CHANGELOG_CSV_PATH)
    
    ad_spend_raw_df = pd.read_csv(AD_SPEND_CSV_PATH) if os.path.exists(AD_SPEND_CSV_PATH) else pd.DataFrame()
    if not ad_spend_raw_df.empty:
        ad_spend_raw_df['day'] = pd.to_datetime(ad_spend_raw_df['day'])
        
    gameplay_raw_df = pd.read_csv(GAMEPLAY_CSV_PATH) if os.path.exists(GAMEPLAY_CSV_PATH) else pd.DataFrame()
    if not gameplay_raw_df.empty:
        gameplay_raw_df['event_date'] = pd.to_datetime(gameplay_raw_df['event_date'])

    technical_raw_df = pd.read_csv(TECHNICAL_CSV_PATH) if os.path.exists(TECHNICAL_CSV_PATH) else pd.DataFrame()
    if not technical_raw_df.empty:
        technical_raw_df['event_date'] = pd.to_datetime(technical_raw_df['event_date'])

    # Load level comparison data
    from level_charts import (
        load_level_data, chart_cumulative_funnel_rate, chart_dropoff_delta,
        chart_continue_rate, chart_first_attempt_win_rate_delta,
        chart_fail_rate_and_attempts, chart_avg_progress, chart_win_duration_ribbon,
        chart_arpu_curve, chart_cumulative_impressions, chart_resource_source_sink,
        chart_t1_t2_ad_mix, chart_avg_imp_per_user, chart_ad_revenue_per_user
    )
    level_a_df, level_b_df = (pd.DataFrame(), pd.DataFrame())
    if os.path.exists(LEVEL_A_CSV_PATH) and os.path.exists(LEVEL_B_CSV_PATH):
        level_a_df, level_b_df = load_level_data(LEVEL_A_CSV_PATH, LEVEL_B_CSV_PATH)

    heart_df = pd.read_csv(HEART_CSV_PATH) if os.path.exists(HEART_CSV_PATH) else pd.DataFrame()
    
    HEART_METRICS_DROP_CSV_PATH = os.path.join(DATA_DIR, "heart_metrics_drop.csv")
    heart_metrics_drop_df = pd.read_csv(HEART_METRICS_DROP_CSV_PATH) if os.path.exists(HEART_METRICS_DROP_CSV_PATH) else pd.DataFrame()
    
    percent_drop_df = pd.DataFrame()
    if os.path.exists(PERCENT_DROP_CSV_PATH):
        percent_drop_df = pd.read_csv(PERCENT_DROP_CSV_PATH)
        for col in ['% losed user drop var', '% out of heart user drop var', '% losed user drop base']:
            if col in percent_drop_df.columns and percent_drop_df[col].dtype == object:
                percent_drop_df[col] = percent_drop_df[col].str.replace('%', '').astype(float)

if raw_df.empty:
    st.error("No data found. Please ensure the CSV file exists at the specified path.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.title("Global Filters")

min_date_raw = raw_df['event_date'].min().date() if not raw_df.empty else None
max_date_raw = raw_df['event_date'].max().date() if not raw_df.empty else None

min_date_ret = retention_raw_df['install_date'].min().date() if not retention_raw_df.empty else None
max_date_ret = retention_raw_df['install_date'].max().date() if not retention_raw_df.empty else None

min_date_roas = roas_raw_df['install_date'].min().date() if not roas_raw_df.empty else None
max_date_roas = roas_raw_df['install_date'].max().date() if not roas_raw_df.empty else None

all_min_dates = [d for d in [min_date_raw, min_date_ret, min_date_roas] if d is not None]
all_max_dates = [d for d in [max_date_raw, max_date_ret, max_date_roas] if d is not None]

min_date = min(all_min_dates) if all_min_dates else pd.to_datetime('today').date()
max_date = max(all_max_dates) if all_max_dates else pd.to_datetime('today').date()

# Set default start date to April 1st as requested
default_start_date = pd.to_datetime('2026-04-01').date()
if default_start_date < min_date or default_start_date > max_date:
    default_start_date = min_date

try:
    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        value=(default_start_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY"
    )
except ValueError:
    # Fallback if user selects incomplete date
    start_date, end_date = default_start_date, max_date

# Country Tier definitions (mobile gaming standard)
T1_COUNTRIES = ['US', 'GB', 'CA', 'AU', 'DE', 'FR', 'JP', 'KR', 'NZ', 'SE', 'NO', 'DK', 'FI', 'CH', 'AT', 'NL', 'BE', 'IE', 'SG', 'HK', 'TW']
T2_COUNTRIES = ['IT', 'ES', 'PT', 'BR', 'MX', 'AR', 'CL', 'CO', 'PE', 'PL', 'CZ', 'RO', 'HU', 'SK', 'HR', 'BG', 'RS', 'UA', 'RU', 'TR', 'SA', 'AE', 'IL', 'TH', 'MY', 'PH', 'ID', 'VN', 'IN', 'ZA', 'EG', 'NG', 'KE', 'GR', 'CN']

all_country_codes = get_unique_values(raw_df, 'country_code')
t1_in_data = [c for c in T1_COUNTRIES if c in all_country_codes]
t2_in_data = [c for c in T2_COUNTRIES if c in all_country_codes]
t3_in_data = [c for c in all_country_codes if c not in T1_COUNTRIES and c not in T2_COUNTRIES]

country_tier = st.sidebar.radio(
    "Country Tier",
    options=["All", "T1", "T2", "T3"],
    horizontal=True,
    help="T1: High eCPM (US, GB, CA, AU, DE, JP, KR...)\nT2: Mid-tier (BR, MX, IN, TH, VN, TR...)\nT3: Rest of world"
)

if country_tier == "T1":
    tier_default = t1_in_data
elif country_tier == "T2":
    tier_default = t2_in_data
elif country_tier == "T3":
    tier_default = t3_in_data
else:
    tier_default = []

countries = st.sidebar.multiselect("Country", options=all_country_codes, default=tier_default)
platforms = st.sidebar.multiselect("Platform", options=get_unique_values(raw_df, 'platform'))
ad_formats = st.sidebar.multiselect("Ad Format (Monetization only)", options=get_unique_values(raw_df, 'ad_format'))
ad_networks = st.sidebar.multiselect("Ad Network (Monetization only)", options=get_unique_values(raw_df, 'ad_network'))
media_sources = st.sidebar.multiselect("Media Source (Cohort only)", options=get_unique_values(retention_raw_df, 'media_source'))
campaigns = st.sidebar.multiselect("Campaign Name (Cohort only)", options=get_unique_values(retention_raw_df, 'campaign_name'))
show_build_lines = st.sidebar.checkbox("Show Build Events on Charts", value=True)
show_ab_test_lines = st.sidebar.checkbox("Show A/B Test Events on Charts", value=True)

# Apply filters
df = filter_data(raw_df, start_date, end_date, countries, platforms, ad_formats, ad_networks)
retention_df = filter_retention_csv(retention_raw_df, start_date, end_date, countries, media_sources, campaigns)
roas_df = filter_roas_csv(roas_raw_df, start_date, end_date, countries, media_sources, campaigns)
dau_df = filter_dau_csv(dau_raw_df, start_date, end_date, countries, platforms, media_sources, campaigns)

ad_spend_df = ad_spend_raw_df.copy()
if not ad_spend_df.empty:
    ad_spend_df = ad_spend_df[(ad_spend_df['day'] >= pd.to_datetime(start_date)) & (ad_spend_df['day'] <= pd.to_datetime(end_date))]

gameplay_df = gameplay_raw_df.copy()
if not gameplay_df.empty:
    gameplay_df = gameplay_df[(gameplay_df['event_date'] >= pd.to_datetime(start_date)) & (gameplay_df['event_date'] <= pd.to_datetime(end_date))]

technical_df = technical_raw_df.copy()
if not technical_df.empty:
    technical_df = technical_df[(technical_df['event_date'] >= pd.to_datetime(start_date)) & (technical_df['event_date'] <= pd.to_datetime(end_date))]

st.title("📊 Game Analytics Dashboard")

# --- TABS ---
tab_installs, tab_monetization, tab_retention, tab_business, tab_spend, tab_roas_eroas, tab_gameplay, tab_technical, tab_level, tab_combined, tab_heart = st.tabs(["🚀 Installs", "💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend", "⚖️ ROAS vs eROAS", "🎮 Gameplay", "⚙️ Technical", "📊 Level", "📋 Combined", "🫀 Heart Diagnostic"])

with tab_monetization:
    st.header("Monetization Overview")
    
    # KPIs
    total_rev = calculate_ad_revenue(df)
    total_imp = calculate_ad_impressions(df)
    overall_ecpm = calculate_ecpm(df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ad Revenue", f"${total_rev:,.2f}")
    col2.metric("Total Ad Impressions", f"{total_imp:,}")
    col3.metric("Overall eCPM", f"${overall_ecpm:,.2f}")
    
    st.divider()
    
    # Trend Charts
    st.subheader("Trends over Time")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        rev_trend = calculate_ad_revenue(df, group_by_col='event_date')
        if not rev_trend.empty:
            fig_rev = px.line(rev_trend, x='event_date', y='total_ad_revenue', title="Ad Revenue Trend")
            add_changelog_vlines(fig_rev, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_rev), use_container_width=True, config=PLOTLY_CONFIG)
            
    with col_chart2:
        imp_trend = calculate_ad_impressions(df, group_by_col='event_date')
        if not imp_trend.empty:
            fig_imp = px.line(imp_trend, x='event_date', y='total_ad_impression', title="Ad Impressions Trend")
            add_changelog_vlines(fig_imp, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_imp), use_container_width=True, config=PLOTLY_CONFIG)

    col_chart3, col_chart4 = st.columns(2)
            
    with col_chart3:
        ecpm_trend = calculate_ecpm(df, group_by_col='event_date')
        if not ecpm_trend.empty:
            fig_ecpm = px.line(ecpm_trend, x='event_date', y='ecpm', title="eCPM Trend")
            add_changelog_vlines(fig_ecpm, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_ecpm), use_container_width=True, config=PLOTLY_CONFIG)
            
    with col_chart4:
        if not ad_spend_df.empty and 'cost' in ad_spend_df.columns:
            spend_trend = ad_spend_df.groupby('day')['cost'].sum().reset_index()
            if not spend_trend.empty:
                fig_spend = px.line(spend_trend, x='day', y='cost', title="Ad Spend Trend")
                add_changelog_vlines(fig_spend, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
                st.plotly_chart(apply_drawing_layout(fig_spend), use_container_width=True, config=PLOTLY_CONFIG)
            
    st.divider()
    
    st.subheader("Ad Impressions / DAU")
    imp_trend_daily = calculate_ad_impressions(df, group_by_col='event_date')
    dau_trend_daily = calculate_dau(dau_df, group_by_col='event_date')
    if not imp_trend_daily.empty and not dau_trend_daily.empty:
        imp_dau_df = pd.merge(imp_trend_daily, dau_trend_daily, on='event_date', how='inner')
        if not imp_dau_df.empty:
            dau_col_name = 'total_dau' if 'total_dau' in imp_dau_df.columns else 'dau'
            imp_dau_df['imp_per_dau'] = imp_dau_df['total_ad_impression'] / imp_dau_df[dau_col_name]
            
            fig_imp_dau = px.line(imp_dau_df, x='event_date', y='imp_per_dau', title="Ad Impressions / DAU (Daily Trend)")
            fig_imp_dau.update_layout(yaxis_title="Impressions / DAU", hovermode='x unified')
            add_changelog_vlines(fig_imp_dau, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_imp_dau), use_container_width=True, config=PLOTLY_CONFIG)

    st.divider()
    
    st.subheader("Breakdown by Ad Format")
    col_fmt1, col_fmt2 = st.columns(2)
    with col_fmt1:
        rev_by_format = calculate_ad_revenue(df, group_by_col='ad_format')
        if not rev_by_format.empty:
            fig_format_rev = px.bar(rev_by_format, x='ad_format', y='total_ad_revenue', title="Revenue by Ad Format", color='ad_format')
            st.plotly_chart(apply_drawing_layout(fig_format_rev), use_container_width=True, config=PLOTLY_CONFIG)
    with col_fmt2:
        imp_by_format = calculate_ad_impressions(df, group_by_col='ad_format')
        if not imp_by_format.empty:
            fig_format_imp = px.bar(imp_by_format, x='ad_format', y='total_ad_impression', title="Impressions by Ad Format", color='ad_format')
            st.plotly_chart(apply_drawing_layout(fig_format_imp), use_container_width=True, config=PLOTLY_CONFIG)
        
    st.divider()
    
    st.subheader("Cohort Metrics (LTV)")
    st.info("💡 Note: LTV metrics are powered by `retention&ltv.csv`. Country, Media Source, and Campaign filters APPLY (Platform and Ad filters do not).")
    
    ltv_kpis = calculate_ltv_kpis_from_csv(retention_df)
    
    cl1, cl2, cl3, cl4, cl5 = st.columns(5)
    cl1.metric("LTV D1", f"${ltv_kpis.get('LTV D1', 0):,.3f}")
    cl2.metric("LTV D3", f"${ltv_kpis.get('LTV D3', 0):,.3f}")
    cl3.metric("LTV D7", f"${ltv_kpis.get('LTV D7', 0):,.3f}")
    cl4.metric("LTV D14", f"${ltv_kpis.get('LTV D14', 0):,.3f}")
    cl5.metric("LTV D30", f"${ltv_kpis.get('LTV D30', 0):,.3f}")
    
    ltv_by_date_df = calculate_ltv_by_date_from_csv(retention_df)
    if not ltv_by_date_df.empty:
        ltv_plot_cols = ['install_date']
        ltv_rename_map = {}
        for c, k in [('ltv_d1', 'LTV D1'), ('ltv_d3', 'LTV D3'), ('ltv_d7', 'LTV D7'), ('ltv_d14', 'LTV D14'), ('ltv_d30', 'LTV D30')]:
            if c in ltv_by_date_df.columns:
                ltv_plot_cols.append(c)
                ltv_rename_map[c] = k
                
        ltv_plot_df = ltv_by_date_df[ltv_plot_cols].copy()
        ltv_plot_df.rename(columns=ltv_rename_map, inplace=True)
        ltv_melted = ltv_plot_df.melt(id_vars=['install_date'], var_name='Metric', value_name='LTV')
        
        fig_ltv_date = px.line(ltv_melted, x='install_date', y='LTV', color='Metric', title="LTV by Install Date", markers=True)
        add_changelog_vlines(fig_ltv_date, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_ltv_date), use_container_width=True, config=PLOTLY_CONFIG)
        
        # Overall LTV Curve
        ltv_curve_data = pd.DataFrame({
            'Day': [1, 3, 7, 14, 30],
            'LTV': [ltv_kpis.get('LTV D1', 0), ltv_kpis.get('LTV D3', 0), ltv_kpis.get('LTV D7', 0), ltv_kpis.get('LTV D14', 0), ltv_kpis.get('LTV D30', 0)]
        })
        fig_ltv_curve = px.line(ltv_curve_data, x='Day', y='LTV', title="Overall Average LTV Curve", markers=True)
        st.plotly_chart(apply_drawing_layout(fig_ltv_curve), use_container_width=True, config=PLOTLY_CONFIG)

with tab_retention:
    st.header("Retention Overview")
    st.info("💡 Note: Retention metrics are currently powered by `retention&ltv.csv`. Country, Media Source, and Campaign filters APPLY to this tab (Platform and Ad filters do not).")
    
    kpis = calculate_retention_kpis_from_csv(retention_df)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("R1", f"{kpis.get('R1', 0):.1%}")
    col2.metric("R3", f"{kpis.get('R3', 0):.1%}")
    col3.metric("R7", f"{kpis.get('R7', 0):.1%}")
    col4.metric("R30", f"{kpis.get('R30', 0):.1%}")
    col5.metric("SumR 7", f"{kpis.get('SumR7', 0):.2f}")
    col6.metric("SumR 30", f"{kpis.get('SumR30', 0):.2f}")
    
    ret_by_date_df = calculate_retention_by_date_from_csv(retention_df)
    
    if not ret_by_date_df.empty:
        # Line chart for Retention Rates over time
        plot_cols = ['install_date']
        rename_map = {}
        for c, k in [('retention_r1', 'R1'), ('retention_r3', 'R3'), ('retention_r7', 'R7'), ('retention_r14', 'R14'), ('retention_r30', 'R30')]:
            if c in ret_by_date_df.columns:
                plot_cols.append(c)
                rename_map[c] = k
                
        plot_df = ret_by_date_df[plot_cols].copy()
        plot_df.rename(columns=rename_map, inplace=True)
        melted = plot_df.melt(id_vars=['install_date'], var_name='Metric', value_name='Rate')
        
        fig_ret_date = px.line(melted, x='install_date', y='Rate', color='Metric', title="Retention Rates by Install Date", markers=True)
        fig_ret_date.update_layout(yaxis_tickformat='.1%')
        add_changelog_vlines(fig_ret_date, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_ret_date), use_container_width=True, config=PLOTLY_CONFIG)
        
        # Line chart for SumR over time
        sum_plot_cols = ['install_date']
        sum_rename_map = {}
        for c, k in [('sumR3', 'SumR3'), ('sumR7', 'SumR7'), ('sumR14', 'SumR14'), ('sumR30', 'SumR30')]:
            if c in ret_by_date_df.columns:
                sum_plot_cols.append(c)
                sum_rename_map[c] = k
                
        if len(sum_plot_cols) > 1:
            sum_plot_df = ret_by_date_df[sum_plot_cols].copy()
            sum_plot_df.rename(columns=sum_rename_map, inplace=True)
            sum_melted = sum_plot_df.melt(id_vars=['install_date'], var_name='Metric', value_name='Value')
            
            fig_sum_date = px.line(sum_melted, x='install_date', y='Value', color='Metric', title="SumR by Install Date", markers=True)
            add_changelog_vlines(fig_sum_date, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_sum_date), use_container_width=True, config=PLOTLY_CONFIG)

        col_sum_1, col_sum_2 = st.columns(2)
        with col_sum_1:
            if not retention_df.empty:
                dow_df = retention_df.copy()
                if not pd.api.types.is_datetime64_any_dtype(dow_df['install_date']):
                    dow_df['install_date'] = pd.to_datetime(dow_df['install_date'])
                dow_df['dow'] = dow_df['install_date'].dt.day_name()
                
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                sumr_kpis = []
                max_date = dow_df['install_date'].max()
                maturity_days_sumr = {'sumR3': 3, 'sumR7': 7, 'sumR14': 14, 'sumR30': 30}
                
                for dow in days_order:
                    day_df = dow_df[dow_df['dow'] == dow]
                    row = {'Day of Week': dow}
                    for col, key in [('sumR3', 'SumR3'), ('sumR7', 'SumR7'), ('sumR14', 'SumR14'), ('sumR30', 'SumR30')]:
                        if col in day_df.columns:
                            req_days = maturity_days_sumr.get(col, 0)
                            mature_date_end = max_date - pd.Timedelta(days=req_days + 1)
                            mature_df = day_df[day_df['install_date'] <= mature_date_end]
                            total_users = mature_df['total_cohort_users'].sum()
                            if total_users > 0:
                                row[key] = (mature_df[col] * mature_df['total_cohort_users']).sum() / total_users
                            else:
                                row[key] = None
                    sumr_kpis.append(row)
                
                sumr_plot_df = pd.DataFrame(sumr_kpis)
                if not sumr_plot_df.empty:
                    sumr_melted_dow = sumr_plot_df.melt(id_vars=['Day of Week'], var_name='Metric', value_name='SumR Value')
                    sumr_melted_dow = sumr_melted_dow.dropna(subset=['SumR Value'])
                    fig_sumr_dow = px.line(sumr_melted_dow, x='Day of Week', y='SumR Value', color='Metric', title="SumR by Day of Week", markers=True)
                    st.plotly_chart(apply_drawing_layout(fig_sumr_dow), use_container_width=True, config=PLOTLY_CONFIG)
        
        col_ret_1, col_ret_2 = st.columns(2)
        with col_ret_1:
            # Overall Retention Curve using the calculated average KPIs
            curve_data = pd.DataFrame({
                'Day': [1, 3, 7, 14, 30],
                'Retention Rate': [kpis.get('R1', 0), kpis.get('R3', 0), kpis.get('R7', 0), kpis.get('R14', 0), kpis.get('R30', 0)]
            })
            fig_ret = px.line(curve_data, x='Day', y='Retention Rate', title="Overall Average Retention Curve", markers=True)
            fig_ret.update_layout(yaxis_tickformat='.1%')
            st.plotly_chart(apply_drawing_layout(fig_ret), use_container_width=True, config=PLOTLY_CONFIG)

        with col_ret_2:
            if not retention_df.empty:
                dow_df = retention_df.copy()
                if not pd.api.types.is_datetime64_any_dtype(dow_df['install_date']):
                    dow_df['install_date'] = pd.to_datetime(dow_df['install_date'])
                dow_df['dow'] = dow_df['install_date'].dt.day_name()
                
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dow_kpis = []
                max_date = dow_df['install_date'].max()
                maturity_days = {'retention_r1': 1, 'retention_r3': 3, 'retention_r7': 7, 'retention_r14': 14, 'retention_r30': 30}
                
                for dow in days_order:
                    day_df = dow_df[dow_df['dow'] == dow]
                    row = {'Day of Week': dow}
                    for col, key in [('retention_r1', 'R1'), ('retention_r3', 'R3'), ('retention_r7', 'R7'), ('retention_r14', 'R14'), ('retention_r30', 'R30')]:
                        if col in day_df.columns:
                            req_days = maturity_days.get(col, 0)
                            mature_date_end = max_date - pd.Timedelta(days=req_days + 1)
                            mature_df = day_df[day_df['install_date'] <= mature_date_end]
                            total_users = mature_df['total_cohort_users'].sum()
                            if total_users > 0:
                                row[key] = (mature_df[col] * mature_df['total_cohort_users']).sum() / total_users
                            else:
                                row[key] = None
                    dow_kpis.append(row)
                
                dow_plot_df = pd.DataFrame(dow_kpis)
                if not dow_plot_df.empty:
                    dow_melted = dow_plot_df.melt(id_vars=['Day of Week'], var_name='Metric', value_name='Retention Rate')
                    dow_melted = dow_melted.dropna(subset=['Retention Rate'])
                    fig_dow = px.line(dow_melted, x='Day of Week', y='Retention Rate', color='Metric', title="Retention by Day of Week", markers=True)
                    fig_dow.update_layout(yaxis_tickformat='.1%')
                    st.plotly_chart(apply_drawing_layout(fig_dow), use_container_width=True, config=PLOTLY_CONFIG)

with tab_business:
    st.header("Business & Scale Overview")
    
    total_dau = calculate_dau(dau_df)
    total_installs = int(ad_spend_df['installs'].sum()) if not ad_spend_df.empty and 'installs' in ad_spend_df.columns else 0
    total_ad_spend = ad_spend_df['cost'].sum() if not ad_spend_df.empty and 'cost' in ad_spend_df.columns else 0
    
    st.subheader("High-Level KPIs")
    num_days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1
    if num_days < 1: num_days = 1
    avg_dau = total_dau / num_days
    avg_installs = total_installs / num_days

    row1_c1, row1_c2, row1_c3, row1_c4, row1_c5 = st.columns(5)
    row1_c1.metric("Total DAU", f"{total_dau:,}")
    row1_c2.metric("Avg DAU / Day", f"{avg_dau:,.0f}")
    row1_c3.metric("Total Installs", f"{total_installs:,}")
    row1_c4.metric("Avg Installs / Day", f"{avg_installs:,.0f}")
    row1_c5.metric("Total Ad Spend", f"${total_ad_spend:,.2f}")
    
    st.divider()
    st.subheader("ROAS KPIs")
    st.caption("Select custom date ranges for ROAS metrics (ignores global sidebar date filter).")
    
    # Calculate default mature dates based on raw data
    max_date_roas_val = roas_raw_df['install_date'].max() if not roas_raw_df.empty else pd.to_datetime('today')
    default_d0_end = max_date_roas_val - pd.Timedelta(days=2)
    default_d0_start = default_d0_end - pd.Timedelta(days=6)

    default_d7_end = max_date_roas_val - pd.Timedelta(days=9)
    default_d7_start = default_d7_end - pd.Timedelta(days=6)

    default_d30_end = max_date_roas_val - pd.Timedelta(days=39)
    default_d30_start = default_d30_end - pd.Timedelta(days=13)

    date_col0, date_col1, date_col2 = st.columns(3)
    with date_col0:
        try:
            d0_picker = st.date_input(
                "D0 Cohort Date Range",
                value=(default_d0_start.date(), default_d0_end.date()),
                key="d0_date_picker"
            )
            if len(d0_picker) == 2:
                d0_picker_start, d0_picker_end = d0_picker
            else:
                d0_picker_start, d0_picker_end = d0_picker[0], d0_picker[0]
        except Exception:
            d0_picker_start, d0_picker_end = default_d0_start.date(), default_d0_end.date()

    with date_col1:
        try:
            d7_picker = st.date_input(
                "D7 Cohort Date Range",
                value=(default_d7_start.date(), default_d7_end.date()),
                key="d7_date_picker"
            )
            if len(d7_picker) == 2:
                d7_picker_start, d7_picker_end = d7_picker
            else:
                d7_picker_start, d7_picker_end = d7_picker[0], d7_picker[0]
        except Exception:
            d7_picker_start, d7_picker_end = default_d7_start.date(), default_d7_end.date()

    with date_col2:
        try:
            d30_picker = st.date_input(
                "D30 Cohort Date Range",
                value=(default_d30_start.date(), default_d30_end.date()),
                key="d30_date_picker"
            )
            if len(d30_picker) == 2:
                d30_picker_start, d30_picker_end = d30_picker
            else:
                d30_picker_start, d30_picker_end = d30_picker[0], d30_picker[0]
        except Exception:
            d30_picker_start, d30_picker_end = default_d30_start.date(), default_d30_end.date()

    campaign_roas_d0, blended_roas_d0, d0_start, d0_end = calculate_roas_d0_kpis_v2(
        roas_raw_df, ad_spend_raw_df, days=7, start_date=d0_picker_start, end_date=d0_picker_end
    )

    campaign_roas_d7, blended_roas_d7, d7_start, d7_end = calculate_roas_d7_kpis_v2(
        roas_raw_df, ad_spend_raw_df, days=7, start_date=d7_picker_start, end_date=d7_picker_end
    )

    solid_roas_d30, blended_roas_d30, d30_start, d30_end = calculate_roas_d30_kpis_v2(
        roas_raw_df, ad_spend_raw_df, days=14, start_date=d30_picker_start, end_date=d30_picker_end
    )

    row2_c1, row2_c2, row2_c3, row2_c4, row2_c5, row2_c6 = st.columns(6)
    
    if d0_start is not None and d0_end is not None:
        d0_label_suffix = f" ({pd.to_datetime(d0_start).strftime('%m/%d')}-{pd.to_datetime(d0_end).strftime('%m/%d')})"
    else:
        d0_label_suffix = ""

    row2_c1.metric(f"Campaign ROAS D0{d0_label_suffix}", f"{campaign_roas_d0:.1%}")
    row2_c2.metric(f"Blended ROAS D0{d0_label_suffix}", f"{blended_roas_d0:.1%}")

    if d7_start is not None and d7_end is not None:
        d7_label_suffix = f" ({pd.to_datetime(d7_start).strftime('%m/%d')}-{pd.to_datetime(d7_end).strftime('%m/%d')})"
    else:
        d7_label_suffix = ""

    row2_c3.metric(f"Campaign ROAS D7{d7_label_suffix}", f"{campaign_roas_d7:.1%}")
    row2_c4.metric(f"Blended ROAS D7{d7_label_suffix}", f"{blended_roas_d7:.1%}")

    if d30_start is not None and d30_end is not None:
        d30_label_suffix = f" ({pd.to_datetime(d30_start).strftime('%m/%d')}-{pd.to_datetime(d30_end).strftime('%m/%d')})"
    else:
        d30_label_suffix = ""

    row2_c5.metric(f"Campaign ROAS D30{d30_label_suffix}", f"{solid_roas_d30:.1%}")
    row2_c6.metric(f"Blended ROAS D30{d30_label_suffix}", f"{blended_roas_d30:.1%}")
    
    dau_trend = calculate_dau(dau_df, group_by_col='event_date')
    if not dau_trend.empty:
        dau_col_name = 'total_dau' if 'total_dau' in dau_trend.columns else 'dau'
        y_cols = [dau_col_name]
        if 'new_users' in dau_trend.columns:
            y_cols.append('new_users')
        if 'return_users' in dau_trend.columns:
            y_cols.append('return_users')
            
        if 'new_users' in dau_trend.columns:
            fig_installs = px.line(dau_trend, x='event_date', y='new_users', title="Installs Trend (New Users)")
            fig_installs.update_layout(yaxis_title='Installs', hovermode='x unified')
            add_changelog_vlines(fig_installs, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_installs), use_container_width=True, config=PLOTLY_CONFIG)

        fig_dau = px.line(dau_trend, x='event_date', y=y_cols, title="DAU Trend (Total vs New vs Return)")
        fig_dau.update_layout(legend_title_text='User Type', yaxis_title='Users', hovermode='x unified')
        add_changelog_vlines(fig_dau, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_dau), use_container_width=True, config=PLOTLY_CONFIG)
        
    roas_date_filtered_df = roas_raw_df.copy()
    if not roas_date_filtered_df.empty:
        roas_date_filtered_df['install_date'] = pd.to_datetime(roas_date_filtered_df['install_date'])
        roas_date_filtered_df = roas_date_filtered_df[(roas_date_filtered_df['install_date'] >= pd.to_datetime(start_date)) & (roas_date_filtered_df['install_date'] <= pd.to_datetime(end_date))]
    roas_trend_df = calculate_roas_by_date_from_csv(roas_date_filtered_df, ad_spend_raw_df)
    
    # Filter only D0, D7, D30 for charts so it doesn't get cluttered
    if not roas_trend_df.empty:
        keep_cols = ['install_date']
        for col in roas_trend_df.columns:
            if 'D0' in col or 'D7' in col or 'D30' in col:
                keep_cols.append(col)
        roas_trend_df = roas_trend_df[keep_cols]
    if not roas_trend_df.empty:
        # Chart 1: Campaign ROAS D7 / D30
        campaign_cols = [c for c in roas_trend_df.columns if c.startswith('Campaign')]
        if campaign_cols:
            campaign_melted = roas_trend_df.melt(id_vars=['install_date'], value_vars=campaign_cols, var_name='Metric', value_name='ROAS')
            fig_campaign = px.line(campaign_melted, x='install_date', y='ROAS', color='Metric', title="Campaign ROAS Trend (Paid Only)", markers=True)
            fig_campaign.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="100% Break-even")
            fig_campaign.update_layout(yaxis_tickformat='.1%')
            add_changelog_vlines(fig_campaign, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_campaign), use_container_width=True, config=PLOTLY_CONFIG)
            
        # Chart 2: Blended ROAS D7 / D30 (eROAS)
        blended_cols = [c for c in roas_trend_df.columns if c.startswith('Blended')]
        if blended_cols:
            blended_melted = roas_trend_df.melt(id_vars=['install_date'], value_vars=blended_cols, var_name='Metric', value_name='ROAS')
            fig_blended = px.line(blended_melted, x='install_date', y='ROAS', color='Metric', title="eROAS Trend (Blended: Paid + Organic)", markers=True)
            fig_blended.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="100% Break-even")
            fig_blended.update_layout(yaxis_tickformat='.1%')
            add_changelog_vlines(fig_blended, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_blended), use_container_width=True, config=PLOTLY_CONFIG)


with tab_spend:
    st.header("Ad Spend Analysis")

    if roas_df.empty:
        st.info("No ROAS/Ad Spend data available.")
    else:
        # 1. Stacked Bar Chart by Channel
        st.subheader("1. Ad Spend by Channel")
        spend_by_channel = roas_df.groupby(['install_date', 'media_source'], as_index=False)['cohort_ad_spend'].sum()
        fig_channel = px.bar(spend_by_channel, x='install_date', y='cohort_ad_spend', color='media_source', title="Ad Spend by Channel")
        fig_channel.update_layout(yaxis_title="Ad Spend ($)", xaxis_title="Date", barmode='stack', hovermode='x unified')
        add_changelog_vlines(fig_channel, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_channel), use_container_width=True, config=PLOTLY_CONFIG)

        # 2. Top 5 Countries Stacked Bar
        st.subheader("2. Ad Spend by Top 5 Countries")
        top_5_countries = roas_df.groupby('country_code')['cohort_ad_spend'].sum().nlargest(5).index.tolist()
        roas_df_mapped = roas_df.copy()
        roas_df_mapped['mapped_country'] = roas_df_mapped['country_code'].apply(lambda c: c if c in top_5_countries else 'Others')
        spend_by_country = roas_df_mapped.groupby(['install_date', 'mapped_country'], as_index=False)['cohort_ad_spend'].sum()
        
        fig_country = px.bar(spend_by_country, x='install_date', y='cohort_ad_spend', color='mapped_country', title="Ad Spend by Top 5 Countries")
        fig_country.update_layout(yaxis_title="Ad Spend ($)", xaxis_title="Date", barmode='stack', hovermode='x unified')
        add_changelog_vlines(fig_country, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_country), use_container_width=True, config=PLOTLY_CONFIG)

        # 3. Combo Chart: Ad Spend (Bar) + Avg CPI / ROAS D7 (Line)
        st.subheader("3. Efficiency: Ad Spend vs Performance")
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        def agg_eff(x):
            tot_spend = x['cohort_ad_spend'].sum()
            tot_users = x['total_cohort_users'].sum()
            avg_cpi = tot_spend / tot_users if tot_users > 0 else 0
            tot_rev_d7 = (x['roas_d7'] * x['cohort_ad_spend']).sum()
            roas_d7_avg = tot_rev_d7 / tot_spend if tot_spend > 0 else 0
            return pd.Series({'cohort_ad_spend': tot_spend, 'roas_d7_avg': roas_d7_avg, 'avg_cpi': avg_cpi})
            
        daily_eff = roas_df.groupby('install_date').apply(agg_eff, include_groups=False).reset_index()

        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_combo.add_trace(
            go.Bar(x=daily_eff['install_date'], y=daily_eff['cohort_ad_spend'], name="Ad Spend ($)", opacity=0.7),
            secondary_y=False,
        )
        fig_combo.add_trace(
            go.Scatter(x=daily_eff['install_date'], y=daily_eff['roas_d7_avg'], name="ROAS D7", mode='lines+markers', line=dict(width=3, color='orange')),
            secondary_y=True,
        )
        fig_combo.update_layout(title="Ad Spend vs ROAS D7", hovermode='x unified')
        fig_combo.update_yaxes(title_text="Ad Spend ($)", secondary_y=False)
        fig_combo.update_yaxes(title_text="ROAS D7", tickformat='.1%', secondary_y=True)
        add_changelog_vlines(fig_combo, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_combo), use_container_width=True, config=PLOTLY_CONFIG)

        # 4. Bubble Chart for Campaign (ROAS D7 vs Ad Spend)
        st.subheader("4. Campaign Performance (Bubble Chart)")
        
        def agg_camp(x):
            tot_spend = x['cohort_ad_spend'].sum()
            tot_users = x['total_cohort_users'].sum()
            tot_rev_d7 = (x['roas_d7'] * x['cohort_ad_spend']).sum()
            roas_d7_avg = tot_rev_d7 / tot_spend if tot_spend > 0 else 0
            return pd.Series({
                'cohort_ad_spend': tot_spend, 
                'total_cohort_users': tot_users,
                'roas_d7': roas_d7_avg
            })
            
        camp_perf = roas_df.groupby(['campaign_name', 'media_source']).apply(agg_camp, include_groups=False).reset_index()
        
        fig_bubble = px.scatter(camp_perf, x='roas_d7', y='cohort_ad_spend', size='total_cohort_users', color='media_source',
                                hover_name='campaign_name', title="Campaigns: ROAS D7 vs Ad Spend",
                                size_max=60)
        fig_bubble.add_vline(x=1.0, line_dash="dash", line_color="green", annotation_text="100% Break-even")
        fig_bubble.update_layout(xaxis_title="ROAS D7", yaxis_title="Ad Spend ($)", xaxis_tickformat='.1%')
        st.plotly_chart(apply_drawing_layout(fig_bubble), use_container_width=True, config=PLOTLY_CONFIG)

with tab_installs:
    st.header("Installs Overview")
    
    if dau_df.empty:
        st.warning("No DAU data available for the selected filters.")
    else:
        # Chart 1: Installs Trend by Channel (Organic vs Non-Organic)
        st.subheader("Installs by Traffic Type (Organic vs Non-Organic)")
        organic_channels = ['organic', '(organic)', 'google_organic_search']
        
        installs_traffic_df = dau_df.copy()
        if 'channel' in installs_traffic_df.columns:
            installs_traffic_df['Traffic Type'] = installs_traffic_df['channel'].apply(
                lambda x: 'Organic' if pd.notna(x) and str(x).lower() in organic_channels else 'Non-Organic'
            )
            traffic_trend = installs_traffic_df.groupby(['event_date', 'Traffic Type'])['new_users'].sum().reset_index()
            
            # Add 'All' category
            all_trend = traffic_trend.groupby('event_date')['new_users'].sum().reset_index()
            all_trend['Traffic Type'] = 'All'
            
            traffic_trend_final = pd.concat([traffic_trend, all_trend], ignore_index=True)
            
            fig_traffic = px.line(traffic_trend_final, x='event_date', y='new_users', color='Traffic Type', 
                                title="Installs Trend (All vs Organic vs Non-Organic)", markers=True)
            add_changelog_vlines(fig_traffic, changelog_df, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_traffic), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.warning("No channel data available.")

        # Chart 2: Installs Trend by Country
        st.subheader("Installs Trend by Country (Top 5 & Others)")
        if 'country_code' in dau_df.columns:
            installs_country_df = dau_df.copy()
            top_countries = installs_country_df.groupby('country_code')['new_users'].sum().nlargest(5).index
            
            installs_country_df['Country Group'] = installs_country_df['country_code'].apply(
                lambda x: x if x in top_countries else 'Others'
            )
            country_trend = installs_country_df.groupby(['event_date', 'Country Group'])['new_users'].sum().reset_index()
            
            fig_country = px.area(country_trend, x='event_date', y='new_users', color='Country Group',
                                title="Installs Trend by Country")
            add_changelog_vlines(fig_country, changelog_df, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_country), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.warning("No country data available.")

with tab_roas_eroas:
    st.header("ROAS vs eROAS (D0, D7, D30)")
    st.markdown("Quy tắc tính: **ROAS** = LTV(Paid) / CPI(Paid) | **eROAS** = LTV(All) / CPI(Paid). Nếu CPI = 0 thì không vẽ (tránh lỗi chia 0). Chỉ tính dữ liệu đã đủ độ chín (Maturity).")
    
    df_roas = pd.read_csv(RETENTION_CSV_PATH)
    organic_sources = ['organic', '(organic)', 'google_organic_search']
    df_roas['is_paid'] = ~df_roas['media_source'].str.lower().isin(organic_sources)
    max_date = pd.to_datetime(df_roas['install_date'].max())
    
    df_roas['date'] = pd.to_datetime(df_roas['install_date'])
    df_roas['week'] = df_roas['date'].dt.to_period('W').apply(lambda r: r.start_time)
    
    import plotly.express as px
    
    for d in [0, 7, 30]:
        st.subheader(f"Metrics D{d}")
        mature_date = max_date - pd.Timedelta(days=d)
        df_mature = df_roas[df_roas['date'] <= mature_date]
        
        if df_mature.empty:
            st.warning(f"Không đủ dữ liệu cho D{d} (Cần cài đặt trước ngày {mature_date.strftime('%Y-%m-%d')})")
            continue
            
        ltv_col = f'ltv_d{d}'
        if ltv_col not in df_mature.columns:
            continue
            
        def agg_roas(group):
            paid_group = group[group['is_paid']]
            paid_users = paid_group['total_cohort_users'].sum()
            paid_spend = paid_group['cohort_ad_spend'].sum()
            paid_rev = (paid_group['total_cohort_users'] * paid_group[ltv_col]).sum()
            
            paid_ltv = paid_rev / paid_users if paid_users > 0 else 0
            paid_cpi = paid_spend / paid_users if paid_users > 0 else 0
            
            all_users = group['total_cohort_users'].sum()
            all_rev = (group['total_cohort_users'] * group[ltv_col]).sum()
            all_ltv = all_rev / all_users if all_users > 0 else 0
            
            if paid_cpi == 0:
                return pd.Series({'ROAS': float('nan'), 'eROAS': float('nan')})
            return pd.Series({
                'ROAS': paid_ltv / paid_cpi,
                'eROAS': all_ltv / paid_cpi
            })

        # Daily
        daily_res = df_mature.groupby('date').apply(agg_roas, include_groups=False).reset_index()
        fig_daily = px.line(daily_res, x='date', y=['ROAS', 'eROAS'], title=f"Daily ROAS D{d} vs eROAS D{d}", markers=True)
        fig_daily.update_yaxes(tickformat='.1%')
        add_changelog_vlines(fig_daily, changelog_df, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_daily), use_container_width=True, config=PLOTLY_CONFIG)
        
        # Weekly
        weekly_res = df_mature.groupby('week').apply(agg_roas, include_groups=False).reset_index()
        fig_weekly = px.line(weekly_res, x='week', y=['ROAS', 'eROAS'], title=f"Weekly ROAS D{d} vs eROAS D{d}", markers=True)
        fig_weekly.update_yaxes(tickformat='.1%')
        add_changelog_vlines(fig_weekly, changelog_df, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_weekly), use_container_width=True, config=PLOTLY_CONFIG)

    st.markdown("---")
    st.header("🔍 Phân tích chuyên sâu (Insights)")
    
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    df_mature_d0 = df_roas[df_roas['date'] <= max_date]
    
    # --- 1. Combo Chart ---
    st.markdown("### 1. Combo Chart: Cost vs ROAS (Weekly)")
    st.markdown("Hiển thị tương quan trực quan giữa Chi phí (Cột) và ROAS D0, D7, D14 (Đường) qua từng tuần.")
    
    def agg_combo(group):
        paid_group = group[group['is_paid']]
        paid_users = paid_group['total_cohort_users'].sum()
        paid_spend = paid_group['cohort_ad_spend'].sum()
        paid_cpi = paid_spend / paid_users if paid_users > 0 else 0
        
        # D0
        paid_rev_d0 = (paid_group['total_cohort_users'] * paid_group['ltv_d0']).sum()
        roas_d0 = (paid_rev_d0 / paid_users) / paid_cpi if paid_cpi > 0 and paid_users > 0 else float('nan')
        
        # D7
        if 'ltv_d7' in paid_group.columns and group['date'].max() <= max_date - pd.Timedelta(days=7):
            paid_rev_d7 = (paid_group['total_cohort_users'] * paid_group['ltv_d7']).sum()
            roas_d7 = (paid_rev_d7 / paid_users) / paid_cpi if paid_cpi > 0 and paid_users > 0 else float('nan')
        else:
            roas_d7 = float('nan')
            
        # D14
        if 'ltv_d14' in paid_group.columns and group['date'].max() <= max_date - pd.Timedelta(days=14):
            paid_rev_d14 = (paid_group['total_cohort_users'] * paid_group['ltv_d14']).sum()
            roas_d14 = (paid_rev_d14 / paid_users) / paid_cpi if paid_cpi > 0 and paid_users > 0 else float('nan')
        else:
            roas_d14 = float('nan')
            
        return pd.Series({'Cost': paid_spend, 'ROAS_D0': roas_d0, 'ROAS_D7': roas_d7, 'ROAS_D14': roas_d14})
        
    combo_res = df_mature_d0.groupby('week').apply(agg_combo, include_groups=False).reset_index()
    combo_res = combo_res.sort_values('week')
    
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(
        go.Bar(x=combo_res['week'], y=combo_res['Cost'], name="Cost ($)", opacity=0.7, marker_color='#37536d'),
        secondary_y=False
    )
    fig_combo.add_trace(
        go.Scatter(x=combo_res['week'], y=combo_res['ROAS_D0'], name="ROAS D0", mode="lines+markers", line=dict(color='red', width=3)),
        secondary_y=True
    )
    fig_combo.add_trace(
        go.Scatter(x=combo_res['week'], y=combo_res['ROAS_D7'], name="ROAS D7", mode="lines+markers", line=dict(color='orange', width=2, dash='dot')),
        secondary_y=True
    )
    fig_combo.add_trace(
        go.Scatter(x=combo_res['week'], y=combo_res['ROAS_D14'], name="ROAS D14", mode="lines+markers", line=dict(color='green', width=2, dash='dash')),
        secondary_y=True
    )
    fig_combo.update_layout(title_text="Cost vs ROAS (D0, D7, D14)", hovermode="x unified")
    fig_combo.update_yaxes(title_text="Cost ($)", secondary_y=False)
    fig_combo.update_yaxes(title_text="ROAS", tickformat='.1%', secondary_y=True)
    st.plotly_chart(apply_drawing_layout(fig_combo), use_container_width=True, config=PLOTLY_CONFIG)
    
    # --- 2. Funnel Chart ---
    st.markdown("### 2. Funnel Chart: User Retention Journey")
    st.markdown("Mô phỏng phễu giữ chân người dùng (Thay cho phễu e-commerce vì dataset là app/game). Giúp tìm ra ngày nào người dùng rời bỏ nhiều nhất.")
    
    total_installs = df_roas['total_cohort_users'].sum()
    total_r1 = (df_roas['total_cohort_users'] * df_roas['retention_r1']).sum()
    total_r3 = (df_roas['total_cohort_users'] * df_roas['retention_r3']).sum()
    total_r7 = (df_roas['total_cohort_users'] * df_roas['retention_r7']).sum()
    
    funnel_data = dict(
        number=[total_installs, total_r1, total_r3, total_r7],
        stage=["1. Installs", "2. Day 1 Retained", "3. Day 3 Retained", "4. Day 7 Retained"]
    )
    fig_funnel = px.funnel(funnel_data, x='number', y='stage', title="User Retention Funnel")
    st.plotly_chart(apply_drawing_layout(fig_funnel), use_container_width=True, config=PLOTLY_CONFIG)
    
    # --- 3. Scatter Plot ---
    st.markdown("### 3. Scatter Plot: Cost vs ROAS D0 by Campaign")
    st.markdown("Trục X là Chi phí, trục Y là ROAS. Kích thước bong bóng là số lượng Installs. Giúp xác định chiến dịch nào đang đốt tiền (Góc dưới bên phải) và chiến dịch nào hiệu quả (Góc trên).")
    
    def agg_campaign(group):
        paid_group = group[group['is_paid']]
        paid_users = paid_group['total_cohort_users'].sum()
        paid_spend = paid_group['cohort_ad_spend'].sum()
        paid_rev = (paid_group['total_cohort_users'] * paid_group['ltv_d0']).sum()
        paid_ltv = paid_rev / paid_users if paid_users > 0 else 0
        paid_cpi = paid_spend / paid_users if paid_users > 0 else 0
        roas = paid_ltv / paid_cpi if paid_cpi > 0 else float('nan')
        return pd.Series({'Cost': paid_spend, 'ROAS': roas, 'Installs': paid_users})

    campaign_res = df_mature_d0.groupby('campaign_name').apply(agg_campaign, include_groups=False).reset_index()
    campaign_res = campaign_res[campaign_res['Cost'] > 0]
    
    fig_scatter = px.scatter(
        campaign_res, x='Cost', y='ROAS', hover_name='campaign_name', 
        size='Installs', color='ROAS',
        title="Campaign Performance (Cost vs ROAS D0)", 
        color_continuous_scale="RdYlGn", size_max=40
    )
    fig_scatter.update_yaxes(tickformat='.1%')
    
    median_roas = campaign_res['ROAS'].median()
    if pd.notnull(median_roas):
        fig_scatter.add_hline(y=median_roas, line_dash="dot", annotation_text="Median ROAS", annotation_position="bottom right")
        
    st.plotly_chart(apply_drawing_layout(fig_scatter), use_container_width=True, config=PLOTLY_CONFIG)


with tab_gameplay:
    st.header("🎮 Gameplay & Engagement Analytics")
    if gameplay_df.empty:
        st.warning("No Gameplay data available for the selected date range.")
    else:
        # High level KPIs
        st.subheader("Key Gameplay Metrics (Averages over period)")
        avg_playing_rate = gameplay_df['playing_rate'].mean()
        avg_win_rate = gameplay_df['overall_win_rate'].mean()
        avg_attempts_per_user = gameplay_df['avg_attempts'].mean()
        avg_median_playtime = gameplay_df['median_playtime_per_user'].mean()
        
        gk1, gk2, gk3, gk4 = st.columns(4)
        gk1.metric("Avg Playing Rate", f"{avg_playing_rate:.1%}")
        gk2.metric("Avg Win Rate", f"{avg_win_rate:.1%}")
        gk3.metric("Avg Attempts/User", f"{avg_attempts_per_user:.1f}")
        gk4.metric("Avg Median Playtime", f"{avg_median_playtime:.1f}s")
        
        st.divider()
        
        # Chart 1: DAU vs Playing Users
        st.subheader("1. Active Users vs Playing Users")
        fig_playing = px.area(gameplay_df, x='event_date', y=['dau', 'playing_users'], 
                              labels={'value': 'Users', 'event_date': 'Date', 'variable': 'Metric'},
                              title="DAU vs Playing Users Trend")
        fig_playing.update_layout(hovermode='x unified')
        add_changelog_vlines(fig_playing, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_playing), use_container_width=True, config=PLOTLY_CONFIG)
        
        st.divider()
        
        gc1, gc2 = st.columns(2)
        
        # Chart 2: Win Rate vs Fail Rate
        with gc1:
            st.subheader("2. Win Rate vs Fail Rate")
            fig_winfail = px.line(gameplay_df, x='event_date', y=['overall_win_rate', 'overall_fail_rate'],
                                  labels={'value': 'Rate', 'event_date': 'Date', 'variable': 'Metric'},
                                  title="Win Rate & Fail Rate Trend")
            fig_winfail.update_layout(hovermode='x unified', yaxis=dict(tickformat=".1%"))
            add_changelog_vlines(fig_winfail, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_winfail), use_container_width=True, config=PLOTLY_CONFIG)
            
        # Chart 3: Playtime Analysis
        with gc2:
            st.subheader("3. Playtime per User (Seconds)")
            fig_playtime = px.line(gameplay_df, x='event_date', y=['median_playtime_per_user', 'avg_playtime_per_user'],
                                   labels={'value': 'Seconds', 'event_date': 'Date', 'variable': 'Metric'},
                                   title="Median vs Average Playtime Trend")
            fig_playtime.update_layout(hovermode='x unified')
            add_changelog_vlines(fig_playtime, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_playtime), use_container_width=True, config=PLOTLY_CONFIG)
            
        st.divider()
        
        gc3, gc4 = st.columns(2)
        
        # Chart 4: Attempts & Booster Usage
        with gc3:
            st.subheader("4. Attempts vs Booster Usage")
            
            fig_attempts = make_subplots(specs=[[{"secondary_y": True}]])
            fig_attempts.add_trace(go.Bar(x=gameplay_df['event_date'], y=gameplay_df['avg_attempts'], name="Avg Attempts/User", opacity=0.7), secondary_y=False)
            fig_attempts.add_trace(go.Scatter(x=gameplay_df['event_date'], y=gameplay_df['avg_booster_usage'], name="Avg Booster Usage", mode='lines+markers', line=dict(color='red')), secondary_y=True)
            
            fig_attempts.update_layout(title_text="Attempts per User vs Booster Usage", hovermode="x unified")
            fig_attempts.update_yaxes(title_text="Attempts", secondary_y=False)
            fig_attempts.update_yaxes(title_text="Booster Usage", secondary_y=True)
            add_changelog_vlines(fig_attempts, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_attempts), use_container_width=True, config=PLOTLY_CONFIG)
            
        # Chart 5: Monetization vs Win Rate
        with gc4:
            st.subheader("5. ARPDAU & Ad ARPDAU vs Win Rate")
            fig_arpdau = make_subplots(specs=[[{"secondary_y": True}]])
            fig_arpdau.add_trace(go.Scatter(x=gameplay_df['event_date'], y=gameplay_df['arpdau'], name="ARPDAU", mode='lines', line=dict(color='green')), secondary_y=False)
            fig_arpdau.add_trace(go.Scatter(x=gameplay_df['event_date'], y=gameplay_df['ad_arpdau'], name="Ad ARPDAU", mode='lines', line=dict(color='blue', dash='dash')), secondary_y=False)
            fig_arpdau.add_trace(go.Scatter(x=gameplay_df['event_date'], y=gameplay_df['overall_win_rate'], name="Win Rate", mode='lines', line=dict(color='orange')), secondary_y=True)
            
            fig_arpdau.update_layout(title_text="Monetization vs Win Rate", hovermode="x unified")
            fig_arpdau.update_yaxes(title_text="ARPDAU ($)", secondary_y=False)
            fig_arpdau.update_yaxes(title_text="Win Rate", tickformat=".1%", secondary_y=True)
            add_changelog_vlines(fig_arpdau, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_arpdau), use_container_width=True, config=PLOTLY_CONFIG)

        st.divider()

        # Chart 6: Level Duration Analysis
        st.subheader("6. Duration Per Attempt Analysis")
        fig_duration = px.line(gameplay_df, x='event_date', 
                               y=['median_duration', 'median_win_duration', 'median_lose_duration'],
                               labels={'value': 'Duration (Seconds)', 'event_date': 'Date', 'variable': 'Duration Type'},
                               title="Win vs Lose vs Overall Duration")
        fig_duration.update_layout(hovermode='x unified')
        add_changelog_vlines(fig_duration, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_duration), use_container_width=True, config=PLOTLY_CONFIG)


with tab_technical:
    st.header("⚙️ Technical & Stability Analytics")
    if technical_df.empty:
        st.warning("No Technical data available for the selected date range.")
    else:
        st.subheader("Key Technical Metrics (Averages over period)")
        
        avg_general_errors = technical_df['total_general_errors'].mean() if 'total_general_errors' in technical_df.columns else 0
        avg_iap_errors = technical_df['total_iap_errors'].mean() if 'total_iap_errors' in technical_df.columns else 0
        avg_versions = technical_df['unique_app_versions_active'].mean() if 'unique_app_versions_active' in technical_df.columns else 0
        avg_devices = technical_df['unique_device_models_active'].mean() if 'unique_device_models_active' in technical_df.columns else 0
        
        tk1, tk2, tk3, tk4 = st.columns(4)
        tk1.metric("Avg General Errors/Day", f"{avg_general_errors:.1f}")
        tk2.metric("Avg IAP Errors/Day", f"{avg_iap_errors:.1f}")
        tk3.metric("Avg Active App Versions", f"{avg_versions:.1f}")
        tk4.metric("Avg Active Device Models", f"{avg_devices:.1f}")
        
        st.divider()
        
        tc1, tc2 = st.columns(2)
        
        with tc1:
            st.subheader("1. Errors Trend")
            cols_to_plot = []
            if 'total_general_errors' in technical_df.columns: cols_to_plot.append('total_general_errors')
            if 'total_iap_errors' in technical_df.columns: cols_to_plot.append('total_iap_errors')
            
            if cols_to_plot:
                fig_errors = px.line(technical_df, x='event_date', y=cols_to_plot,
                                      labels={'value': 'Error Count', 'event_date': 'Date', 'variable': 'Error Type'},
                                      title="Daily Errors (General vs IAP)")
                fig_errors.update_layout(hovermode='x unified')
                add_changelog_vlines(fig_errors, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
                st.plotly_chart(apply_drawing_layout(fig_errors), use_container_width=True, config=PLOTLY_CONFIG)
                
        with tc2:
            st.subheader("2. Fragmentation Trend")
            cols_to_plot = []
            if 'unique_app_versions_active' in technical_df.columns: cols_to_plot.append('unique_app_versions_active')
            if 'unique_device_models_active' in technical_df.columns: cols_to_plot.append('unique_device_models_active')
            
            if cols_to_plot:
                fig_frag = px.line(technical_df, x='event_date', y=cols_to_plot,
                                   labels={'value': 'Count', 'event_date': 'Date', 'variable': 'Metric'},
                                   title="Active App Versions & Device Models")
                fig_frag.update_layout(hovermode='x unified')
                add_changelog_vlines(fig_frag, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
                st.plotly_chart(apply_drawing_layout(fig_frag), use_container_width=True, config=PLOTLY_CONFIG)
                
        st.divider()
        
        st.subheader("3. App Launch Duration")
        launch_cols = []
        if 'avg_app_launch_duration' in technical_df.columns and not technical_df['avg_app_launch_duration'].isna().all():
            launch_cols.append('avg_app_launch_duration')
        if 'median_app_launch_duration' in technical_df.columns and not technical_df['median_app_launch_duration'].isna().all():
            launch_cols.append('median_app_launch_duration')
            
        if launch_cols:
            fig_launch = px.line(technical_df, x='event_date', y=launch_cols,
                                 labels={'value': 'Duration (ms/sec)', 'event_date': 'Date', 'variable': 'Metric'},
                                 title="App Launch Duration Trend")
            fig_launch.update_layout(hovermode='x unified')
            add_changelog_vlines(fig_launch, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
            st.plotly_chart(apply_drawing_layout(fig_launch), use_container_width=True, config=PLOTLY_CONFIG)
        else:
            st.info("App Launch Duration data is empty or not available.")

with tab_level:
    st.header("📊 Level Funnel Comparison: Build 1.0.11 vs 1.1.0")
    st.markdown(
        "So sánh hành vi người chơi, độ khó, và hiệu quả kiếm tiền giữa 2 build **1.0.11** vs **1.1.0** "
        "dọc theo chiều dài các level. Dữ liệu lấy từ `level_1_0_11.csv` và `level_1_1_0.csv`."
    )

    if level_a_df.empty or level_b_df.empty:
        st.warning("Level data not found. Please ensure level_1_0_11.csv and level_1_1_0.csv exist.")
    else:
        LABEL_A = "1.0.11"
        LABEL_B = "1.1.0"

        # Level range slider
        max_possible_level = max(level_a_df['level'].max(), level_b_df['level'].max())
        level_range = st.slider(
            "Level Range", min_value=1, max_value=int(max_possible_level),
            value=(1, min(200, int(max_possible_level))),
            help="Các level cao (>100) có rất ít user nên tỷ lệ % dao động nhiều. Khuyến nghị xem đến level 150–200."
        )
        max_lv = level_range[1]
        # Filter by min level too
        lv_a = level_a_df[level_a_df['level'] >= level_range[0]].copy()
        lv_b = level_b_df[level_b_df['level'] >= level_range[0]].copy()

        # KPI summary
        st.subheader("High-Level Comparison")
        common_max = min(level_a_df['level'].max(), level_b_df['level'].max())
        a50 = level_a_df[level_a_df['level'] == 50]
        b50 = level_b_df[level_b_df['level'] == 50]
        a100 = level_a_df[level_a_df['level'] == 100]
        b100 = level_b_df[level_b_df['level'] == 100]

        kc1, kc2, kc3, kc4, kc5, kc6 = st.columns(6)
        kc1.metric(f"Users L1 ({LABEL_A})", f"{int(level_a_df[level_a_df['level']==1]['playing_user'].values[0]):,}")
        kc2.metric(f"Users L1 ({LABEL_B})", f"{int(level_b_df[level_b_df['level']==1]['playing_user'].values[0]):,}")
        if not a50.empty and not b50.empty:
            kc3.metric(f"Funnel L50 ({LABEL_A})", f"{a50['funnel_rate'].values[0]:.1%}")
            kc4.metric(f"Funnel L50 ({LABEL_B})", f"{b50['funnel_rate'].values[0]:.1%}")
        if not a100.empty and not b100.empty:
            kc5.metric(f"Funnel L100 ({LABEL_A})", f"{a100['funnel_rate'].values[0]:.1%}")
            kc6.metric(f"Funnel L100 ({LABEL_B})", f"{b100['funnel_rate'].values[0]:.1%}")

        st.divider()

        # ─── SECTION 1: Funnel & Churn ───
        st.subheader("📉 Phần 1: Funnel & Churn (Sức khỏe người chơi)")

        fig_funnel = chart_cumulative_funnel_rate(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
        st.plotly_chart(apply_drawing_layout(fig_funnel), use_container_width=True, config=PLOTLY_CONFIG)

        lv_col1, lv_col2 = st.columns(2)
        with lv_col1:
            fig_drop = chart_dropoff_delta(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_drop), use_container_width=True, config=PLOTLY_CONFIG)
        with lv_col2:
            fig_cont = chart_continue_rate(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_cont), use_container_width=True, config=PLOTLY_CONFIG)

        st.divider()

        # ─── SECTION 2: Difficulty & Engagement ───
        st.subheader("⚔️ Phần 2: Difficulty & Engagement (Độ khó & Trải nghiệm)")

        fig_1st = chart_first_attempt_win_rate_delta(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
        st.plotly_chart(apply_drawing_layout(fig_1st), use_container_width=True, config=PLOTLY_CONFIG)

        lv_col3, lv_col4 = st.columns(2)
        with lv_col3:
            fig_fail = chart_fail_rate_and_attempts(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_fail), use_container_width=True, config=PLOTLY_CONFIG)
        with lv_col4:
            fig_prog = chart_avg_progress(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_prog), use_container_width=True, config=PLOTLY_CONFIG)

        fig_ribbon = chart_win_duration_ribbon(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
        st.plotly_chart(apply_drawing_layout(fig_ribbon), use_container_width=True, config=PLOTLY_CONFIG)

        st.divider()

        # ─── SECTION 3: Monetization & Resource Economy ───
        st.subheader("💰 Phần 3: Monetization & Resource Economy (Dòng tiền & Tài nguyên)")

        # Basic Monetization
        lv_col_m1, lv_col_m2 = st.columns(2)
        with lv_col_m1:
            fig_avg_imp = chart_avg_imp_per_user(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_avg_imp), use_container_width=True, config=PLOTLY_CONFIG)
        with lv_col_m2:
            fig_avg_rev = chart_ad_revenue_per_user(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_avg_rev), use_container_width=True, config=PLOTLY_CONFIG)

        lv_col5, lv_col6 = st.columns(2)
        with lv_col5:
            fig_arpu = chart_arpu_curve(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_arpu), use_container_width=True, config=PLOTLY_CONFIG)
        with lv_col6:
            fig_imp = chart_cumulative_impressions(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
            st.plotly_chart(apply_drawing_layout(fig_imp), use_container_width=True, config=PLOTLY_CONFIG)

        # Resource Source vs Sink for each resource
        st.markdown("#### Resource Source vs Sink Balance")
        resource_tab_hint, resource_tab_wand, resource_tab_eraser, resource_tab_grid = st.tabs(
            ["🔍 Hint", "🪄 Wand", "🧹 Eraser", "🔲 Grid"]
        )
        with resource_tab_hint:
            fig_hint = chart_resource_source_sink(lv_a, lv_b, LABEL_A, LABEL_B, "hint", max_lv)
            st.plotly_chart(apply_drawing_layout(fig_hint), use_container_width=True, config=PLOTLY_CONFIG)
        with resource_tab_wand:
            fig_wand = chart_resource_source_sink(lv_a, lv_b, LABEL_A, LABEL_B, "wand", max_lv)
            st.plotly_chart(apply_drawing_layout(fig_wand), use_container_width=True, config=PLOTLY_CONFIG)
        with resource_tab_eraser:
            fig_eraser = chart_resource_source_sink(lv_a, lv_b, LABEL_A, LABEL_B, "eraser", max_lv)
            st.plotly_chart(apply_drawing_layout(fig_eraser), use_container_width=True, config=PLOTLY_CONFIG)
        with resource_tab_grid:
            fig_grid = chart_resource_source_sink(lv_a, lv_b, LABEL_A, LABEL_B, "grid", max_lv)
            st.plotly_chart(apply_drawing_layout(fig_grid), use_container_width=True, config=PLOTLY_CONFIG)

        # T1 vs T2 Ad Quality
        fig_t1t2 = chart_t1_t2_ad_mix(lv_a, lv_b, LABEL_A, LABEL_B, max_lv)
        st.plotly_chart(apply_drawing_layout(fig_t1t2), use_container_width=True, config=PLOTLY_CONFIG)

with tab_combined:
    st.header("📋 Combined Charts")

    # ── 1. Weekly Installs vs Ad Spend ──
    st.subheader("1. Weekly Installs vs Ad Spend")
    st.markdown(
        "Bar chart thể hiện tổng **Installs** mỗi tuần, "
        "line thể hiện tổng **Ad Spend ($)** tương ứng. "
        "Dữ liệu từ `ad_spend.csv` và `DAU.csv`."
    )

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # --- Prepare ad_spend weekly ---
    ad_combined = ad_spend_raw_df.copy()
    if not ad_combined.empty:
        ad_combined['day'] = pd.to_datetime(ad_combined['day'])
        ad_combined['week'] = ad_combined['day'].dt.to_period('W').apply(lambda r: r.start_time)
        ad_weekly = ad_combined.groupby('week').agg(
            installs=('installs', 'sum'),
            cost=('cost', 'sum'),
        ).reset_index()
        ad_weekly = ad_weekly.sort_values('week')

        # --- Prepare DAU weekly from DAU.csv ---
        dau_combined = dau_raw_df.copy()
        dau_weekly = pd.DataFrame()
        if not dau_combined.empty:
            dau_combined['event_date'] = pd.to_datetime(dau_combined['event_date'])
            # DAU per day = sum of total_dau grouped by event_date
            dau_daily = dau_combined.groupby('event_date')['total_dau'].sum().reset_index()
            dau_daily['week'] = dau_daily['event_date'].dt.to_period('W').apply(lambda r: r.start_time)
            dau_weekly = dau_daily.groupby('week').agg(
                avg_dau=('total_dau', 'mean'),
            ).reset_index()

        # --- Build chart ---
        fig_combined = make_subplots(specs=[[{"secondary_y": True}]])

        # Bars: Installs
        fig_combined.add_trace(
            go.Bar(
                x=ad_weekly['week'], y=ad_weekly['installs'],
                name="Installs", opacity=0.75,
                marker_color='#636EFA',
                text=ad_weekly['installs'].apply(lambda x: f"{x:,.0f}"),
                textposition='outside',
                hovertemplate="Week %{x}<br>Installs: %{y:,.0f}<extra></extra>",
            ),
            secondary_y=False,
        )

        # Line: Ad Spend
        fig_combined.add_trace(
            go.Scatter(
                x=ad_weekly['week'], y=ad_weekly['cost'],
                name="Ad Spend ($)", mode='lines+markers',
                line=dict(color='#EF553B', width=3),
                hovertemplate="Week %{x}<br>Cost: $%{y:,.2f}<extra></extra>",
            ),
            secondary_y=True,
        )

        # Line: Avg DAU (if available)
        if not dau_weekly.empty:
            # Merge on week to align
            merged_weeks = pd.merge(ad_weekly[['week']], dau_weekly, on='week', how='left')
            fig_combined.add_trace(
                go.Scatter(
                    x=merged_weeks['week'], y=merged_weeks['avg_dau'],
                    name="Avg DAU", mode='lines+markers',
                    line=dict(color='#00CC96', width=2, dash='dash'),
                    hovertemplate="Week %{x}<br>Avg DAU: %{y:,.0f}<extra></extra>",
                ),
                secondary_y=False,
            )

        fig_combined.update_layout(
            title_text="Weekly Installs vs Ad Spend (with Avg DAU)",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            bargap=0.2,
        )
        fig_combined.update_yaxes(title_text="Installs / DAU", secondary_y=False)
        fig_combined.update_yaxes(title_text="Ad Spend ($)", secondary_y=True)
        add_changelog_vlines(fig_combined, changelog_df, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(apply_drawing_layout(fig_combined), use_container_width=True, config=PLOTLY_CONFIG)

        # --- KPI Summary ---
        st.markdown("#### Weekly Summary Table")
        display_df = ad_weekly.copy()
        display_df['week_label'] = display_df['week'].dt.strftime('%Y-%m-%d')
        display_df['CPI'] = display_df['cost'] / display_df['installs'].replace(0, float('nan'))
        if not dau_weekly.empty:
            display_df = pd.merge(display_df, dau_weekly, on='week', how='left')
        cols_show = ['week_label', 'installs', 'cost']
        col_config = {
            'week_label': st.column_config.TextColumn('Week'),
            'installs': st.column_config.NumberColumn('Installs', format='%d'),
            'cost': st.column_config.NumberColumn('Ad Spend ($)', format='$%.2f'),
            'CPI': st.column_config.NumberColumn('CPI ($)', format='$%.4f'),
        }
        if 'avg_dau' in display_df.columns:
            cols_show.append('avg_dau')
            col_config['avg_dau'] = st.column_config.NumberColumn('Avg DAU', format='%.0f')
        cols_show.append('CPI')
        st.dataframe(display_df[cols_show], column_config=col_config, use_container_width=True, hide_index=True)
    else:
        st.warning("Ad Spend data not available.")

    st.divider()
    # ── 2. IS Impression vs Level Difficulty ──
    st.subheader("2. Avg IS Impression & Avg Attempts by Level (1.1.0 vs 1.0.11)")
    if not level_a_df.empty and not level_b_df.empty:
        # Prepare data
        df_a = level_a_df[['level', 'is_imp', 'playing_user', 'avg_attempts']].copy()
        df_a['avg_is_imp'] = df_a['is_imp'] / df_a['playing_user'].replace(0, float('nan'))
        
        df_b = level_b_df[['level', 'is_imp', 'playing_user', 'avg_attempts']].copy()
        df_b['avg_is_imp'] = df_b['is_imp'] / df_b['playing_user'].replace(0, float('nan'))
        
        # Filter for first 100 levels to keep it readable, as higher levels can be noisy
        df_a = df_a[df_a['level'] <= 100]
        df_b = df_b[df_b['level'] <= 100]
        
        fig_is_diff = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Build 1.0.11
        fig_is_diff.add_trace(
            go.Bar(x=df_a['level'], y=df_a['avg_is_imp'], name='Avg IS/User (1.0.11)', marker_color='lightgray', opacity=0.7),
            secondary_y=False
        )
        fig_is_diff.add_trace(
            go.Scatter(x=df_a['level'], y=df_a['avg_attempts'], name='Avg Attempts (1.0.11)', mode='lines', line=dict(color='gray', width=1, dash='dot')),
            secondary_y=True
        )
        
        # Build 1.1.0
        fig_is_diff.add_trace(
            go.Bar(x=df_b['level'], y=df_b['avg_is_imp'], name='Avg IS/User (1.1.0)', marker_color='#636EFA'),
            secondary_y=False
        )
        fig_is_diff.add_trace(
            go.Scatter(x=df_b['level'], y=df_b['avg_attempts'], name='Avg Attempts (1.1.0)', mode='lines', line=dict(color='#EF553B', width=2)),
            secondary_y=True
        )
        
        fig_is_diff.update_layout(
            title="Avg IS Impression per User vs Avg Attempts (Difficulty)",
            barmode='group',
            hovermode="x unified",
            xaxis_title="Level",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        fig_is_diff.update_yaxes(title_text="Avg IS Imp per User", secondary_y=False)
        fig_is_diff.update_yaxes(title_text="Avg Attempts (Difficulty)", secondary_y=True, showgrid=False)
        
        st.plotly_chart(apply_drawing_layout(fig_is_diff), use_container_width=True, config=PLOTLY_CONFIG)

with tab_heart:
    st.header("🫀 Heart Mechanism Diagnostic (1.0.11 vs 1.1.0)")
    st.markdown("> Cơ chế Heart (Lives) ở Build 1.1.0 làm nghẽn luồng chơi → giảm session/retries → giảm IS Impression → giảm Ad Revenue & LTV7. RW Impression tăng (do user xem ads hồi tim) nhưng không đủ bù đắp IS bị mất.")
    
    if level_a_df.empty or level_b_df.empty or heart_df.empty:
        st.warning("Missing data for Heart Diagnostic. Need level_1_0_11.csv, level_1_1_0.csv and heart.csv.")
    else:
        from heart_charts import (
            chart_a1_funnel, chart_a2_is_gap, chart_a3_rw_breakdown,
            chart_a4_heart_waterfall, chart_a5_revenue_delta, chart_a6_net_revenue
        )
        max_lv = 80 # default max level for this diagnostic
        
        st.subheader("Phần A & B: Narrative Story Charts & Dashboard Grid")
        
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            st.plotly_chart(chart_a1_funnel(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)
        with h_col2:
            st.plotly_chart(chart_a2_is_gap(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)
            
        h_col3, h_col4 = st.columns(2)
        with h_col3:
            st.plotly_chart(chart_a3_rw_breakdown(level_b_df, max_lvl=max_lv), use_container_width=True)
        with h_col4:
            st.plotly_chart(chart_a4_heart_waterfall(heart_df, max_lvl=max_lv), use_container_width=True)
            
        h_col5, h_col6 = st.columns(2)
        with h_col5:
            st.plotly_chart(chart_a5_revenue_delta(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)
        with h_col6:
            st.plotly_chart(chart_a6_net_revenue(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)

        st.markdown("---")
        st.subheader("Phần C: Bonus Charts (Deep-dive)")
        
        from heart_charts import (
            chart_c1_rw_heart_funnel, chart_c2_fail_rate_spike, chart_c3_session_killer,
            chart_c4_is_imp_delta, chart_c5_avg_is_normalized, chart_c6_rw_is_tradeoff
        )
        
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.plotly_chart(chart_c1_rw_heart_funnel(heart_df, max_lvl=max_lv), use_container_width=True)
        with b_col2:
            st.plotly_chart(chart_c2_fail_rate_spike(level_b_df, heart_df, max_lvl=max_lv), use_container_width=True)
            
        b_col3, b_col4 = st.columns(2)
        with b_col3:
            st.plotly_chart(chart_c3_session_killer(heart_df), use_container_width=True)
        with b_col4:
            st.plotly_chart(chart_c4_is_imp_delta(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)
            
        b_col5, b_col6 = st.columns(2)
        with b_col5:
            st.plotly_chart(chart_c5_avg_is_normalized(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)
        with b_col6:
            st.plotly_chart(chart_c6_rw_is_tradeoff(level_a_df, level_b_df, max_lvl=max_lv), use_container_width=True)

        # --- PHẦN D ---
        if not heart_metrics_drop_df.empty:
            st.markdown("---")
            st.subheader("Phần D: Drop Behavior Analysis")
            from heart_charts import (
                chart_d1_stage_drop, chart_d2_hard_frustration,
                chart_d3_cum_drop, chart_d4_drop_delta, chart_d5_causality
            )
            
            st.markdown("**Chart D1: Stage-by-Stage Drop Rate Comparison**")
            st.plotly_chart(chart_d1_stage_drop(level_a_df, heart_metrics_drop_df, level_b_df, max_lvl=max_lv), use_container_width=True)
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown("**Chart D2: Hard Level Frustration (Build 1.1.0)**")
                st.plotly_chart(chart_d2_hard_frustration(heart_metrics_drop_df, level_b_df, max_lvl=max_lv), use_container_width=True)
            with d_col2:
                st.markdown("**Chart D3: Cumulative Drop Funnel**")
                st.plotly_chart(chart_d3_cum_drop(level_a_df, heart_metrics_drop_df, max_lvl=max_lv), use_container_width=True)
                
            d_col3, d_col4 = st.columns(2)
            with d_col3:
                st.markdown("**Chart D4: Per-Level Drop Rate Delta Overlay**")
                st.plotly_chart(chart_d4_drop_delta(level_a_df, heart_metrics_drop_df, level_b_df, max_lvl=max_lv), use_container_width=True)
            with d_col4:
                st.markdown("**Chart D5: Drop Causality Decomposition (Bằng Chứng Nhân Quả)**")
                st.plotly_chart(chart_d5_causality(level_a_df, heart_metrics_drop_df, level_b_df, max_lvl=max_lv), use_container_width=True)

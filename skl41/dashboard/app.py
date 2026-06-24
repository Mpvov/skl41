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

CSV_PATH = "../dau_ad_imp_ad_rev_geo_channel.csv"
RETENTION_CSV_PATH = "../retention&ltv.csv"
ROAS_CSV_PATH = "../roas.csv"
DAU_CSV_PATH = "../DAU.csv"
CHANGELOG_CSV_PATH = "../changelog.csv"

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

st.title("📊 Game Analytics Dashboard")

# --- TABS ---
tab_combined, tab_installs, tab_monetization, tab_retention, tab_business, tab_spend, tab_roas_eroas = st.tabs(["🔥 Combined Insight", "🚀 Installs", "💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend", "⚖️ ROAS vs eROAS"])

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
        if not roas_df.empty and 'cohort_ad_spend' in roas_df.columns:
            spend_trend = roas_df.groupby('install_date')['cohort_ad_spend'].sum().reset_index()
            if not spend_trend.empty:
                fig_spend = px.line(spend_trend, x='install_date', y='cohort_ad_spend', title="Ad Spend Trend")
                add_changelog_vlines(fig_spend, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
                st.plotly_chart(apply_drawing_layout(fig_spend), use_container_width=True, config=PLOTLY_CONFIG)
            
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
                    # Drop None values to avoid plotting lines to 0
                    dow_melted = dow_melted.dropna(subset=['Retention Rate'])
                    fig_dow = px.line(dow_melted, x='Day of Week', y='Retention Rate', color='Metric', title="Retention by Day of Week", markers=True)
                    fig_dow.update_layout(yaxis_tickformat='.1%')
                    st.plotly_chart(apply_drawing_layout(fig_dow), use_container_width=True, config=PLOTLY_CONFIG)

with tab_business:
    st.header("Business & Scale Overview")
    
    total_dau = calculate_dau(dau_df)
    total_installs = int(dau_df['new_users'].sum()) if not dau_df.empty and 'new_users' in dau_df.columns else 0
    total_ad_spend = calculate_total_ad_spend(retention_df)
    
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

    retention_df_d0 = filter_retention_csv(retention_raw_df, d0_picker_start, d0_picker_end, countries, media_sources, campaigns)
    roas_df_d7 = filter_roas_csv(roas_raw_df, d7_picker_start, d7_picker_end, countries, media_sources, campaigns)
    roas_df_d30 = filter_roas_csv(roas_raw_df, d30_picker_start, d30_picker_end, countries, media_sources, campaigns)

    campaign_roas_d0, blended_roas_d0, d0_start, d0_end = calculate_roas_d0_kpis_v2(
        retention_df_d0, days=7, start_date=d0_picker_start, end_date=d0_picker_end
    )

    campaign_roas_d7, blended_roas_d7, d7_start, d7_end = calculate_roas_d7_kpis_v2(
        roas_df_d7, days=7, start_date=d7_picker_start, end_date=d7_picker_end
    )

    solid_roas_d30, blended_roas_d30, d30_start, d30_end = calculate_roas_d30_kpis_v2(
        roas_df_d30, days=14, start_date=d30_picker_start, end_date=d30_picker_end
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
        
    roas_trend_df = calculate_roas_by_date_from_csv(retention_df)
    
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


with tab_combined:
    st.header("Executive Summary: CPI & DAU Paradox")
    
    # Calculate L30 vs P30 for narrative
    max_date = pd.to_datetime(dau_raw_df['event_date'].max())
    l30_start = max_date - pd.Timedelta(days=29)
    p30_start = l30_start - pd.Timedelta(days=30)
    p30_end = l30_start - pd.Timedelta(days=1)
    
    dau_l30 = dau_raw_df[(pd.to_datetime(dau_raw_df['event_date']) >= l30_start)]
    dau_p30 = dau_raw_df[(pd.to_datetime(dau_raw_df['event_date']) >= p30_start) & (pd.to_datetime(dau_raw_df['event_date']) <= p30_end)]
    
    roas_l30 = roas_raw_df[(pd.to_datetime(roas_raw_df['install_date']) >= l30_start)]
    roas_p30 = roas_raw_df[(pd.to_datetime(roas_raw_df['install_date']) >= p30_start) & (pd.to_datetime(roas_raw_df['install_date']) <= p30_end)]
    
    avg_dau_l30 = dau_l30['total_dau'].sum() / dau_l30['event_date'].nunique() if dau_l30['event_date'].nunique() > 0 else 0
    avg_dau_p30 = dau_p30['total_dau'].sum() / dau_p30['event_date'].nunique() if dau_p30['event_date'].nunique() > 0 else 0
    dau_diff_pct = (avg_dau_l30 - avg_dau_p30) / avg_dau_p30 * 100 if avg_dau_p30 > 0 else 0
    
    t1_l30 = roas_l30[roas_l30['country_code'].isin(T1_COUNTRIES)]
    t1_users_l30 = t1_l30['total_cohort_users'].sum()
    t1_cpi_l30 = t1_l30['cohort_ad_spend'].sum() / t1_users_l30 if t1_users_l30 > 0 else 0
    
    t1_p30 = roas_p30[roas_p30['country_code'].isin(T1_COUNTRIES)]
    t1_users_p30 = t1_p30['total_cohort_users'].sum()
    t1_cpi_p30 = t1_p30['cohort_ad_spend'].sum() / t1_users_p30 if t1_users_p30 > 0 else 0
    
    cpi_growth = t1_cpi_l30 / t1_cpi_p30 if t1_cpi_p30 > 0 else 1
    
    t3_l30 = roas_l30[~roas_l30['country_code'].isin(T1_COUNTRIES) & ~roas_l30['country_code'].isin(T2_COUNTRIES)]
    t3_users_l30 = t3_l30['total_cohort_users'].sum()
    t3_cpi_l30 = t3_l30['cohort_ad_spend'].sum() / t3_users_l30 if t3_users_l30 > 0 else 0
    
    cpi_ratio = t1_cpi_l30 / t3_cpi_l30 if t3_cpi_l30 > 0 else 0
    
    # Render Narrative
    dau_direction = "giảm" if dau_diff_pct < 0 else "tăng"
    st.markdown(f"### DAU {dau_direction} {abs(dau_diff_pct):.1f}% dù tăng ngân sách: Chi phí bị hút vào tệp Tier 1 giá cao (CPI tăng {(cpi_growth):.1f} lần) khiến tổng lượng user mới thu về thấp hơn tháng trước.")
    st.markdown(f"**Chi tiết:** CPI trung bình của Tier 1 tháng này là **${t1_cpi_l30:.2f}**, tăng **{(cpi_growth-1)*100:.1f}%** so với tháng trước (**${t1_cpi_p30:.2f}**). Hơn nữa, mức CPI này đắt gấp **{cpi_ratio:.1f} lần** so với tệp Tier 3 (**${t3_cpi_l30:.2f}**). Tiền bị 'bốc hơi' vào giá thầu nhưng lượng user mới thu về ít đi, không đủ bù đắp lượng user đang rời bỏ (churn) tự nhiên, dẫn đến tổng DAU sụt giảm.")
    
    # Weekly Combo Chart
    combo_roas = roas_df.copy()
    if not combo_roas.empty:
        combo_roas['week'] = pd.to_datetime(combo_roas['install_date']).dt.to_period('W').apply(lambda r: r.start_time)
        weekly_spend = combo_roas.groupby('week')['cohort_ad_spend'].sum().reset_index()
        
        combo_dau = dau_df.copy()
        combo_dau['week'] = pd.to_datetime(combo_dau['event_date']).dt.to_period('W').apply(lambda r: r.start_time)
        weekly_installs = combo_dau.groupby('week')['new_users'].sum().reset_index()
        
        weekly_combo = pd.merge(weekly_spend, weekly_installs, on='week', how='outer').fillna(0).sort_values('week')
        
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
        fig_combo.add_trace(
            go.Bar(x=weekly_combo['week'], y=weekly_combo['cohort_ad_spend'], name="Tổng Ad Spend", opacity=0.7, marker_color='rgb(55, 83, 109)'),
            secondary_y=False
        )
        fig_combo.add_trace(
            go.Scatter(x=weekly_combo['week'], y=weekly_combo['new_users'], name="New Installs", mode="lines+markers", line=dict(color='red', width=3)),
            secondary_y=True
        )
        
        fig_combo.update_layout(
            title_text="Ad Spend vs New Installs (Weekly)",
            xaxis_title="Tuần",
            hovermode="x unified"
        )
        fig_combo.update_yaxes(title_text="Ad Spend ($)", secondary_y=False)
        fig_combo.update_yaxes(title_text="New Installs", secondary_y=True)
        
        st.plotly_chart(apply_drawing_layout(fig_combo), use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.warning("No data available for Combo Chart.")


with tab_roas_eroas:
    st.header("ROAS vs eROAS (D0, D7, D30)")
    st.markdown("Quy tắc tính: **ROAS** = LTV(Paid) / CPI(Paid) | **eROAS** = LTV(All) / CPI(Paid). Nếu CPI = 0 thì không vẽ (tránh lỗi chia 0). Chỉ tính dữ liệu đã đủ độ chín (Maturity).")
    
    df_roas = pd.read_csv("../retention&ltv.csv")
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

import re

with open('app.py', 'r', encoding='utf8') as f:
    content = f.read()

# 1. Add "Combined Insight" to the tabs definition
tabs_old = 'tab_installs, tab_monetization, tab_retention, tab_business, tab_spend = st.tabs(["🚀 Installs", "💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend"])'
tabs_new = 'tab_combined, tab_installs, tab_monetization, tab_retention, tab_business, tab_spend = st.tabs(["🔥 Combined Insight", "🚀 Installs", "💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend"])'

if tabs_old in content:
    content = content.replace(tabs_old, tabs_new)
else:
    print("Could not find tabs definition.")

# 2. Add the Combined tab logic at the end of the file
combined_logic = """
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
        
        st.plotly_chart(fig_combo, use_container_width=True)
    else:
        st.warning("No data available for Combo Chart.")
"""

if "with tab_combined:" not in content:
    content += "\n" + combined_logic

with open('app.py', 'w', encoding='utf8') as f:
    f.write(content)

print("Updated app.py with Combined tab.")

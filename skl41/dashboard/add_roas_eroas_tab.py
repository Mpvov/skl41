import pandas as pd
import re

with open('app.py', 'r', encoding='utf8') as f:
    content = f.read()

# 1. Update Tabs Definition
tabs_old = 'tab_combined, tab_installs, tab_monetization, tab_retention, tab_business, tab_spend = st.tabs(["🔥 Combined Insight", "🚀 Installs", "💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend"])'
tabs_new = 'tab_combined, tab_installs, tab_monetization, tab_retention, tab_business, tab_spend, tab_roas_eroas = st.tabs(["🔥 Combined Insight", "🚀 Installs", "💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend", "⚖️ ROAS vs eROAS"])'

if tabs_old in content:
    content = content.replace(tabs_old, tabs_new)

# 2. Add the tab_roas_eroas logic at the end
roas_eroas_logic = """
with tab_roas_eroas:
    st.header("ROAS vs eROAS (D0, D7, D30)")
    st.markdown("Quy tắc tính: **ROAS** = LTV(Paid) / CPI(Paid) | **eROAS** = LTV(All) / CPI(Paid). Nếu CPI = 0 thì không vẽ (tránh lỗi chia 0). Chỉ tính dữ liệu đã đủ độ chín (Maturity).")
    
    df_roas = roas_raw_df.copy()
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
"""

if "with tab_roas_eroas:" not in content:
    content += "\n" + roas_eroas_logic

with open('app.py', 'w', encoding='utf8') as f:
    f.write(content)

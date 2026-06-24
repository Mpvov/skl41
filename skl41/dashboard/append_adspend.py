# append_adspend.py
import re

with open('app.py', 'r', encoding='utf8') as f:
    content = f.read()

# Replace tabs definition
old_tabs = 'tab_monetization, tab_retention, tab_business = st.tabs(["💰 Monetization", "🔄 Retention", "📈 Business"])'
new_tabs = 'tab_monetization, tab_retention, tab_business, tab_spend = st.tabs(["💰 Monetization", "🔄 Retention", "📈 Business", "💸 Ad Spend"])'

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
else:
    print("WARNING: Could not find old tabs definition!")

ad_spend_code = """

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
        st.plotly_chart(fig_channel, use_container_width=True)

        # 2. Top 5 Countries Stacked Bar
        st.subheader("2. Ad Spend by Top 5 Countries")
        top_5_countries = roas_df.groupby('country_code')['cohort_ad_spend'].sum().nlargest(5).index.tolist()
        roas_df_mapped = roas_df.copy()
        roas_df_mapped['mapped_country'] = roas_df_mapped['country_code'].apply(lambda c: c if c in top_5_countries else 'Others')
        spend_by_country = roas_df_mapped.groupby(['install_date', 'mapped_country'], as_index=False)['cohort_ad_spend'].sum()
        
        fig_country = px.bar(spend_by_country, x='install_date', y='cohort_ad_spend', color='mapped_country', title="Ad Spend by Top 5 Countries")
        fig_country.update_layout(yaxis_title="Ad Spend ($)", xaxis_title="Date", barmode='stack', hovermode='x unified')
        add_changelog_vlines(fig_country, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)
        st.plotly_chart(fig_country, use_container_width=True)

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
        st.plotly_chart(fig_combo, use_container_width=True)

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
        st.plotly_chart(fig_bubble, use_container_width=True)
"""

if 'with tab_spend:' not in content:
    content += ad_spend_code
    print("Added Ad Spend code.")
else:
    print("Ad Spend code already exists.")

with open('app.py', 'w', encoding='utf8') as f:
    f.write(content)

print("Done.")

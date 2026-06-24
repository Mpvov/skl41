import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

with open('app.py', 'r', encoding='utf8') as f:
    content = f.read()

append_logic = """
    st.markdown("---")
    st.header("🔍 Phân tích chuyên sâu (Insights)")
    
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    df_mature_d0 = df_roas[df_roas['date'] <= max_date]
    
    # --- 1. Combo Chart ---
    st.markdown("### 1. Combo Chart: Cost vs ROAS D0 (Weekly)")
    st.markdown("Hiển thị tương quan trực quan giữa Chi phí (Cột) và ROAS (Đường) qua từng tuần.")
    
    def agg_combo(group):
        paid_group = group[group['is_paid']]
        paid_users = paid_group['total_cohort_users'].sum()
        paid_spend = paid_group['cohort_ad_spend'].sum()
        paid_rev = (paid_group['total_cohort_users'] * paid_group['ltv_d0']).sum()
        paid_ltv = paid_rev / paid_users if paid_users > 0 else 0
        paid_cpi = paid_spend / paid_users if paid_users > 0 else 0
        roas = paid_ltv / paid_cpi if paid_cpi > 0 else float('nan')
        return pd.Series({'Cost': paid_spend, 'ROAS': roas})
        
    combo_res = df_mature_d0.groupby('week').apply(agg_combo, include_groups=False).reset_index()
    combo_res = combo_res.sort_values('week')
    
    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(
        go.Bar(x=combo_res['week'], y=combo_res['Cost'], name="Cost ($)", opacity=0.7, marker_color='#37536d'),
        secondary_y=False
    )
    fig_combo.add_trace(
        go.Scatter(x=combo_res['week'], y=combo_res['ROAS'], name="ROAS D0", mode="lines+markers", line=dict(color='red', width=3)),
        secondary_y=True
    )
    fig_combo.update_layout(title_text="Cost vs ROAS D0", hovermode="x unified")
    fig_combo.update_yaxes(title_text="Cost ($)", secondary_y=False)
    fig_combo.update_yaxes(title_text="ROAS D0", tickformat='.1%', secondary_y=True)
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
"""

if "3. Scatter Plot: Cost vs ROAS" not in content:
    content += append_logic

with open('app.py', 'w', encoding='utf8') as f:
    f.write(content)

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

BUILD_OLD_COLOR = "#1f77b4" # Blue
BUILD_NEW_COLOR = "#ff7f0e" # Orange
LOSS_COLOR = "#d62728" # Red
GAIN_COLOR = "#2ca02c" # Green

def filter_to_max_level(df, max_lvl=80):
    return df[df['level'] <= max_lvl].copy()

def chart_a1_funnel(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl)
    df_new = filter_to_max_level(df_new, max_lvl)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_old['level'], y=df_old['funnel_rate'], mode='lines', name='1.0.11 (Old)', line=dict(color=BUILD_OLD_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=df_new['level'], y=df_new['funnel_rate'], mode='lines', name='1.1.0 (New)', line=dict(color=BUILD_NEW_COLOR, width=2)))
    
    for boss in [25, 40, 44]:
        fig.add_vline(x=boss, line_dash="dash", line_color="gray", annotation_text="Boss", annotation_position="top right")
        
    fig.update_layout(title="Level Funnel Rate: Build 1.0.11 vs 1.1.0", xaxis_title="Level", yaxis_title="Funnel Rate", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_a2_is_gap(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl)
    df_new = filter_to_max_level(df_new, max_lvl)
    merged = pd.merge(df_old[['level', 'cum_avg_is_imp']], df_new[['level', 'cum_avg_is_imp']], on='level', suffixes=('_old', '_new'))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['cum_avg_is_imp_old'], mode='lines', name='1.0.11 (Old)', line=dict(color=BUILD_OLD_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['cum_avg_is_imp_new'], mode='lines', name='1.1.0 (New)', line=dict(color=BUILD_NEW_COLOR, width=2), fill='tonexty', fillcolor='rgba(214, 39, 40, 0.2)'))
    
    delta_80 = merged.iloc[-1]['cum_avg_is_imp_old'] - merged.iloc[-1]['cum_avg_is_imp_new']
    fig.add_annotation(x=80, y=merged.iloc[-1]['cum_avg_is_imp_new'], text=f"Δ = {delta_80:.2f} imp/user", showarrow=True, arrowhead=1)
    
    fig.update_layout(title="Cumulative Avg IS Impressions per User", xaxis_title="Level", yaxis_title="Cum Avg IS Imp", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_a3_rw_breakdown(df_new, max_lvl=80):
    df_new = filter_to_max_level(df_new, max_lvl).copy()
    df_new['level_bin'] = ((df_new['level'] - 1) // 5) * 5 + 1
    cols = ['rw_star_imp', 'rw_coin_imp', 'rw_heart_imp', 'rw_hint_booster_imp', 'rw_eraser_booster_imp', 'rw_wand_booster_imp', 'rw_grid_booster_imp']
    binned = df_new.groupby('level_bin')[cols].sum().reset_index()
    binned['level_label'] = binned['level_bin'].apply(lambda x: f"{x}-{x+4}")
    
    colors = {'rw_star_imp': '#f1c40f', 'rw_coin_imp': '#95a5a6', 'rw_heart_imp': '#e74c3c', 'rw_hint_booster_imp': '#2ecc71', 'rw_eraser_booster_imp': '#9b59b6', 'rw_wand_booster_imp': '#3498db', 'rw_grid_booster_imp': '#e67e22'}
    
    fig = go.Figure()
    for col in cols:
        fig.add_trace(go.Bar(x=binned['level_label'], y=binned[col], name=col.replace('_imp',''), marker_color=colors[col]))
        
    fig.update_layout(barmode='stack', title="RW Impression Breakdown by Type (Build 1.1.0)", xaxis_title="Level (Binned)", yaxis_title="Total RW Impressions", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_a4_heart_waterfall(df_heart, max_lvl=80):
    df_heart = filter_to_max_level(df_heart, max_lvl)
    fig = go.Figure()
    
    fig.add_trace(go.Bar(x=df_heart['level'], y=df_heart['out_of_lives_dropped'], name='Dropped', marker_color='#c0392b'))
    fig.add_trace(go.Bar(x=df_heart['level'], y=df_heart['out_of_lives_passed_sameday'], name='Passed Same Day', marker_color='#27ae60'))
    fig.add_trace(go.Bar(x=df_heart['level'], y=df_heart['out_of_lives_passed_later'], name='Returned Later', marker_color='#2980b9'))
    
    for boss in [25, 40, 44]:
        fig.add_vline(x=boss, line_dash="dot", line_color="black")
        row = df_heart[df_heart['level'] == boss]
        if not row.empty:
            total = row['total_out_of_lives_users'].values[0]
            fig.add_annotation(x=boss, y=total + 5, text=f"{total}", showarrow=False, font=dict(color="red", weight="bold"))
            
    fig.update_layout(barmode='stack', title="Out-of-Lives Behavior by Level (Build 1.1.0)", xaxis_title="Level", yaxis_title="Users", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_a5_revenue_delta(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl).copy()
    df_new = filter_to_max_level(df_new, max_lvl).copy()
    df_old['level_bin'] = ((df_old['level'] - 1) // 5) * 5 + 1
    df_new['level_bin'] = ((df_new['level'] - 1) // 5) * 5 + 1
    
    binned_old = df_old.groupby('level_bin')[['ad_is_revenue', 'ad_rw_revenue']].sum().reset_index()
    binned_new = df_new.groupby('level_bin')[['ad_is_revenue', 'ad_rw_revenue']].sum().reset_index()
    merged = pd.merge(binned_old, binned_new, on='level_bin', suffixes=('_old', '_new'))
    merged['level_label'] = merged['level_bin'].apply(lambda x: f"{x}-{x+4}")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=merged['level_label'], y=merged['ad_is_revenue_old'], name='IS Rev (1.0.11)', marker_color='#1f77b4'))
    fig.add_trace(go.Bar(x=merged['level_label'], y=merged['ad_is_revenue_new'], name='IS Rev (1.1.0)', marker_color='#aec7e8'))
    fig.add_trace(go.Bar(x=merged['level_label'], y=merged['ad_rw_revenue_old'], name='RW Rev (1.0.11)', marker_color='#ff7f0e'))
    fig.add_trace(go.Bar(x=merged['level_label'], y=merged['ad_rw_revenue_new'], name='RW Rev (1.1.0)', marker_color='#ffbb78'))
    
    fig.update_layout(barmode='group', title="Ad Revenue Comparison: IS vs RW by Level", xaxis_title="Level (Binned)", yaxis_title="Revenue ($)", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_a6_net_revenue(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl)
    df_new = filter_to_max_level(df_new, max_lvl)
    is_lost = df_new['ad_is_revenue'].sum() - df_old['ad_is_revenue'].sum()
    rw_gained = df_new['ad_rw_revenue'].sum() - df_old['ad_rw_revenue'].sum()
    net_impact = is_lost + rw_gained
    
    categories = ['IS Revenue Lost', 'RW Revenue Gained', 'Net Impact']
    values = [is_lost, rw_gained, net_impact]
    colors = [LOSS_COLOR, GAIN_COLOR, LOSS_COLOR if net_impact < 0 else GAIN_COLOR]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=categories, y=values, marker_color=colors, text=[f"${v:.2f}" for v in values], textposition='auto'))
    
    fig.update_layout(title="Net Ad Revenue Impact: Heart Mechanism (L1-80)", yaxis_title="Delta Revenue ($)", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_c1_rw_heart_funnel(df_heart, max_lvl=80):
    df = filter_to_max_level(df_heart, max_lvl)
    total_out = df['total_out_of_lives_users'].sum()
    total_rw = df['rw_heart_imp'].sum() + df['rw_home_heart_imp'].sum()
    total_passed = df['out_of_lives_passed_sameday'].sum()
    
    stages = ['Out of Lives', 'Watched Ad (RW)', 'Passed Same Day']
    values = [total_out, total_rw, total_passed]
    texts = [f"{v} ({(v/total_out)*100 if total_out>0 else 0:.1f}%)" for v in values]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(y=stages, x=values, orientation='h', marker_color=['#e74c3c', '#f39c12', '#2ecc71'], text=texts, textposition='auto'))
    fig.update_layout(title="RW Heart Conversion Funnel (L1-80)", margin=dict(l=20, r=20, t=40, b=20), yaxis=dict(autorange="reversed"))
    return fig

def chart_c2_fail_rate_spike(df_new, df_heart, max_lvl=80):
    df_new = filter_to_max_level(df_new, max_lvl)
    df_heart = filter_to_max_level(df_heart, max_lvl)
    merged = pd.merge(df_new[['level', 'level_fail_rate']], df_heart[['level', 'out_of_lives_dropped', 'playing_users']], on='level')
    merged['dropped_rate'] = merged['out_of_lives_dropped'] / merged['playing_users'].replace(0, np.nan)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=merged['level'], y=merged['level_fail_rate'], name='Fail Rate (New)', marker_color='#bdc3c7', yaxis='y1'))
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['dropped_rate'], name='Drop Rate (Out of Lives)', mode='lines', line=dict(color='#c0392b', width=2), yaxis='y2'))
    
    fig.update_layout(
        title="Fail Rate vs Out of Lives Drop Rate Correlation",
        xaxis=dict(title="Level"),
        yaxis=dict(title="Fail Rate", color='#7f8c8d'),
        yaxis2=dict(title="Out of Lives Drop Rate", color='#c0392b', overlaying='y', side='right'),
        hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def chart_c3_session_killer(df_heart):
    boss_levels = [25, 40, 44]
    df = df_heart[df_heart['level'].isin(boss_levels)].copy()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[f"Level {l}" for l in boss_levels], y=df['total_out_of_lives_users'], name='Total Out of Lives', marker_color='#f39c12'))
    fig.add_trace(go.Bar(x=[f"Level {l}" for l in boss_levels], y=df['out_of_lives_dropped'], name='Dropped (Quit)', marker_color='#c0392b', text=[f"{(row.out_of_lives_dropped/row.total_out_of_lives_users)*100 if row.total_out_of_lives_users>0 else 0:.0f}%" for row in df.itertuples()], textposition='outside'))
    
    fig.update_layout(barmode='group', title="Drop Rate at Boss Levels", yaxis_title="Users", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_c4_is_imp_delta(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl)
    df_new = filter_to_max_level(df_new, max_lvl)
    merged = pd.merge(df_old[['level', 'is_imp']], df_new[['level', 'is_imp']], on='level', suffixes=('_old', '_new'))
    merged['delta'] = merged['is_imp_new'] - merged['is_imp_old']
    colors = [GAIN_COLOR if d > 0 else LOSS_COLOR for d in merged['delta']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=merged['level'], y=merged['delta'], marker_color=colors, name='Delta IS Imp'))
    fig.add_hline(y=0, line_color="black")
    
    fig.update_layout(title="Per-Level IS Impression Delta (New - Old)", xaxis_title="Level", yaxis_title="Delta IS Impressions", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_c5_avg_is_normalized(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl).copy()
    df_new = filter_to_max_level(df_new, max_lvl).copy()
    df_old['avg_is'] = df_old['is_imp'] / df_old['playing_user'].replace(0, np.nan)
    df_new['avg_is'] = df_new['is_imp'] / df_new['playing_user'].replace(0, np.nan)
    df_old['smooth'] = df_old['avg_is'].rolling(5, center=True, min_periods=1).mean()
    df_new['smooth'] = df_new['avg_is'].rolling(5, center=True, min_periods=1).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_old['level'], y=df_old['smooth'], mode='lines', name='1.0.11 (Old)', line=dict(color=BUILD_OLD_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=df_new['level'], y=df_new['smooth'], mode='lines', name='1.1.0 (New)', line=dict(color=BUILD_NEW_COLOR, width=2)))
    
    fig.update_layout(title="Avg IS Impression per User per Level (Rolling Avg)", xaxis_title="Level", yaxis_title="IS / User", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_c6_rw_is_tradeoff(df_old, df_new, max_lvl=80):
    df_old = filter_to_max_level(df_old, max_lvl).copy()
    df_new = filter_to_max_level(df_new, max_lvl).copy()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_old['rw_imp'], y=df_old['is_imp'], mode='markers', name='1.0.11', marker=dict(size=df_old['playing_user']/100, sizemode='area', color=BUILD_OLD_COLOR, opacity=0.5)))
    fig.add_trace(go.Scatter(x=df_new['rw_imp'], y=df_new['is_imp'], mode='markers', name='1.1.0', marker=dict(size=df_new['playing_user']/100, sizemode='area', color=BUILD_NEW_COLOR, opacity=0.5)))
    
    fig.update_layout(title="Total RW vs IS Volume Trade-off", xaxis_title="Total RW Impressions per Level", yaxis_title="Total IS Impressions per Level", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d1_excess_stack(df_drop, max_lvl=50):
    df = df_drop[df_drop['level'] <= max_lvl].copy()
    base = df['% losed user drop base']
    var = df['% losed user drop var']
    heart_drop = df['% out of heart user drop var']
    
    var_base_part = np.minimum(base, var)
    excess = np.maximum(0, var - base)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['level'], y=base, name='Base Drop (1.0.11)', marker_color='#bdc3c7', offsetgroup=1))
    fig.add_trace(go.Bar(x=df['level'], y=var_base_part, name='Var Drop (Base equiv)', marker_color='#3498db', offsetgroup=2))
    fig.add_trace(go.Bar(x=df['level'], y=excess, name='Excess Drop', marker_color='#e74c3c', offsetgroup=2, base=var_base_part))
    
    fig.add_trace(go.Scatter(x=df['level'], y=heart_drop, mode='markers', name='Out of Heart Drop', marker=dict(symbol='diamond', size=8, color='#f1c40f', line=dict(color='black', width=1))))
    
    fig.update_layout(title="The Excess Stack: Phân tích nguyên nhân chênh lệch Drop Rate", xaxis_title="Level", yaxis_title="Drop Rate (%)", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d2_delta_isolation(df_drop, max_lvl=80):
    df = df_drop[df_drop['level'] <= max_lvl].copy()
    delta = df['% losed user drop var'] - df['% losed user drop base']
    colors = ['#e74c3c' if d > 0 else '#95a5a6' for d in delta]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['level'], y=delta, name='Delta (Var - Base)', marker_color=colors))
    fig.add_trace(go.Scatter(x=df['level'], y=df['% out of heart user drop var'], mode='lines+markers', name='Out of Heart Drop', line=dict(color='black', width=2), marker=dict(size=4)))
    
    fig.add_hline(y=0, line_color="black")
    fig.update_layout(title="Delta Isolation: Mức độ bù đắp của Heart Drop", xaxis_title="Level", yaxis_title="Difference (%)", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d3_cannibalization(df_drop, max_lvl=80):
    df = df_drop[df_drop['level'] <= max_lvl].copy()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['level'], y=df['% losed user drop var'], name='Lose Drop (New)', marker_color='#3498db'))
    fig.add_trace(go.Bar(x=df['level'], y=df['% out of heart user drop var'], name='Heart Drop (New)', marker_color='#e74c3c'))
    
    fig.add_trace(go.Scatter(x=df['level'], y=df['% losed user drop base'], mode='lines', name='Baseline Lose Drop (Old)', line=dict(color='gray', width=2, dash='dash')))
    
    fig.update_layout(barmode='stack', title="The Cannibalization View: Tổng tỷ lệ bất mãn bỏ game", xaxis_title="Level", yaxis_title="Total Drop Rate (%)", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

# --- PHẦN D: Drop Behavior Analysis ---

def chart_d1_stage_drop(df_old, df_heart_drop, df_new, max_lvl=80):
    df_old = df_old[df_old['level'] <= max_lvl].copy()
    df_heart_drop = df_heart_drop[df_heart_drop['level'] <= max_lvl].copy()
    df_new = df_new[df_new['level'] <= max_lvl].copy()
    
    # Merge avg_attempts and funnel_rate from df_new into df_heart_drop to identify stages
    df_new_info = df_new[['level', 'avg_attempts', 'funnel_rate']]
    df_hd = pd.merge(df_heart_drop, df_new_info, on='level', how='left')
    
    def get_stage(row):
        if row['level'] <= 14:
            return 'Early Stage (1-14)'
        elif row['avg_attempts'] > 2.5 or row['funnel_rate'] < 0.5:
            return 'Hard Level Stage'
        else:
            return 'Standard Stage'
            
    df_hd['stage'] = df_hd.apply(get_stage, axis=1)
    stage_map = dict(zip(df_hd['level'], df_hd['stage']))
    df_old['stage'] = df_old['level'].map(stage_map).fillna('Standard Stage')
    
    stages = ['Early Stage (1-14)', 'Standard Stage', 'Hard Level Stage']
    rates_old = []
    rates_new = []
    
    for stg in stages:
        old_subset = df_old[df_old['stage'] == stg]
        new_subset = df_hd[df_hd['stage'] == stg]
        
        old_drops = old_subset['lose_dropped_users_cohort'].sum() + old_subset['win_dropped_users_cohort'].sum()
        old_users = old_subset['playing_user'].sum()
        rates_old.append(old_drops / old_users if old_users > 0 else 0)
        
        new_drops = new_subset['lose_dropped_users_cohort'].sum() + new_subset['win_dropped_users_cohort'].sum()
        new_users = new_subset['playing_users'].sum()
        rates_new.append(new_drops / new_users if new_users > 0 else 0)
        
    fig = go.Figure()
    fig.add_trace(go.Bar(x=stages, y=rates_old, name='1.0.11 (Old)', marker_color=BUILD_OLD_COLOR))
    fig.add_trace(go.Bar(x=stages, y=rates_new, name='1.1.0 (New)', marker_color=BUILD_NEW_COLOR))
    
    fig.update_layout(title="Stage-by-Stage Drop Rate Comparison", barmode='group', yaxis_tickformat='.1%', xaxis_title="Stage", yaxis_title="Average Drop Rate", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d2_hard_frustration(df_heart_drop, df_new, max_lvl=80):
    df_hd = df_heart_drop[df_heart_drop['level'] <= max_lvl].copy()
    df_n = df_new[df_new['level'] <= max_lvl][['level', 'avg_attempts', 'funnel_rate']].copy()
    
    merged = pd.merge(df_hd, df_n, on='level')
    hard = merged[(merged['avg_attempts'] > 2.5) | (merged['funnel_rate'] < 0.5)].copy()
    
    if hard.empty:
        return go.Figure().update_layout(title="No Hard Levels found")
        
    # Stack layers
    c_churned = hard['out_of_lives_churned_cohort']
    c_lost_heart = hard['lost_heart_not_out_dropped_cohort']
    # Thua bình thường = Tổng lose dropped - c_churned - c_lost_heart
    c_thua = hard['lose_dropped_users_cohort'] - c_churned - c_lost_heart
    c_thua = c_thua.clip(lower=0)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hard['level'].astype(str), y=c_thua, name='Thua bình thường', marker_color='#95a5a6'))
    fig.add_trace(go.Bar(x=hard['level'].astype(str), y=c_lost_heart, name='Mất tim nản nghỉ', marker_color='#f1c40f'))
    fig.add_trace(go.Bar(x=hard['level'].astype(str), y=c_churned, name='Cạn máu nghỉ', marker_color='#e74c3c'))
    
    fig.update_layout(title="Hard Level Frustration (Drop Anatomy in Build 1.1.0)", barmode='stack', xaxis_title="Hard Levels", yaxis_title="Number of Users Dropped", hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d3_cum_drop(df_old, df_heart_drop, max_lvl=80):
    df_old = df_old[df_old['level'] <= max_lvl].copy().sort_values('level')
    df_hd = df_heart_drop[df_heart_drop['level'] <= max_lvl].copy().sort_values('level')
    
    users_l1_old = df_old[df_old['level'] == 1]['playing_user'].values[0] if not df_old.empty else 1
    users_l1_new = df_hd[df_hd['level'] == 1]['playing_users'].values[0] if not df_hd.empty else 1
    
    df_old['drops'] = df_old['lose_dropped_users_cohort'] + df_old['win_dropped_users_cohort']
    df_hd['drops'] = df_hd['lose_dropped_users_cohort'] + df_hd['win_dropped_users_cohort']
    
    df_old['cum_drops_pct'] = df_old['drops'].cumsum() / users_l1_old
    df_hd['cum_drops_pct'] = df_hd['drops'].cumsum() / users_l1_new
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df_old['level'], y=df_old['cum_drops_pct'], mode='lines', name='1.0.11 (Old)', line=dict(color=BUILD_OLD_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=df_hd['level'], y=df_hd['cum_drops_pct'], mode='lines', name='1.1.0 (New)', line=dict(color=BUILD_NEW_COLOR, width=2), fill='tonexty', fillcolor='rgba(231, 76, 60, 0.2)'))
    
    fig.update_layout(title="Cumulative Drop Funnel", xaxis_title="Level", yaxis_title="Cumulative Drop %", yaxis_tickformat='.1%', hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d4_drop_delta(df_old, df_heart_drop, df_new, max_lvl=80):
    df_o = df_old[df_old['level'] <= max_lvl].copy()
    df_hd = df_heart_drop[df_heart_drop['level'] <= max_lvl].copy()
    df_n = df_new[df_new['level'] <= max_lvl].copy()
    
    df_o['drop_rate_old'] = (df_o['lose_dropped_users_cohort'] + df_o['win_dropped_users_cohort']) / df_o['playing_user']
    df_hd['drop_rate_new'] = (df_hd['lose_dropped_users_cohort'] + df_hd['win_dropped_users_cohort']) / df_hd['playing_users']
    
    merged = pd.merge(df_o[['level', 'drop_rate_old']], df_hd[['level', 'drop_rate_new']], on='level')
    merged = pd.merge(merged, df_n[['level', 'avg_attempts', 'funnel_rate']], on='level')
    
    merged['delta'] = merged['drop_rate_new'] - merged['drop_rate_old']
    colors = ['#e74c3c' if d > 0 else '#2ca02c' for d in merged['delta']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=merged['level'], y=merged['delta'], name='Drop Rate Delta (New - Old)', marker_color=colors))
    
    # Background for Early Stage
    fig.add_vrect(x0=0.5, x1=14.5, fillcolor="gray", opacity=0.1, layer="below", line_width=0, annotation_text="Early Stage (1-14)", annotation_position="top left")
    
    # Red vrects for Hard Levels
    hard_levels = merged[(merged['avg_attempts'] > 2.5) | (merged['funnel_rate'] < 0.5)]['level'].tolist()
    for hl in hard_levels:
        fig.add_vrect(x0=hl-0.4, x1=hl+0.4, fillcolor="red", opacity=0.1, layer="below", line_width=0)
        
    fig.update_layout(title="Per-Level Drop Rate Delta Overlay", xaxis_title="Level", yaxis_title="Delta (Absolute)", yaxis_tickformat='.1%', hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20))
    return fig

def chart_d5_causality(df_old, df_heart_drop, df_new, max_lvl=80):
    df_o = df_old[df_old['level'] <= max_lvl].copy()
    df_hd = df_heart_drop[df_heart_drop['level'] <= max_lvl].copy()
    
    # Calculate baseline rates (1.0.11)
    df_o['base_drop_rate'] = df_o['lose_dropped_users_cohort'] / df_o['playing_user'].replace(0, float('nan'))
    df_o['base_win_rate'] = df_o['funnel_rate']  # rough approximation for win rate
    
    # Calculate rates for heart impact groups (1.1.0)
    df_hd['lost_heart_drop_rate'] = df_hd['lost_heart_not_out_dropped_cohort'] / df_hd['lost_heart_not_out_users'].replace(0, float('nan'))
    df_hd['lost_heart_win_rate'] = df_hd['lost_heart_not_out_won'] / df_hd['lost_heart_not_out_users'].replace(0, float('nan'))
    
    df_hd['out_of_lives_drop_rate'] = df_hd['out_of_lives_churned_cohort'] / df_hd['total_out_of_lives_users'].replace(0, float('nan'))
    df_hd['out_of_lives_return_rate'] = df_hd['out_of_lives_returned_users'] / df_hd['total_out_of_lives_users'].replace(0, float('nan'))
    
    merged = pd.merge(df_o[['level', 'base_drop_rate']], df_hd, on='level', how='inner')
    
    # Smoothing lines for clearer trend
    w = 3
    for col in ['base_drop_rate', 'lost_heart_drop_rate', 'out_of_lives_drop_rate', 'lost_heart_win_rate', 'out_of_lives_return_rate']:
        merged[col+'_smooth'] = merged[col].rolling(window=w, min_periods=1, center=True).mean()
    
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        subplot_titles=("1. Drop Rate Comparison (Do users drop more when losing hearts?)", 
                                        "2. Win vs Return Rate (Are they retrying/returning?)"))
    
    # --- Subplot 1: Drop Rates ---
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['base_drop_rate_smooth'], mode='lines', name='Base Drop Rate (1.0.11)', line=dict(color='gray', width=2, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['lost_heart_drop_rate_smooth'], mode='lines', name='Drop Rate: Mất <5 tim', line=dict(color='#f1c40f', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['out_of_lives_drop_rate_smooth'], mode='lines', name='Drop Rate: Cạn máu', line=dict(color='#e74c3c', width=3)), row=1, col=1)
    
    # --- Subplot 2: Win & Return Rates ---
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['lost_heart_win_rate_smooth'], mode='lines', name='Win Rate (khi mất <5 tim)', line=dict(color='#2ecc71', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=merged['level'], y=merged['out_of_lives_return_rate_smooth'], mode='lines', name='Return Rate (khi cạn máu)', line=dict(color='#3498db', width=2)), row=2, col=1)
    
    fig.update_layout(
        title="Impact of Heart Loss per Level (Smoothed)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.05)
    )
    fig.update_yaxes(title_text="Drop Rate (%)", tickformat='.1%', row=1, col=1)
    fig.update_yaxes(title_text="Rate (%)", tickformat='.1%', row=2, col=1)
    fig.update_xaxes(title_text="Level", row=2, col=1)
    
    return fig


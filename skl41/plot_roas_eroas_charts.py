import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def calculate_roas_eroas(df, days, date_col='install_date'):
    organic_sources = ['organic', '(organic)', 'google_organic_search']
    
    # Maturity filter
    max_date = pd.to_datetime(df[date_col].max())
    mature_date = max_date - pd.Timedelta(days=days)
    df_mature = df[pd.to_datetime(df[date_col]) <= mature_date].copy()
    
    if df_mature.empty:
        return pd.DataFrame()

    df_mature['date'] = pd.to_datetime(df_mature[date_col])
    df_mature['week'] = df_mature['date'].dt.to_period('W').apply(lambda r: r.start_time)
    
    df_mature['is_paid'] = ~df_mature['media_source'].str.lower().isin(organic_sources)
    
    ltv_col = f'ltv_d{days}'
    if ltv_col not in df_mature.columns:
        return pd.DataFrame()
        
    # We will compute metrics for 'date' (daily) and 'week' (weekly)
    results = []
    for time_col in ['date', 'week']:
        grouped = df_mature.groupby(time_col)
        
        for name, group in grouped:
            # Paid metrics
            paid_group = group[group['is_paid']]
            paid_users = paid_group['total_cohort_users'].sum()
            paid_spend = paid_group['cohort_ad_spend'].sum()
            paid_rev = (paid_group['total_cohort_users'] * paid_group[ltv_col]).sum()
            
            paid_ltv = paid_rev / paid_users if paid_users > 0 else 0
            paid_cpi = paid_spend / paid_users if paid_users > 0 else 0
            
            # All metrics
            all_users = group['total_cohort_users'].sum()
            all_rev = (group['total_cohort_users'] * group[ltv_col]).sum()
            all_ltv = all_rev / all_users if all_users > 0 else 0
            
            # If CPI is 0, replace with NaN
            if paid_cpi == 0:
                roas = np.nan
                eroas = np.nan
            else:
                roas = paid_ltv / paid_cpi
                eroas = all_ltv / paid_cpi
                
            results.append({
                'time_col': time_col,
                'period': name,
                'ROAS': roas,
                'eROAS': eroas,
                'Paid_CPI': paid_cpi
            })
            
    return pd.DataFrame(results)

def plot_charts():
    df = pd.read_csv(r"d:\skylink\data\skl41\retention&ltv.csv")
    sns.set_theme(style="whitegrid")
    
    for d in [0, 7, 30]:
        res_df = calculate_roas_eroas(df, d)
        if res_df.empty:
            continue
            
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Daily
        daily_df = res_df[res_df['time_col'] == 'date'].sort_values('period')
        ax1 = axes[0]
        ax1.plot(daily_df['period'], daily_df['ROAS'], label='ROAS', color='blue', linewidth=2)
        ax1.plot(daily_df['period'], daily_df['eROAS'], label='eROAS', color='orange', linewidth=2)
        ax1.set_title(f'Daily ROAS D{d} vs eROAS D{d}', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ratio')
        ax1.legend()
        
        # Weekly
        weekly_df = res_df[res_df['time_col'] == 'week'].sort_values('period')
        ax2 = axes[1]
        ax2.plot(weekly_df['period'], weekly_df['ROAS'], label='ROAS', color='blue', marker='o', linewidth=2)
        ax2.plot(weekly_df['period'], weekly_df['eROAS'], label='eROAS', color='orange', marker='o', linewidth=2)
        ax2.set_title(f'Weekly ROAS D{d} vs eROAS D{d}', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Ratio')
        ax2.legend()
        
        plt.tight_layout()
        out_file = f"roas_eroas_d{d}.png"
        plt.savefig(out_file, dpi=300)
        print(f"Saved {out_file}")

if __name__ == "__main__":
    plot_charts()

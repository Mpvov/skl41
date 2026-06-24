import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os

def main():
    # File paths
    roas_file = r"d:\skylink\data\skl41\roas.csv"

    print("Loading data...")
    # Load ROAS data
    df = pd.read_csv(roas_file)
    
    # Exclude IN and VN if needed, but let's just stick to the basic calculation
    # In dashboard tab Ad Spend, there wasn't an explicit exclude except if applied globally.
    # To be consistent with previous DAU, I'll exclude them.
    if 'country_code' in df.columns:
        df = df[~df['country_code'].isin(['IN', 'VN'])]
        
    df['install_date'] = pd.to_datetime(df['install_date'])

    def agg_eff(x):
        tot_spend = x['cohort_ad_spend'].sum()
        tot_users = x['total_cohort_users'].sum()
        avg_cpi = tot_spend / tot_users if tot_users > 0 else 0
        
        # Calculate ROAS D7 weighted by ad spend
        if 'roas_d7' in x.columns:
            tot_rev_d7 = (x['roas_d7'] * x['cohort_ad_spend']).sum()
            roas_d7_avg = tot_rev_d7 / tot_spend if tot_spend > 0 else 0
        else:
            roas_d7_avg = float('nan')
            
        return pd.Series({'cohort_ad_spend': tot_spend, 'roas_d7_avg': roas_d7_avg, 'avg_cpi': avg_cpi})

    daily_eff = df.groupby('install_date').apply(agg_eff, include_groups=False).reset_index()
    daily_eff = daily_eff.sort_values('install_date')

    print("Creating chart using Matplotlib...")
    sns.set_theme(style="whitegrid")
    
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Bar chart for Ad Spend
    color_spend = '#37536d'
    ax1.set_xlabel('Install Date', fontweight='bold')
    ax1.set_ylabel('Ad Spend ($)', color=color_spend, fontweight='bold')
    ax1.bar(daily_eff['install_date'], daily_eff['cohort_ad_spend'], color=color_spend, alpha=0.7, label='Ad Spend')
    ax1.tick_params(axis='y', labelcolor=color_spend)
    
    # Format x-axis dates
    plt.xticks(rotation=45, ha='right')

    # Line chart for ROAS D7 on secondary Y axis
    ax2 = ax1.twinx()
    color_roas = 'tab:orange'
    ax2.set_ylabel('ROAS D7', color=color_roas, fontweight='bold')
    ax2.plot(daily_eff['install_date'], daily_eff['roas_d7_avg'], color=color_roas, marker='o', linewidth=3, markersize=6, label='Avg ROAS D7')
    ax2.tick_params(axis='y', labelcolor=color_roas)
    
    # Format Y axis as percentage
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    # Set title and layout
    plt.title('Efficiency: Ad Spend vs ROAS D7 (Daily)', fontsize=16, fontweight='bold', pad=20)
    fig.tight_layout()

    # Save to PNG file
    out_file = "efficiency_ad_spend.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    print(f"Chart successfully generated and saved to: {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()

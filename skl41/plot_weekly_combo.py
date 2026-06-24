import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    # File paths
    dau_file = r"d:\skylink\data\skl41\DAU.csv"
    ret_file = r"d:\skylink\data\skl41\retention&ltv.csv"

    print("Loading data...")
    # Load DAU data
    dau_df = pd.read_csv(dau_file)
    # Exclude IN and VN
    dau_df = dau_df[~dau_df['country_code'].isin(['IN', 'VN'])]
    # Calculate daily total DAU, then average it per week
    dau_daily = dau_df.groupby('event_date')['total_dau'].sum().reset_index()
    dau_daily['week'] = pd.to_datetime(dau_daily['event_date']).dt.to_period('W').apply(lambda r: r.start_time)
    dau_weekly = dau_daily.groupby('week')['total_dau'].mean().reset_index()
    dau_weekly.rename(columns={'total_dau': 'Avg_DAU'}, inplace=True)

    # Load Retention (Ad Spend) data
    ret_df = pd.read_csv(ret_file)
    # Exclude IN and VN
    ret_df = ret_df[~ret_df['country_code'].isin(['IN', 'VN'])]
    ret_df['week'] = pd.to_datetime(ret_df['install_date']).dt.to_period('W').apply(lambda r: r.start_time)
    spend_weekly = ret_df.groupby('week')['cohort_ad_spend'].sum().reset_index()

    # Merge data
    combo_df = pd.merge(spend_weekly, dau_weekly, on='week', how='outer').fillna(0).sort_values('week')
    
    # Ensure weeks are formatted as strings for consistent categorical X axis
    combo_df['week_str'] = combo_df['week'].dt.strftime('%Y-%m-%d')

    print("Creating chart using Matplotlib/Seaborn...")
    sns.set_theme(style="whitegrid")
    
    # Create Combo Chart
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Bar chart for Ad Spend
    color = '#37536d'
    ax1.set_xlabel('Week', fontweight='bold')
    ax1.set_ylabel('Weekly Ad Spend ($)', color=color, fontweight='bold')
    sns.barplot(data=combo_df, x='week_str', y='cohort_ad_spend', color=color, alpha=0.7, ax=ax1)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.xticks(rotation=45, ha='right')

    # Line chart for DAU on secondary Y axis
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Weekly Avg DAU', color=color2, fontweight='bold')
    # Use ax2.plot instead of sns.lineplot to ensure it aligns perfectly with categorical bar chart centers
    ax2.plot(ax1.get_xticks(), combo_df['Avg_DAU'], color=color2, marker='o', linewidth=3, markersize=8, label='Avg DAU')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Set title and layout
    plt.title('Weekly Ad Spend vs DAU', fontsize=16, fontweight='bold', pad=20)
    fig.tight_layout()

    # Save to PNG file
    out_file = "weekly_spend_vs_dau.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    print(f"Chart successfully generated and saved to: {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()

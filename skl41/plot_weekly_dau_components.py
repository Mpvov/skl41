import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    # File paths
    dau_file = r"d:\skylink\data\skl41\DAU.csv"

    print("Loading data...")
    # Load DAU data
    dau_df = pd.read_csv(dau_file)
    
    # Exclude IN and VN
    dau_df = dau_df[~dau_df['country_code'].isin(['IN', 'VN'])]
    
    # Calculate daily totals
    dau_daily = dau_df.groupby('event_date')[['total_dau', 'new_users', 'return_users']].sum().reset_index()
    
    # Calculate weekly averages
    dau_daily['week'] = pd.to_datetime(dau_daily['event_date']).dt.to_period('W').apply(lambda r: r.start_time)
    dau_weekly = dau_daily.groupby('week')[['total_dau', 'new_users', 'return_users']].mean().reset_index()
    
    # Ensure weeks are formatted as strings for consistent categorical X axis
    dau_weekly['week_str'] = dau_weekly['week'].dt.strftime('%Y-%m-%d')

    print("Creating chart using Matplotlib/Seaborn...")
    sns.set_theme(style="whitegrid")
    
    # Create Combo Chart
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # Stacked Bar chart for New Users and Return Users
    # To do stacked bars in seaborn/matplotlib, we can plot return_users + new_users, then new_users on top, 
    # but pandas built-in plot is easier for stacked bars. We will use matplotlib bar directly.
    
    ax1.set_xlabel('Week', fontweight='bold')
    ax1.set_ylabel('Avg Users', fontweight='bold')
    
    # Plot all metrics as line charts
    ax1.plot(dau_weekly['week_str'], dau_weekly['total_dau'], color='tab:red', marker='o', linewidth=3, markersize=8, label='Avg DAU (Total)')
    ax1.plot(dau_weekly['week_str'], dau_weekly['return_users'], color='tab:cyan', marker='s', linewidth=2.5, markersize=6, label='Return Users')
    ax1.plot(dau_weekly['week_str'], dau_weekly['new_users'], color='tab:blue', marker='^', linewidth=2.5, markersize=6, label='New Installs')
    
    plt.xticks(rotation=45, ha='right')

    # Set title and layout
    plt.title('Weekly Avg DAU, New Installs & Return Users', fontsize=16, fontweight='bold', pad=20)
    
    # Add legend
    ax1.legend(loc='upper left', fontsize=11)
    
    fig.tight_layout()

    # Save to PNG file
    out_file = "weekly_dau_components.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    print(f"Chart successfully generated and saved to: {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()

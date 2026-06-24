import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    dau_file = r"d:\skylink\data\skl41\DAU.csv"
    print("Loading data...")
    
    # Read data
    df = pd.read_csv(dau_file)
    
    # Filter out IN and VN (keeping consistency with previous logic)
    df = df[~df['country_code'].isin(['IN', 'VN'])]
    
    # Define traffic types
    organic_sources = ['organic', '(organic)', 'google_organic_search']
    
    # Add traffic type column
    df['traffic_type'] = df['channel'].apply(
        lambda x: 'Organic' if str(x).lower() in organic_sources else 'Non-Organic'
    )
    
    # Group by date and traffic type
    daily_traffic = df.groupby(['event_date', 'traffic_type'])['new_users'].sum().reset_index()
    
    # Calculate 'All' traffic
    daily_all = df.groupby('event_date')['new_users'].sum().reset_index()
    daily_all['traffic_type'] = 'All'
    
    # Combine all data
    plot_df = pd.concat([daily_traffic, daily_all], ignore_index=True)
    
    # Convert event_date to datetime for plotting
    plot_df['event_date'] = pd.to_datetime(plot_df['event_date'])
    plot_df = plot_df.sort_values('event_date')

    print("Creating chart using Matplotlib/Seaborn...")
    sns.set_theme(style="whitegrid")
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Define color palette
    palette = {'Organic': 'tab:green', 'Non-Organic': 'tab:orange', 'All': 'tab:blue'}
    
    sns.lineplot(
        data=plot_df, 
        x='event_date', 
        y='new_users', 
        hue='traffic_type', 
        palette=palette,
        linewidth=2.5,
        ax=ax
    )
    
    # Customize the axes and title
    ax.set_title('Installs (New Users) by Traffic Type', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Installs', fontsize=12, fontweight='bold')
    
    plt.xticks(rotation=45)
    plt.legend(title='Traffic Type', title_fontsize='13', fontsize='11')
    
    fig.tight_layout()

    # Save to PNG file
    out_file = "installs_by_traffic.png"
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    print(f"Chart successfully generated and saved to: {os.path.abspath(out_file)}")

if __name__ == "__main__":
    main()

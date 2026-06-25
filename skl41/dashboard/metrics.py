import pandas as pd
import numpy as np

def calculate_ad_revenue(df, group_by_col=None):
    if df.empty:
        return pd.DataFrame() if group_by_col else 0.0
    if group_by_col:
        return df.groupby(group_by_col)['total_ad_revenue'].sum().reset_index()
    return df['total_ad_revenue'].sum()

def calculate_ad_impressions(df, group_by_col=None):
    if df.empty:
        return pd.DataFrame() if group_by_col else 0
    if group_by_col:
        return df.groupby(group_by_col)['total_ad_impression'].sum().reset_index()
    return df['total_ad_impression'].sum()

def calculate_ecpm(df, group_by_col=None):
    if df.empty:
        return pd.DataFrame() if group_by_col else 0.0
        
    if group_by_col:
        grouped = df.groupby(group_by_col).agg(
            revenue=('total_ad_revenue', 'sum'),
            impressions=('total_ad_impression', 'sum')
        ).reset_index()
        grouped['ecpm'] = (grouped['revenue'] / grouped['impressions']) * 1000
        grouped['ecpm'] = grouped['ecpm'].fillna(0)
        return grouped
        
    total_rev = df['total_ad_revenue'].sum()
    total_imp = df['total_ad_impression'].sum()
    return (total_rev / total_imp) * 1000 if total_imp > 0 else 0.0

def calculate_dau(df, group_by_col=None):
    if df.empty:
        return pd.DataFrame() if group_by_col else 0
    
    dau_col = 'total_dau' if 'total_dau' in df.columns else 'dau'
    if dau_col not in df.columns:
        return pd.DataFrame() if group_by_col else 0
        
    if group_by_col:
        cols_to_sum = [dau_col]
        if 'new_users' in df.columns:
            cols_to_sum.append('new_users')
        if 'return_users' in df.columns:
            cols_to_sum.append('return_users')
        return df.groupby(group_by_col)[cols_to_sum].sum().reset_index()
    return df[dau_col].sum()

def calculate_retention_curve(df):
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby('day_since_install').agg(
        active_users=('active_users', 'sum'),
        cohort_installs=('total_cohort_installs', 'sum')
    ).reset_index()
    grouped['retention_rate'] = grouped['active_users'] / grouped['cohort_installs'].replace(0, pd.NA)
    grouped['retention_rate'] = grouped['retention_rate'].fillna(0)
    return grouped

def calculate_ltv_curve(df):
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby('day_since_install').agg(
        cumulative_revenue=('cumulative_revenue', 'sum'),
        cohort_installs=('total_cohort_installs', 'sum')
    ).reset_index()
    grouped['ltv'] = grouped['cumulative_revenue'] / grouped['cohort_installs'].replace(0, pd.NA)
    grouped['ltv'] = grouped['ltv'].fillna(0)
    return grouped

def calculate_roas_curve(df):
    if df.empty:
        return pd.DataFrame()
    grouped = df.groupby('day_since_install').agg(
        cumulative_revenue=('cumulative_revenue', 'sum'),
        cohort_spend=('total_cohort_ad_spend', 'sum')
    ).reset_index()
    grouped['roas'] = grouped['cumulative_revenue'] / grouped['cohort_spend'].replace(0, pd.NA)
    grouped['roas'] = grouped['roas'].fillna(0)
    return grouped

def get_kpi_at_day(curve_df, metric_col, day):
    if curve_df.empty or 'day_since_install' not in curve_df.columns:
        return 0.0
    row = curve_df[curve_df['day_since_install'] == day]
    if not row.empty:
        return row.iloc[0][metric_col]
    return 0.0

def get_max_day_kpi(curve_df, metric_col):
    if curve_df.empty or 'day_since_install' not in curve_df.columns:
        return 0.0
    max_day = curve_df['day_since_install'].max()
    row = curve_df[curve_df['day_since_install'] == max_day]
    if not row.empty:
        return row.iloc[0][metric_col]
    return 0.0

def calculate_sum_r(retention_curve_df, up_to_day):
    if retention_curve_df.empty or 'day_since_install' not in retention_curve_df.columns:
        return 0.0
    df_filtered = retention_curve_df[retention_curve_df['day_since_install'] <= up_to_day]
    return df_filtered['retention_rate'].sum()

def calculate_total_installs(df):
    if df.empty:
        return 0
    if 'total_cohort_users' in df.columns:
        return df['total_cohort_users'].sum()
    if 'total_cohort_installs' in df.columns:
        return df['total_cohort_installs'].sum()
    return 0

def calculate_total_ad_spend(df):
    if df.empty:
        return 0
    if 'cohort_ad_spend' in df.columns:
        return df['cohort_ad_spend'].sum()
    if 'total_cohort_ad_spend' in df.columns:
        return df['total_cohort_ad_spend'].sum()
    return 0

def calculate_roas_d30_by_date(df):
    if df.empty:
        return pd.DataFrame()
    d30_df = df[df['day_since_install'] == 30]
    grouped = d30_df.groupby('install_date').agg(
        cumulative_revenue=('cumulative_revenue', 'sum'),
        cohort_spend=('total_cohort_ad_spend', 'sum')
    ).reset_index()
    grouped['roas_d30'] = grouped['cumulative_revenue'] / grouped['cohort_spend'].replace(0, pd.NA)
    grouped['roas_d30'] = grouped['roas_d30'].fillna(0)
    return grouped

def calculate_retention_by_date(df):
    if df.empty:
        return pd.DataFrame()
    filtered = df[df['day_since_install'].isin([1, 3, 7])]
    if filtered.empty:
        return pd.DataFrame()
        
    grouped = filtered.groupby(['install_date', 'day_since_install']).agg(
        active_users=('active_users', 'sum'),
        cohort_installs=('total_cohort_installs', 'sum')
    ).reset_index()
    grouped['retention_rate'] = grouped['active_users'] / grouped['cohort_installs'].replace(0, pd.NA)
    grouped['retention_rate'] = grouped['retention_rate'].fillna(0)
    
    pivot = grouped.pivot(index='install_date', columns='day_since_install', values='retention_rate').reset_index()
    pivot.columns.name = None
    
    cols_to_keep = ['install_date']
    rename_dict = {}
    if 1 in pivot.columns:
        rename_dict[1] = 'R1'
        cols_to_keep.append('R1')
    if 3 in pivot.columns:
        rename_dict[3] = 'R3'
        cols_to_keep.append('R3')
    if 7 in pivot.columns:
        rename_dict[7] = 'R7'
        cols_to_keep.append('R7')
        
    pivot.rename(columns=rename_dict, inplace=True)
    return pivot[cols_to_keep]

def calculate_retention_kpis_from_csv(df):
    if df.empty:
        return {}
    
    kpis = {}
    max_date = df['install_date'].max()
    
    maturity_days = {
        'retention_r1': 1, 'retention_r3': 3, 'retention_r7': 7, 
        'retention_r14': 14, 'retention_r30': 30,
        'sumR3': 3, 'sumR7': 7, 'sumR14': 14, 'sumR30': 30
    }
    
    for col, key in [('retention_r1', 'R1'), ('retention_r3', 'R3'), ('retention_r7', 'R7'), 
                     ('retention_r14', 'R14'), ('retention_r30', 'R30'),
                     ('sumR3', 'SumR3'), ('sumR7', 'SumR7'), ('sumR14', 'SumR14'), ('sumR30', 'SumR30')]:
        if col in df.columns:
            required_days = maturity_days.get(col, 0)
            # Add 1 day buffer
            mature_date_end = max_date - pd.Timedelta(days=required_days + 1)
            mature_df = df[df['install_date'] <= mature_date_end]
            
            total_mature_users = mature_df['total_cohort_users'].sum()
            if total_mature_users > 0:
                weighted_sum = (mature_df[col] * mature_df['total_cohort_users']).sum()
                kpis[key] = weighted_sum / total_mature_users
            else:
                kpis[key] = 0.0
        
    return kpis

def calculate_retention_by_date_from_csv(df):
    if df.empty:
        return pd.DataFrame()
    
    metrics_cols = [c for c in ['retention_r1', 'retention_r3', 'retention_r7', 'retention_r14', 'retention_r30',
                                'sumR3', 'sumR7', 'sumR14', 'sumR30'] if c in df.columns]
    
    # We need to compute weighted average by install_date
    # Multiply metrics by total_cohort_users
    temp_df = df[['install_date', 'total_cohort_users'] + metrics_cols].copy()
    for col in metrics_cols:
        temp_df[col] = temp_df[col] * temp_df['total_cohort_users']
        
    grouped = temp_df.groupby('install_date').sum().reset_index()
    
    max_date = df['install_date'].max()
    maturity_days = {
        'retention_r1': 1, 'retention_r3': 3, 'retention_r7': 7, 
        'retention_r14': 14, 'retention_r30': 30,
        'sumR3': 3, 'sumR7': 7, 'sumR14': 14, 'sumR30': 30
    }
    
    # Divide by total_cohort_users to get the weighted average
    for col in metrics_cols:
        grouped[col] = grouped[col] / grouped['total_cohort_users'].replace(0, pd.NA)
        
        # Set immature dates to NaN so line charts don't drop to zero
        # Add 1 day buffer to ensure the required day is fully complete
        required_days = maturity_days.get(col, 0)
        mature_date_end = max_date - pd.Timedelta(days=required_days + 1)
        grouped.loc[grouped['install_date'] > mature_date_end, col] = np.nan
        
    return grouped

def calculate_ltv_kpis_from_csv(df):
    if df.empty:
        return {}
        
    kpis = {}
    max_date = df['install_date'].max()
    
    maturity_days = {
        'ltv_d1': 1,
        'ltv_d3': 3,
        'ltv_d7': 7,
        'ltv_d14': 14,
        'ltv_d30': 30
    }
    
    for col, key in [('ltv_d1', 'LTV D1'), ('ltv_d3', 'LTV D3'), ('ltv_d7', 'LTV D7'), 
                     ('ltv_d14', 'LTV D14'), ('ltv_d30', 'LTV D30')]:
        if col in df.columns:
            required_days = maturity_days.get(col, 0)
            # Add 1 day buffer
            mature_date_end = max_date - pd.Timedelta(days=required_days + 1)
            mature_df = df[df['install_date'] <= mature_date_end]
            
            total_mature_users = mature_df['total_cohort_users'].sum()
            if total_mature_users > 0:
                weighted_sum = (mature_df[col] * mature_df['total_cohort_users']).sum()
                kpis[key] = weighted_sum / total_mature_users
            else:
                kpis[key] = 0.0
            
    return kpis

def calculate_ltv_by_date_from_csv(df):
    if df.empty:
        return pd.DataFrame()
    
    metrics_cols = [c for c in ['ltv_d0', 'ltv_d1', 'ltv_d3', 'ltv_d7', 'ltv_d14', 'ltv_d30'] if c in df.columns]
    
    temp_df = df[['install_date', 'total_cohort_users'] + metrics_cols].copy()
    for col in metrics_cols:
        temp_df[col] = temp_df[col] * temp_df['total_cohort_users']
        
    grouped = temp_df.groupby('install_date').sum().reset_index()
    
    max_date = df['install_date'].max()
    maturity_days = {
        'ltv_d0': 0, 'ltv_d1': 1, 'ltv_d3': 3, 
        'ltv_d7': 7, 'ltv_d14': 14, 'ltv_d30': 30
    }
    
    for col in metrics_cols:
        grouped[col] = grouped[col] / grouped['total_cohort_users'].replace(0, pd.NA)
        
        required_days = maturity_days.get(col, 0)
        mature_date_end = max_date - pd.Timedelta(days=required_days)
        grouped.loc[grouped['install_date'] > mature_date_end, col] = np.nan
        
    return grouped

def calculate_roas_by_date_from_csv(df, ad_spend_raw_df=None):
    if df.empty or 'total_cohort_users' not in df.columns:
        return pd.DataFrame()

    if ad_spend_raw_df is None or ad_spend_raw_df.empty or 'cost' not in ad_spend_raw_df.columns:
        return pd.DataFrame()

    metrics_cols = [c for c in ['ltv_d0', 'ltv_d1', 'ltv_d3', 'ltv_d7', 'ltv_d14', 'ltv_d30'] if c in df.columns]
    if not metrics_cols:
        return pd.DataFrame()

    df['install_date'] = pd.to_datetime(df['install_date'])
    ad_spend_raw_df['day'] = pd.to_datetime(ad_spend_raw_df['day'])

    # Campaign ROAS (Paid Traffic Only - excluding organic)
    organic_sources = ['organic', '(organic)', 'google_organic_search']
    if 'media_source' in df.columns:
        paid_df = df[~df['media_source'].isin(organic_sources)][['install_date', 'total_cohort_users'] + metrics_cols].copy()
    else:
        paid_df = df[df['cohort_ad_spend'] > 0][['install_date', 'total_cohort_users'] + metrics_cols].copy()

    # Blended ROAS (All Traffic)
    all_df = df[['install_date', 'total_cohort_users'] + metrics_cols].copy()

    # Aggregate Ad Spend by date
    daily_spend = ad_spend_raw_df.groupby('day')['cost'].sum().reset_index()
    daily_spend.rename(columns={'day': 'install_date'}, inplace=True)

    max_date = df['install_date'].max()
    result = pd.DataFrame({'install_date': sorted(df['install_date'].unique())})
    result = pd.merge(result, daily_spend, on='install_date', how='left')
    result['cost'] = result['cost'].fillna(0)

    for col in metrics_cols:
        d = col.split('_')[1] # e.g. 'd0', 'd7'
        day_num = int(d[1:]) # 0, 7
        
        # paid
        paid_d = paid_df.copy()
        paid_d['rev'] = paid_d[col] * paid_d['total_cohort_users']
        paid_d_grouped = paid_d.groupby('install_date')['rev'].sum().reset_index()

        # all
        all_d = all_df.copy()
        all_d['rev'] = all_d[col] * all_d['total_cohort_users']
        all_d_grouped = all_d.groupby('install_date')['rev'].sum().reset_index()

        d_merge = pd.merge(result[['install_date', 'cost']], paid_d_grouped, on='install_date', how='left')
        d_merge = pd.merge(d_merge, all_d_grouped, on='install_date', how='left', suffixes=('_paid', '_all'))

        result[f'Campaign ROAS {d.upper()}'] = d_merge['rev_paid'] / d_merge['cost'].replace(0, pd.NA)
        result[f'Blended ROAS {d.upper()}'] = d_merge['rev_all'] / d_merge['cost'].replace(0, pd.NA)

        # Buffer rule: data must be fully mature.
        mature_date_end = max_date - pd.Timedelta(days=day_num + 2)
        result.loc[result['install_date'] > mature_date_end, [f'Campaign ROAS {d.upper()}', f'Blended ROAS {d.upper()}']] = np.nan

    # clean up temporary cost column
    if 'cost' in result.columns:
        result.drop(columns=['cost'], inplace=True)

    return result

def calculate_roas_d30_kpis_v2(df, ad_spend_raw_df=None, days=14, start_date=None, end_date=None):
    if df.empty or 'ltv_d30' not in df.columns or ad_spend_raw_df is None or ad_spend_raw_df.empty:
        return 0.0, 0.0, None, None
        
    df['install_date'] = pd.to_datetime(df['install_date'])
    ad_spend_raw_df['day'] = pd.to_datetime(ad_spend_raw_df['day'])

    if start_date is not None and end_date is not None:
        mature_date_start = pd.to_datetime(start_date)
        mature_date_end = pd.to_datetime(end_date)
    else:
        max_date = df['install_date'].max()
        mature_date_end = max_date - pd.Timedelta(days=39)
        mature_date_start = mature_date_end - pd.Timedelta(days=days - 1)
    
    mature_df = df[(df['install_date'] >= mature_date_start) & (df['install_date'] <= mature_date_end)]
    ad_spend_mature = ad_spend_raw_df[(ad_spend_raw_df['day'] >= mature_date_start) & (ad_spend_raw_df['day'] <= mature_date_end)]
    
    if mature_df.empty or ad_spend_mature.empty:
        return 0.0, 0.0, mature_date_start, mature_date_end

    total_cost = ad_spend_mature['cost'].sum()
    if total_cost <= 0:
        return 0.0, 0.0, mature_date_start, mature_date_end
    
    organic_sources = ['organic', '(organic)', 'google_organic_search']
    if 'media_source' in mature_df.columns:
        paid_df = mature_df[~mature_df['media_source'].isin(organic_sources)]
    else:
        paid_df = mature_df[mature_df['cohort_ad_spend'] > 0]
        
    campaign_revenue = (paid_df['ltv_d30'] * paid_df['total_cohort_users']).sum()
    campaign_roas = campaign_revenue / total_cost
        
    blended_revenue = (mature_df['ltv_d30'] * mature_df['total_cohort_users']).sum()
    blended_roas = blended_revenue / total_cost
        
    return campaign_roas, blended_roas, mature_date_start, mature_date_end

def calculate_roas_d7_kpis_v2(df, ad_spend_raw_df=None, days=7, start_date=None, end_date=None):
    if df.empty or 'ltv_d7' not in df.columns or ad_spend_raw_df is None or ad_spend_raw_df.empty:
        return 0.0, 0.0, None, None
        
    df['install_date'] = pd.to_datetime(df['install_date'])
    ad_spend_raw_df['day'] = pd.to_datetime(ad_spend_raw_df['day'])

    if start_date is not None and end_date is not None:
        mature_date_start = pd.to_datetime(start_date)
        mature_date_end = pd.to_datetime(end_date)
    else:
        max_date = df['install_date'].max()
        mature_date_end = max_date - pd.Timedelta(days=9)
        mature_date_start = mature_date_end - pd.Timedelta(days=days - 1)
    
    mature_df = df[(df['install_date'] >= mature_date_start) & (df['install_date'] <= mature_date_end)]
    ad_spend_mature = ad_spend_raw_df[(ad_spend_raw_df['day'] >= mature_date_start) & (ad_spend_raw_df['day'] <= mature_date_end)]
    
    if mature_df.empty or ad_spend_mature.empty:
        return 0.0, 0.0, mature_date_start, mature_date_end
        
    total_cost = ad_spend_mature['cost'].sum()
    if total_cost <= 0:
        return 0.0, 0.0, mature_date_start, mature_date_end

    organic_sources = ['organic', '(organic)', 'google_organic_search']
    if 'media_source' in mature_df.columns:
        paid_df = mature_df[~mature_df['media_source'].isin(organic_sources)]
    else:
        paid_df = mature_df[mature_df['cohort_ad_spend'] > 0]
        
    campaign_revenue = (paid_df['ltv_d7'] * paid_df['total_cohort_users']).sum()
    campaign_roas = campaign_revenue / total_cost
        
    blended_revenue = (mature_df['ltv_d7'] * mature_df['total_cohort_users']).sum()
    blended_roas = blended_revenue / total_cost
        
    return campaign_roas, blended_roas, mature_date_start, mature_date_end


def calculate_roas_d0_kpis_v2(df, ad_spend_raw_df=None, days=1, start_date=None, end_date=None):
    if df.empty or 'ltv_d0' not in df.columns or ad_spend_raw_df is None or ad_spend_raw_df.empty:
        return 0.0, 0.0, None, None
        
    df['install_date'] = pd.to_datetime(df['install_date'])
    ad_spend_raw_df['day'] = pd.to_datetime(ad_spend_raw_df['day'])

    if start_date is not None and end_date is not None:
        mature_date_start = pd.to_datetime(start_date)
        mature_date_end = pd.to_datetime(end_date)
    else:
        max_date = df['install_date'].max()
        mature_date_end = max_date - pd.Timedelta(days=2) # 2 days buffer for D0
        mature_date_start = mature_date_end - pd.Timedelta(days=days - 1)
    
    mature_df = df[(df['install_date'] >= mature_date_start) & (df['install_date'] <= mature_date_end)]
    ad_spend_mature = ad_spend_raw_df[(ad_spend_raw_df['day'] >= mature_date_start) & (ad_spend_raw_df['day'] <= mature_date_end)]
    
    if mature_df.empty or ad_spend_mature.empty:
        return 0.0, 0.0, mature_date_start, mature_date_end
        
    total_cost = ad_spend_mature['cost'].sum()
    if total_cost <= 0:
        return 0.0, 0.0, mature_date_start, mature_date_end

    organic_sources = ['organic', '(organic)', 'google_organic_search']
    if 'media_source' in mature_df.columns:
        paid_df = mature_df[~mature_df['media_source'].isin(organic_sources)]
    else:
        paid_df = mature_df[mature_df['cohort_ad_spend'] > 0]
        
    campaign_revenue = (paid_df['ltv_d0'] * paid_df['total_cohort_users']).sum()
    campaign_roas = campaign_revenue / total_cost
        
    blended_revenue = (mature_df['ltv_d0'] * mature_df['total_cohort_users']).sum()
    blended_roas = blended_revenue / total_cost
        
    return campaign_roas, blended_roas, mature_date_start, mature_date_end



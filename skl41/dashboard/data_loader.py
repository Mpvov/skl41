import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data(file_path):
    """Loads the main dataset and parses dates."""
    if not os.path.exists(file_path):
        st.error(f"Data file not found: {file_path}")
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df['event_date'] = pd.to_datetime(df['event_date'])
    return df

def filter_data(df, start_date, end_date, countries, platforms, ad_formats, ad_networks):
    """Filters the dataset based on global selections."""
    if df.empty:
        return df

    filtered_df = df.copy()
    
    # Date filter
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = filtered_df[(filtered_df['event_date'] >= start_date) & (filtered_df['event_date'] <= end_date)]
    
    # Country filter
    if countries:
        filtered_df = filtered_df[filtered_df['country_code'].isin(countries)]
        
    # Platform filter
    if platforms:
        filtered_df = filtered_df[filtered_df['platform'].isin(platforms)]
        
    # Ad format filter
    if ad_formats:
        filtered_df = filtered_df[filtered_df['ad_format'].isin(ad_formats)]
        
    # Ad network filter
    if ad_networks:
        filtered_df = filtered_df[filtered_df['ad_network'].isin(ad_networks)]
        
    return filtered_df


@st.cache_data
def load_retention_csv(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['install_date'] = pd.to_datetime(df['install_date'])
    numeric_cols = [
        'total_cohort_users', 'cohort_ad_spend',
        'retention_r1', 'retention_r3', 'retention_r7', 'retention_r14', 'retention_r30', 
        'sumR3', 'sumR7', 'sumR14', 'sumR30',
        'ltv_d0', 'ltv_d1', 'ltv_d3', 'ltv_d7', 'ltv_d14', 'ltv_d30',
        'roas_d0', 'roas_d1', 'roas_d3', 'roas_d7', 'roas_d14', 'roas_d30'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def filter_retention_csv(df, start_date, end_date, countries=None, media_sources=None, campaigns=None):
    if df.empty:
        return df
    filtered_df = df.copy()
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = filtered_df[(filtered_df['install_date'] >= start_date) & (filtered_df['install_date'] <= end_date)]
    
    if countries and 'country_code' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['country_code'].isin(countries)]
        
    if media_sources and 'media_source' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['media_source'].isin(media_sources)]
        
    if campaigns and 'campaign_name' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['campaign_name'].isin(campaigns)]
        
    return filtered_df

@st.cache_data
def load_roas_csv(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['install_date'] = pd.to_datetime(df['install_date'])
    numeric_cols = ['total_cohort_users', 'cohort_ad_spend', 'avg_cpi', 'ltv_d7', 'ltv_d30', 'roas_d7', 'roas_d30']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def filter_roas_csv(df, start_date, end_date, countries=None, media_sources=None, campaigns=None):
    return filter_retention_csv(df, start_date, end_date, countries, media_sources, campaigns)

@st.cache_data
def load_dau_csv(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['event_date'] = pd.to_datetime(df['event_date'])
    numeric_cols = ['total_dau', 'new_users', 'return_users']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def filter_dau_csv(df, start_date, end_date, countries=None, platforms=None, channels=None, campaigns=None):
    if df.empty:
        return df
    filtered_df = df.copy()
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = filtered_df[(filtered_df['event_date'] >= start_date) & (filtered_df['event_date'] <= end_date)]
    
    if countries and 'country_code' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['country_code'].isin(countries)]
        
    if platforms and 'platform' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['platform'].isin(platforms)]
        
    if channels and 'channel' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['channel'].isin(channels)]
        
    if campaigns and 'campaign_name' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['campaign_name'].isin(campaigns)]
        
    return filtered_df

@st.cache_data
def load_changelog_v2(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    df = pd.read_csv(file_path, sep='\t')
    df['Date live'] = pd.to_datetime(df['Date live'], format='%d/%m/%y')
    return df

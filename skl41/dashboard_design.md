# Streamlit Dashboard Design: Analytics KPIs

## Understanding Summary
- **What is being built:** A Streamlit dashboard to visualize DAU, Ad Impressions, and Ad Revenue, broken down by multiple dimensions.
- **Why it exists:** To track Monetization and Business scale, with a flexible architecture designed to easily add Retention, LTV, and ROAS later.
- **Who it is for:** Game analysts / product managers evaluating the game's performance.
- **Key constraints:** The dashboard will read from the local `dau_ad_imp_ad_rev_geo_channel.csv` file.
- **Explicit non-goals:** Not querying BigQuery directly for now. Not implementing LTV/Retention metrics until the required data (user logs) is added.

## Assumptions (Non-Functional Requirements)
- **Performance/Scale:** The CSV (~5MB) easily fits in memory. Streamlit caching (`@st.cache_data`) will be used to ensure fast load times and responsive filtering.
- **Security:** Running locally; no authentication required.
- **Maintenance:** Modular design is used so that swapping out data sources (e.g., switching to BigQuery) or adding complex metrics (like LTV cohorts) won't require rewriting the UI logic.

## Decision Log
1. **Data Source:** Decided to use the local CSV file `dau_ad_imp_ad_rev_geo_channel.csv` instead of connecting directly to BigQuery to simplify Phase 1.
2. **Architecture:** Chose a Layered Architecture (MVC-like) over a monolithic file or a multi-page app. This provides the best balance of maintainability and ease of sharing global filters across different KPI views.
3. **UI Layout:** Decided to use Streamlit Tabs for the three pillars (Monetization, Retention, Business) to keep all global sidebar filters unified and apply them to all views instantly.

## Final Design
The application uses a Layered Architecture with the following structure:

```text
dashboard/
├── data_loader.py    # Handles reading data and caching
├── metrics.py        # Logic for aggregating and calculating KPIs safely
├── app.py            # Streamlit entry point, sidebar, and tab layouts
└── requirements.txt  # Dependencies (pandas, streamlit, plotly)
```

**Data Layer (`data_loader.py`):**
- Features a `load_data()` function decorated with `@st.cache_data`.
- Parses dates and handles initial data types.
- Provides a `filter_data()` function to apply global filters once before passing to the UI/Metrics.

**Metrics Layer (`metrics.py`):**
- Contains isolated, testable functions for KPI calculations (e.g., `calculate_ecpm()`, `calculate_revenue()`).
- Prevents DAU overcounting when aggregating across dimensions like ad networks.

**Presentation Layer (`app.py`):**
- **Sidebar:** Contains global filters (Date Range, Country, Platform, Ad Format, Ad Network).
- **Tabs:**
  - **Monetization:** Displays scorecards and Plotly trend charts for Ad Revenue, eCPM, and Impressions (Interstitial vs. Rewarded).
  - **Business:** Displays DAU trends. Installs, ROAS, and Ad Spend are noted as "Phase 2".
  - **Retention:** Currently a placeholder, ready to be activated once the user cohort data is integrated.

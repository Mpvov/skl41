"""
Level-comparison chart functions for the dashboard.
Follows chart_design_spec.md to compare Build A vs Build B across levels.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


ROLLING_WINDOW = 5  # rolling average window for smoothing noisy high-level data
BUILD_A_COLOR = "#636EFA"  # blue
BUILD_B_COLOR = "#EF553B"  # red
POSITIVE_COLOR = "#00CC96"  # green (Build B better)
NEGATIVE_COLOR = "#EF553B"  # red (Build B worse)


def load_level_data(path_a, path_b, label_a="1.0.11", label_b="1.1.0"):
    """Load and tag two level CSVs, then merge on level."""
    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)
    df_a["build"] = label_a
    df_b["build"] = label_b
    return df_a, df_b


def _apply_rolling(series, window=ROLLING_WINDOW):
    """Apply centered rolling average, filling NaNs at edges."""
    return series.rolling(window, center=True, min_periods=1).mean()


# ──────────────────────────────────────────────
# SECTION 1: Funnel & Churn
# ──────────────────────────────────────────────

def chart_cumulative_funnel_rate(df_a, df_b, label_a, label_b, max_level=None):
    """1.1 Cumulative Funnel Rate – dual line chart."""
    a = df_a[["level", "funnel_rate"]].copy()
    b = df_b[["level", "funnel_rate"]].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=a["level"], y=a["funnel_rate"], name=label_a,
        mode="lines", line=dict(color=BUILD_A_COLOR, width=2),
        hovertemplate="Level %{x}<br>Funnel: %{y:.2%}<extra>" + label_a + "</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=b["level"], y=b["funnel_rate"], name=label_b,
        mode="lines", line=dict(color=BUILD_B_COLOR, width=2),
        hovertemplate="Level %{x}<br>Funnel: %{y:.2%}<extra>" + label_b + "</extra>",
    ))
    fig.update_layout(
        title="Cumulative Funnel Rate (% Players Surviving)",
        xaxis_title="Level", yaxis_title="Funnel Rate",
        yaxis_tickformat=".0%", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def chart_dropoff_delta(df_a, df_b, label_a, label_b, max_level=None):
    """1.2 Level-specific Drop-off Delta (Build B − Build A)."""
    merged = pd.merge(
        df_a[["level", "funnel_rate"]],
        df_b[["level", "funnel_rate"]],
        on="level", suffixes=("_a", "_b"), how="inner",
    )
    if max_level:
        merged = merged[merged["level"] <= max_level]

    # Drop-off at each level = 1 − (funnel[level] / funnel[level−1])
    merged["drop_a"] = 1 - merged["funnel_rate_a"] / merged["funnel_rate_a"].shift(1)
    merged["drop_b"] = 1 - merged["funnel_rate_b"] / merged["funnel_rate_b"].shift(1)
    merged["delta"] = merged["drop_b"] - merged["drop_a"]
    merged = merged.dropna()

    colors = [NEGATIVE_COLOR if d > 0 else POSITIVE_COLOR for d in merged["delta"]]
    fig = go.Figure(go.Bar(
        x=merged["level"], y=merged["delta"],
        marker_color=colors,
        hovertemplate="Level %{x}<br>Δ Drop-off: %{y:+.2%}<extra></extra>",
    ))
    fig.update_layout(
        title=f"Drop-off Delta ({label_b} − {label_a})",
        xaxis_title="Level", yaxis_title="Δ Drop-off Rate",
        yaxis_tickformat="+.1%",
        annotations=[dict(
            text=f"<span style='color:{NEGATIVE_COLOR}'>■</span> {label_b} loses more users  |  <span style='color:{POSITIVE_COLOR}'>■</span> {label_b} retains better",
            xref="paper", yref="paper", x=0.5, y=-0.12,
            showarrow=False, font=dict(size=11),
        )],
    )
    return fig


def chart_continue_rate(df_a, df_b, label_a, label_b, max_level=None):
    """1.3 Level Continue Rate Trend (with rolling avg)."""
    a = df_a[["level", "level_continue_rate"]].copy()
    b = df_b[["level", "level_continue_rate"]].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    a["smooth"] = _apply_rolling(a["level_continue_rate"])
    b["smooth"] = _apply_rolling(b["level_continue_rate"])

    fig = go.Figure()
    # Raw as faint
    fig.add_trace(go.Scatter(x=a["level"], y=a["level_continue_rate"], name=f"{label_a} (raw)", mode="lines",
                             line=dict(color=BUILD_A_COLOR, width=0.8), opacity=0.25, showlegend=False))
    fig.add_trace(go.Scatter(x=b["level"], y=b["level_continue_rate"], name=f"{label_b} (raw)", mode="lines",
                             line=dict(color=BUILD_B_COLOR, width=0.8), opacity=0.25, showlegend=False))
    # Smoothed
    fig.add_trace(go.Scatter(x=a["level"], y=a["smooth"], name=label_a, mode="lines",
                             line=dict(color=BUILD_A_COLOR, width=3)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["smooth"], name=label_b, mode="lines",
                             line=dict(color=BUILD_B_COLOR, width=3)))
    fig.update_layout(
        title="Level Continue Rate (Rolling Avg)",
        xaxis_title="Level", yaxis_title="Continue Rate",
        yaxis_tickformat=".0%", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


# ──────────────────────────────────────────────
# SECTION 2: Difficulty & Engagement
# ──────────────────────────────────────────────

def chart_first_attempt_win_rate_delta(df_a, df_b, label_a, label_b, max_level=None):
    """2.1 1st Attempt Win Rate Delta – diverging bar (Red/Green)."""
    merged = pd.merge(
        df_a[["level", "1st_attempts_win"]],
        df_b[["level", "1st_attempts_win"]],
        on="level", suffixes=("_a", "_b"), how="inner",
    )
    if max_level:
        merged = merged[merged["level"] <= max_level]
    merged["delta"] = merged["1st_attempts_win_b"] - merged["1st_attempts_win_a"]

    colors = [POSITIVE_COLOR if d >= 0 else NEGATIVE_COLOR for d in merged["delta"]]
    fig = go.Figure(go.Bar(
        x=merged["level"], y=merged["delta"], marker_color=colors,
        hovertemplate="Level %{x}<br>Δ 1st Win: %{y:+.2%}<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_layout(
        title=f"1st Attempt Win Rate Delta ({label_b} − {label_a})",
        xaxis_title="Level", yaxis_title="Δ 1st Attempt Win Rate",
        yaxis_tickformat="+.1%",
        annotations=[dict(
            text=f"<span style='color:{POSITIVE_COLOR}'>■</span> Easier in {label_b}  |  <span style='color:{NEGATIVE_COLOR}'>■</span> Harder in {label_b}",
            xref="paper", yref="paper", x=0.5, y=-0.12,
            showarrow=False, font=dict(size=11),
        )],
    )
    return fig


def chart_fail_rate_and_attempts(df_a, df_b, label_a, label_b, max_level=None):
    """2.2 Fail Rate & Avg Attempts – dual-axis line chart."""
    a = df_a[["level", "level_fail_rate", "avg_attempts"]].copy()
    b = df_b[["level", "level_fail_rate", "avg_attempts"]].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    a["fail_smooth"] = _apply_rolling(a["level_fail_rate"])
    b["fail_smooth"] = _apply_rolling(b["level_fail_rate"])
    a["att_smooth"] = _apply_rolling(a["avg_attempts"])
    b["att_smooth"] = _apply_rolling(b["avg_attempts"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Fail rate lines
    fig.add_trace(go.Scatter(x=a["level"], y=a["fail_smooth"], name=f"{label_a} Fail Rate",
                             line=dict(color=BUILD_A_COLOR, width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=b["level"], y=b["fail_smooth"], name=f"{label_b} Fail Rate",
                             line=dict(color=BUILD_B_COLOR, width=2)), secondary_y=False)
    # Attempts lines
    fig.add_trace(go.Scatter(x=a["level"], y=a["att_smooth"], name=f"{label_a} Avg Attempts",
                             line=dict(color=BUILD_A_COLOR, width=2, dash="dot")), secondary_y=True)
    fig.add_trace(go.Scatter(x=b["level"], y=b["att_smooth"], name=f"{label_b} Avg Attempts",
                             line=dict(color=BUILD_B_COLOR, width=2, dash="dot")), secondary_y=True)
    fig.update_layout(
        title="Fail Rate & Avg Attempts (Rolling Avg)",
        xaxis_title="Level", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_yaxes(title_text="Fail Rate", tickformat=".0%", secondary_y=False)
    fig.update_yaxes(title_text="Avg Attempts", secondary_y=True)
    return fig


def chart_avg_progress(df_a, df_b, label_a, label_b, max_level=None):
    """2.3 Average Progress upon Failure."""
    a = df_a[["level", "avg_progress"]].copy()
    b = df_b[["level", "avg_progress"]].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    # Convert to numeric, coerce errors
    a["avg_progress"] = pd.to_numeric(a["avg_progress"], errors="coerce")
    b["avg_progress"] = pd.to_numeric(b["avg_progress"], errors="coerce")
    a["smooth"] = _apply_rolling(a["avg_progress"])
    b["smooth"] = _apply_rolling(b["avg_progress"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a["level"], y=a["smooth"], name=label_a,
                             line=dict(color=BUILD_A_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["smooth"], name=label_b,
                             line=dict(color=BUILD_B_COLOR, width=2)))
    fig.update_layout(
        title="Avg Progress upon Failure (Rolling Avg)",
        xaxis_title="Level", yaxis_title="Avg Progress (%)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def chart_win_duration_ribbon(df_a, df_b, label_a, label_b, max_level=None):
    """2.4 Win Duration Spectrum – ribbon chart (p50-p90)."""
    cols = ["level", "win_duration_p50", "win_duration_p75", "win_duration_p90"]
    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    for c in cols[1:]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")

    fig = go.Figure()
    # Build A ribbon (p50-p90)
    fig.add_trace(go.Scatter(
        x=a["level"], y=a["win_duration_p90"], name=f"{label_a} p90",
        line=dict(width=0), showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=a["level"], y=a["win_duration_p50"], name=f"{label_a} (p50–p90)",
        fill="tonexty", fillcolor="rgba(99,110,250,0.15)",
        line=dict(color=BUILD_A_COLOR, width=2),
    ))
    # Build B ribbon
    fig.add_trace(go.Scatter(
        x=b["level"], y=b["win_duration_p90"], name=f"{label_b} p90",
        line=dict(width=0), showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=b["level"], y=b["win_duration_p50"], name=f"{label_b} (p50–p90)",
        fill="tonexty", fillcolor="rgba(239,85,59,0.15)",
        line=dict(color=BUILD_B_COLOR, width=2),
    ))
    fig.update_layout(
        title="Win Duration Spectrum (p50 – p90)",
        xaxis_title="Level", yaxis_title="Duration (seconds)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


# ──────────────────────────────────────────────
# SECTION 3: Monetization & Resource Economy
# ──────────────────────────────────────────────

def chart_avg_imp_per_user(df_a, df_b, label_a, label_b, max_level=None):
    """Basic Monetization: Avg IS & RW Impressions per User at Level."""
    cols = ["level", "playing_user", "rw_imp", "is_imp"]
    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
        
    for df in [a, b]:
        df["playing_user"] = pd.to_numeric(df["playing_user"], errors="coerce")
        df["rw_imp"] = pd.to_numeric(df["rw_imp"], errors="coerce")
        df["is_imp"] = pd.to_numeric(df["is_imp"], errors="coerce")
        df["avg_rw_imp"] = df["rw_imp"] / df["playing_user"].replace(0, np.nan)
        df["avg_is_imp"] = df["is_imp"] / df["playing_user"].replace(0, np.nan)
        df["avg_rw_smooth"] = _apply_rolling(df["avg_rw_imp"])
        df["avg_is_smooth"] = _apply_rolling(df["avg_is_imp"])

    fig = go.Figure()
    # RW
    fig.add_trace(go.Scatter(x=a["level"], y=a["avg_rw_smooth"], name=f"{label_a} RW",
                             line=dict(color=BUILD_A_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["avg_rw_smooth"], name=f"{label_b} RW",
                             line=dict(color=BUILD_B_COLOR, width=2)))
    # IS
    fig.add_trace(go.Scatter(x=a["level"], y=a["avg_is_smooth"], name=f"{label_a} IS",
                             line=dict(color=BUILD_A_COLOR, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=b["level"], y=b["avg_is_smooth"], name=f"{label_b} IS",
                             line=dict(color=BUILD_B_COLOR, width=2, dash="dash")))
                             
    fig.update_layout(
        title="Avg Impressions per User at Level (RW & IS)",
        xaxis_title="Level", yaxis_title="Avg Impressions / User",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def chart_ad_revenue_per_user(df_a, df_b, label_a, label_b, max_level=None):
    """Basic Monetization: Avg Ad Revenue per User at Level."""
    cols = ["level", "playing_user", "ad_revenue"]
    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
        
    for df in [a, b]:
        df["playing_user"] = pd.to_numeric(df["playing_user"], errors="coerce")
        df["ad_revenue"] = pd.to_numeric(df["ad_revenue"], errors="coerce")
        df["avg_ad_rev"] = df["ad_revenue"] / df["playing_user"].replace(0, np.nan)
        df["avg_ad_rev_smooth"] = _apply_rolling(df["avg_ad_rev"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a["level"], y=a["avg_ad_rev_smooth"], name=label_a,
                             line=dict(color=BUILD_A_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["avg_ad_rev_smooth"], name=label_b,
                             line=dict(color=BUILD_B_COLOR, width=2)))
                             
    fig.update_layout(
        title="Avg Ad Revenue per User at Level",
        xaxis_title="Level", yaxis_title="Avg Ad Revenue ($)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig

def chart_arpu_curve(df_a, df_b, label_a, label_b, max_level=None):
    """3.1 ARPU & Ad ARPU Curve."""
    cols = ["level", "arpu", "ad_arpu"]
    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    for c in cols[1:]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
    a["arpu_smooth"] = _apply_rolling(a["arpu"])
    b["arpu_smooth"] = _apply_rolling(b["arpu"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a["level"], y=a["arpu_smooth"], name=f"{label_a} ARPU",
                             line=dict(color=BUILD_A_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["arpu_smooth"], name=f"{label_b} ARPU",
                             line=dict(color=BUILD_B_COLOR, width=2)))
    fig.update_layout(
        title="ARPU Curve by Level (Rolling Avg)",
        xaxis_title="Level", yaxis_title="ARPU ($)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def chart_cumulative_impressions(df_a, df_b, label_a, label_b, max_level=None):
    """3.2 Cumulative Avg Impressions (RW & IS)."""
    cols = ["level", "cum_avg_rw_imp", "cum_avg_is_imp"]
    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    for c in cols[1:]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")

    fig = go.Figure()
    # RW
    fig.add_trace(go.Scatter(x=a["level"], y=a["cum_avg_rw_imp"], name=f"{label_a} RW",
                             line=dict(color=BUILD_A_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["cum_avg_rw_imp"], name=f"{label_b} RW",
                             line=dict(color=BUILD_B_COLOR, width=2)))
    # IS
    fig.add_trace(go.Scatter(x=a["level"], y=a["cum_avg_is_imp"], name=f"{label_a} IS",
                             line=dict(color=BUILD_A_COLOR, width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=b["level"], y=b["cum_avg_is_imp"], name=f"{label_b} IS",
                             line=dict(color=BUILD_B_COLOR, width=2, dash="dash")))
    fig.update_layout(
        title="Cumulative Avg Impressions (RW & IS)",
        xaxis_title="Level", yaxis_title="Cumulative Avg Impressions",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def chart_resource_source_sink(df_a, df_b, label_a, label_b, resource="hint", max_level=None):
    """3.3 Resource Source vs Sink Balance – overlapping area chart."""
    src_col = f"avg_res_src_{resource}"
    sink_col = f"avg_res_sink_{resource}"
    cols = ["level", src_col, sink_col]

    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    for c in cols[1:]:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")

    fig = make_subplots(rows=1, cols=2, subplot_titles=[label_a, label_b], shared_yaxes=True)
    # Build A
    fig.add_trace(go.Scatter(x=a["level"], y=a[src_col], name="Source", fill="tozeroy",
                             fillcolor="rgba(0,204,150,0.3)", line=dict(color=POSITIVE_COLOR)),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=a["level"], y=a[sink_col], name="Sink", fill="tozeroy",
                             fillcolor="rgba(239,85,59,0.3)", line=dict(color=NEGATIVE_COLOR)),
                  row=1, col=1)
    # Build B
    fig.add_trace(go.Scatter(x=b["level"], y=b[src_col], name="Source", fill="tozeroy",
                             fillcolor="rgba(0,204,150,0.3)", line=dict(color=POSITIVE_COLOR), showlegend=False),
                  row=1, col=2)
    fig.add_trace(go.Scatter(x=b["level"], y=b[sink_col], name="Sink", fill="tozeroy",
                             fillcolor="rgba(239,85,59,0.3)", line=dict(color=NEGATIVE_COLOR), showlegend=False),
                  row=1, col=2)
    fig.update_layout(
        title=f"Resource Balance: {resource.title()} (Source vs Sink)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05),
    )
    fig.update_xaxes(title_text="Level")
    fig.update_yaxes(title_text="Avg per User", col=1)
    return fig


def chart_t1_t2_ad_mix(df_a, df_b, label_a, label_b, max_level=None):
    """3.4 T1 vs T2 Ad Quality Mix – 100% stacked bar chart."""
    cols = ["level", "t1_rw_user", "t2_rw_user", "t1_is_user", "t2_is_user"]
    a = df_a[cols].copy()
    b = df_b[cols].copy()
    if max_level:
        a = a[a["level"] <= max_level]
        b = b[b["level"] <= max_level]
    for c in cols[1:]:
        a[c] = pd.to_numeric(a[c], errors="coerce").fillna(0)
        b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)

    # Compute total RW users and percentages
    a["total_rw"] = a["t1_rw_user"] + a["t2_rw_user"]
    a["t1_rw_pct"] = a["t1_rw_user"] / a["total_rw"].replace(0, np.nan)
    b["total_rw"] = b["t1_rw_user"] + b["t2_rw_user"]
    b["t1_rw_pct"] = b["t1_rw_user"] / b["total_rw"].replace(0, np.nan)

    # Smooth
    a["t1_smooth"] = _apply_rolling(a["t1_rw_pct"], window=10)
    b["t1_smooth"] = _apply_rolling(b["t1_rw_pct"], window=10)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a["level"], y=a["t1_smooth"], name=f"{label_a} T1%",
                             line=dict(color=BUILD_A_COLOR, width=2)))
    fig.add_trace(go.Scatter(x=b["level"], y=b["t1_smooth"], name=f"{label_b} T1%",
                             line=dict(color=BUILD_B_COLOR, width=2)))
    fig.add_hline(y=0.5, line_dash="dot", line_color="gray", annotation_text="50%")
    fig.update_layout(
        title="RW Ad Quality: T1 User Ratio (Rolling Avg)",
        xaxis_title="Level", yaxis_title="T1 User %",
        yaxis_tickformat=".0%",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig

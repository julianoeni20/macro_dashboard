from data import get_us_yield
import plotly.express as px
import plotly.graph_objects as go

def us_treasury_plots():
    import pandas as pd
    # Fetch data
    df = get_us_yield(360)
    
    # --- CHART 1: Time Series ---
    fig_ts = px.line(df, x=df.index, y=df.columns,
                title="US Treasury Yields: Time Series",
                labels={"value": "Yield(%)", "index": "Date"},
                template='plotly_dark')

    # --- CHART 2: Yield Curve Evolution ---
    tenor_map = {
        "US1M": 1/12,
        "US3M": 0.25, "US1Y": 1.0, "US2Y": 2.0, 
        "US5Y": 5.0, "US10Y": 10.0, "US20Y": 20.0
    }

    # Use iloc safely (ensure df has enough rows)
    latest = df.iloc[-1]
    week_ago = df.iloc[-5] if len(df) > 5 else df.iloc[0]
    month_ago = df.iloc[-25] if len(df) > 25 else df.iloc[0]
    year_ago = df.iloc[-255] if len(df) > 255 else df.iloc[0]

    curve_data = pd.DataFrame({
        'Maturity': df.columns,
        'Latest': latest.values,
        '1 Week Ago': week_ago.values,
        '1 Month Ago': month_ago.values,
        '1 Year Ago': year_ago.values
    })
    
    curve_melted = curve_data.melt(id_vars='Maturity', var_name='Timeline', value_name='Yield')
    curve_melted['Years'] = curve_melted['Maturity'].map(tenor_map)

    fig_curve = px.line(curve_melted, 
                x='Years', y='Yield', color='Timeline', 
                markers=True,
                title="US Yield Curve Evolution (Latest vs 1W vs 1M vs 1Y)",
                template="plotly_dark",
                hover_data={'Maturity': True, 'Years': False})
    
    fig_curve.update_layout(
        xaxis = dict(
            tickmode = 'array',
            tickvals = list(tenor_map.values()),
            ticktext = list(tenor_map.keys())
        )
    )

    # Return both figures as a tuple
    return fig_ts, fig_curve

def credit_spread_plots(df):
    """
    Plots US Corporate Credit Spreads (OAS) in Basis Points (bps) with dual Y-axes.
    """
    if df.empty:
        return go.Figure()

    # Create a local copy and convert to Basis Points (x 100)
    # We use .copy() to avoid modifying the cached dataframe in memory
    df_bps = df.copy() * 100

    fig = go.Figure()

    # Define colors
    colors = {
        "High Yield (Junk)": "#d62728",     # Red
        "BBB Corp (Inv. Grade)": "#ff7f0e", # Orange
        "AAA Corp (Prime)": "#2ca02c"       # Green
    }

    for column in df_bps.columns:
        # Assign traces to different Y-axes
        if column == "High Yield (Junk)":
            yaxis_assignment = "y1" # Primary Y-axis (Left)
        else:
            yaxis_assignment = "y2" # Secondary Y-axis (Right)

        fig.add_trace(go.Scatter(
            x=df_bps.index,
            y=df_bps[column],
            mode='lines',
            name=column,
            line=dict(width=2, color=colors.get(column, "blue")),
            yaxis=yaxis_assignment
        ))

    # Update layout with BPS titles
    fig.update_layout(
        title="US Corporate Credit Spreads (OAS)",
        xaxis_title="Date",
        
        # Left Axis (High Yield)
        yaxis=dict(
            title="High Yield Spread (bps)", # <--- Changed to bps
        ),
        
        # Right Axis (IG / Prime)
        yaxis2=dict(
            title="Inv. Grade / Prime Spread (bps)", # <--- Changed to bps
            overlaying="y",
            side="right"
        ),
        
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=500
    )
    
    return fig
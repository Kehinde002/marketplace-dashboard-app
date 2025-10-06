# -*- coding: utf-8 -*-
# Save this entire block as marketplace_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- Configuration and Setup ---
st.set_page_config(layout="wide", page_title="Marketplace Search Model")

# 1. Define the directory path where your CSV is saved
# This code uses Python's os module to guarantee the path is built correctly 
# relative to the script's location, bypassing environment path confusion.
BASE_DIR = os.path.dirname(__file__) 
FILE_PATH = os.path.join(BASE_DIR, 'marketplace_dashboard_data.csv')

# --- Data Loading (Phase 1/2) ---
# Use the Streamlit cache to load data efficiently
@st.cache_data
def load_data(path):
    # Check if the file exists before loading
    if not os.path.exists(path):
        st.error(f"Error: Data file not found at {os.path.abspath(path)}")
        return pd.DataFrame() # Return empty if missing
        
    df = pd.read_csv(path)
    # Ensure the month column is in datetime format for plotting
    df['published_month'] = pd.to_datetime(df['published_month'])
    return df

my_dashboard_data = load_data(FILE_PATH)

if my_dashboard_data.empty:
    st.stop() # Stop the app if data failed to load

# Calculate KPIs once
TOTAL_PROJECTS = my_dashboard_data['job_count'].sum()
TOTAL_CLIENT_COUNTRIES = my_dashboard_data['country'].nunique()
AVG_FEE_PER_JOB = my_dashboard_data['simulated_platform_fee'].median()
MEDIAN_FRICTION = my_dashboard_data['price_gap_abs'].median()

# --- Page Title and Introduction ---
st.title("🚀 Freelance Marketplace Dynamics: A Search Model Analysis")
st.markdown("---")

st.markdown("""
    *Analysis inspired by economic search theory (DMP model) to quantify market **Friction** and guide platform strategy.*
""")

# --- 2. Section 1: Overview KPIs ---
st.header("1. Overview & Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Projects Posted (Demand $\Lambda$)", f"{TOTAL_PROJECTS:,.0f}")
with col2:
    st.metric("Total Client Countries", f"{TOTAL_CLIENT_COUNTRIES:,.0f}")
with col3:
    st.metric("Median Fee per Match ($\Pi_p$)", f"${AVG_FEE_PER_JOB:,.2f}")
with col4:
    st.metric("Median Price Gap (Friction)", f"${MEDIAN_FRICTION:,.2f}")

st.markdown("---")

# --- 3. Section 2: Market Dynamics (Visual 1 & 4) ---
st.header("2. Market Dynamics: Demand Flow vs. Revenue (Volatility)")
st.markdown("Revenue is highly dependent on Demand Flow, leading to extreme volatility.")

# Aggregate for time series plotting
time_series_data = my_dashboard_data.groupby('published_month', as_index=False).agg(
    {'job_count': 'sum', 'simulated_platform_fee': 'sum'}
)

# Create dual-axis plot for better comparison
fig_time = px.line(
    time_series_data, 
    x='published_month', 
    y=['job_count', 'simulated_platform_fee'],
    title='Demand Flow (Jobs) and Platform Revenue ($\Pi_p$) Over Time',
    labels={'value': 'Value', 'published_month': 'Month', 'variable': 'Metric'},
    template='plotly_white'
)
fig_time.update_traces(hovertemplate='Month: %{x}<br>Value: %{y:,.0f}<extra></extra>')

# Add a note about the correlation
fig_time.add_annotation(
    x=time_series_data['published_month'].iloc[-1], y=time_series_data['job_count'].max() * 0.9,
    text="Sharp post-peak drop in both metrics indicates high friction is causing churn.",
    showarrow=True, arrowhead=1, ax=0, ay=-40
)

st.plotly_chart(fig_time, use_container_width=True)


# --- 4. Section 3: Matching Efficiency (Visual 2 & 3) ---
st.header("3. Matching Efficiency: Finding the Low-Friction Equilibrium")
st.markdown("The key to matching speed is aligning client budget with the market’s expected rate.")

col_scatter, col_box = st.columns([2, 1])

# Scatter Plot (Visual 2)
with col_scatter:
    st.subheader("Client Budget vs. Price Gap (Friction V-Shape)")
    
    # Sample a smaller number of points for clarity
    plot_data_sample = my_dashboard_data.sample(n=10000, random_state=42)
    
    fig_scatter = px.scatter(
        plot_data_sample,
        x='client_budget_usd',
        y='price_gap_abs',
        color='budget_category',
        log_x=True, log_y=True,
        labels={'client_budget_usd': 'Client Budget (Log)', 'price_gap_abs': '|Budget - Market Rate| (Friction, Log)'},
        template='plotly_white'
    )
    # Highlight the equilibrium zone (where friction is lowest)
    fig_scatter.add_vline(x=500, line_dash="dash", line_color="red", annotation_text="~ $500 Equilibrium Zone")
    fig_scatter.update_traces(marker=dict(size=4, opacity=0.7))
    st.plotly_chart(fig_scatter, use_container_width=True)

# Box Plot (Visual 3)
with col_box:
    st.subheader("Friction Volatility by Segment")
    
    fig_box = px.box(
        my_dashboard_data,
        x='budget_category',
        y='price_gap_abs',
        color='budget_category',
        log_y=True, 
        labels={'price_gap_abs': 'Friction (Log)', 'budget_category': 'Segment'},
        template='plotly_white'
    )
    fig_box.update_xaxes(categoryorder='array', categoryarray=['Low Budget', 'Mid Budget', 'High Budget', 'Premium Budget'])
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("""
    **Insight:** The V-shape shows **friction is lowest near the $500 equilibrium**. The **Premium Budget** segment exhibits the highest friction volatility (the largest box range), requiring specialized matching resources.

""")





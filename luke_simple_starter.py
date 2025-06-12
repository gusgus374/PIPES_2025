"""
Money Makes the Ball Go Round - Starter
=======================================

This is your starter file, Luke! Follow the TODOs to complete your MLS salary analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from itscalledsoccer.client import AmericanSoccerAnalysis
from sklearn.linear_model import LinearRegression

st.title("Money Makes the Ball Go Round")

# --- TODO 1: Load Data ---
# Use the ASA API to get salary, player, and goals data for MLS
# salary_df = ...
# players_df = ...
# goals_df = ...

# --- TODO 2: Merge Data ---
# Merge the dataframes on player_id, keep relevant columns, calculate age
# merged = ...

# --- TODO 3: Scatter Plot (Goals vs Salary) ---
# Make a scatter plot of goals vs salary, add a regression line
# fig1 = ...
# st.plotly_chart(fig1)

# --- TODO 4: Bar Graph (Salary vs Age) ---
# Make a bar graph of average salary by age
# fig2 = ...
# st.plotly_chart(fig2)

# --- TODO 5: Write a short summary of your findings below ---
# st.write("...")
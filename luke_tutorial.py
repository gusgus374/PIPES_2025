"""
Money Makes the Ball Go Round
============================

Welcome Luke! Today, you'll explore how money and performance are connected in Major League Soccer (MLS).
We'll use real salary and performance data from the American Soccer Analysis API to answer:

- Do higher-paid players score more goals?
- How does salary relate to player age?

Let's get started!
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from itscalledsoccer.client import AmericanSoccerAnalysis
from sklearn.linear_model import LinearRegression

st.title("Money Makes the Ball Go Round")
st.header("MLS Player Value: Salary vs. Performance")

# --- Step 1: Load Data ---
st.subheader("Step 1: Load MLS Salary and Performance Data")
st.write("We'll use the American Soccer Analysis API to get player salary and goals data for the most recent MLS season.")

with st.echo():
    asa = AmericanSoccerAnalysis()
    # Get salary data (latest available season)
    salary_df = asa.get_player_salaries(leagues="mls")
    # Get player stats (goals, age, etc.)
    players_df = asa.get_players(leagues="mls")
    goals_df = asa.get_player_xgoals(leagues="mls")
    teams_df = asa.get_teams(leagues="mls")
    st.write("salary_df columns:", salary_df.columns.tolist())
    st.write("players_df columns:", players_df.columns.tolist())
    st.write("goals_df columns:", goals_df.columns.tolist())
    st.write("teams_df columns:", teams_df.columns.tolist())
    st.write("salary_df dtypes:", salary_df.dtypes)
    st.write("players_df dtypes:", players_df.dtypes)
    st.write("goals_df dtypes:", goals_df.dtypes)
    st.write("teams_df dtypes:", teams_df.dtypes)

# --- Step 2: Merge Data ---
st.subheader("Step 2: Merge Salary and Goals Data")
st.write("We'll merge the salary, player info, and goals data into one DataFrame.")

with st.echo():
    # Merge salary and player info on player_id
    merged = pd.merge(salary_df, players_df, on="player_id", suffixes=("_salary", "_info"))
    # Merge with goals data
    merged = pd.merge(merged, goals_df, on=["player_id", "team_id"])  # merge on both player_id and team_id for accuracy
    # Map team_id to team_name
    team_id_to_name = dict(zip(teams_df['team_id'], teams_df['team_name']))
    merged['team_name'] = merged['team_id'].map(team_id_to_name)
    # Clean up: keep only relevant columns
    merged = merged[["player_name", "team_name", "base_salary", "guaranteed_compensation", "birth_date", "xgoals", "goals"]]
    # Calculate age
    merged["birth_date"] = pd.to_datetime(merged["birth_date"], errors="coerce")
    merged["age"] = (pd.Timestamp("today") - merged["birth_date"]).dt.days // 365
    # Drop rows with missing salary or goals
    merged = merged.dropna(subset=["base_salary", "goals", "age"])

    st.write(merged.head())

# --- Step 3: Visual 1 - Goals vs Salary ---
st.subheader("Step 3: Do Higher-Paid Players Score More Goals?")
st.write("Let's plot goals vs. salary and fit a regression line.")

with st.echo():
    # Scatter plot with regression line
    X = merged[["base_salary"]].values
    y = merged["goals"].values
    reg = LinearRegression().fit(X, y)
    merged["predicted_goals"] = reg.predict(X)

    fig1 = px.scatter(merged, x="base_salary", y="goals", hover_name="player_name",
                     title="MLS: Goals vs. Salary",
                     labels={"base_salary": "Base Salary ($)", "goals": "Goals"})
    fig1.add_traces(px.line(merged, x="base_salary", y="predicted_goals").data)
    st.plotly_chart(fig1, use_container_width=True)
    st.write(f"Regression slope: {reg.coef_[0]:.4f} goals per $1 salary")

# --- Step 4: Visual 2 - Salary vs Age ---
st.subheader("Step 4: How Does Salary Vary by Age?")
st.write("Now let's see how salary changes with player age.")

with st.echo():
    # Bar graph: average salary by age
    age_salary = merged.groupby("age")["base_salary"].mean().reset_index()
    fig2 = px.bar(age_salary, x="age", y="base_salary",
                 title="MLS: Average Salary by Age",
                 labels={"base_salary": "Average Base Salary ($)", "age": "Age"})
    st.plotly_chart(fig2, use_container_width=True)

# --- Step 5: Summary ---
st.subheader("Summary & Discussion")
st.write("""
- We used real MLS salary and performance data.
- We found a (weak/strong?) relationship between salary and goals.
- Salary tends to (increase/decrease) with age, but there are exceptions.
- Remember: Salary isn't just about goals! Experience, position, and marketability matter too.
""")

st.info("Try changing the code to look at other stats, or compare different leagues!")

# End of tutorial

# References:
# - https://app.americansocceranalysis.com/api/v1/__docs__/#/Major%20League%20Soccer%20(MLS)/get_mls_players_salaries
# - https://american-soccer-analysis.github.io/itscalledsoccer/reference/
# - 2_US_Pro_Soccer.py (provided by instructor)
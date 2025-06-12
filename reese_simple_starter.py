"""
🏆 Reese's Soccer Data Science Project
=====================================

Copy this code into your reese.py file and complete the TODOs!
This will help you answer: "Which teams scored the most goals in the 2023 Women's World Cup?"
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from mplsoccer import Sbopen

# TODO 1: Add your title and introduction
st.title("🏆 Reese's 2023 Women's World Cup Analysis")
st.write("Hi! I'm analyzing which teams scored the most goals!")

# TODO 2: Load the data (this function is provided for you)
@st.cache_data
def load_match_data(competition_id, season_id):
    """Load match data from StatsBomb API"""
    parser = Sbopen()
    return parser.match(competition_id=competition_id, season_id=season_id)

@st.cache_data
def load_event_data(match_id):
    """Load event data for a specific match"""
    parser = Sbopen()
    return parser.event(match_id)[0]

# Set up tournament data
competition_id = 72    # Women's World Cup
season_id = 107        # 2023 tournament

# Load matches
st.write("Loading tournament data...")
df_matches = load_match_data(competition_id, season_id)
st.success(f"Loaded {len(df_matches)} matches!")

# TODO 3: Get all shooting data from the tournament
@st.cache_data
def get_shooting_data(df_matches):
    """Get all shots and goals from the tournament"""
    match_ids = df_matches["match_id"].tolist()
    all_shots = []

    progress = st.progress(0)
    for i, match_id in enumerate(match_ids):
        try:
            # Load events for this match
            events = load_event_data(match_id)

            # Filter for shots only
            shots = events[events['type_name'] == 'Shot'].copy()

            if not shots.empty:
                # Add goal information
                shots['is_goal'] = shots['outcome_name'] == 'Goal'

                # Keep only the columns we need (check if they exist)
                required_cols = ['player_name', 'team_name', 'is_goal']
                available_cols = [col for col in required_cols if col in shots.columns]
                if available_cols:  # Only add if we have the required columns
                    all_shots.append(shots[available_cols])

            progress.progress((i + 1) / len(match_ids))
        except:
            continue

    progress.empty()

    if all_shots:
        return pd.concat(all_shots, ignore_index=True)
    return pd.DataFrame()

# Get the shooting data
shooting_data = get_shooting_data(df_matches)
st.write(f"Found {len(shooting_data)} total shots in the tournament!")

# TODO 4: Group by player to get individual stats
st.subheader("Step 1: Player Statistics")

# Group by player name and calculate stats
player_stats = shooting_data.groupby('player_name').agg({
    'is_goal': ['sum', 'count'],  # Total goals (sum) AND total shots (count)
    'team_name': 'first'          # Get team name
}).reset_index()

# Flatten column names and rename to be clearer
player_stats.columns = ['player_name', 'goals', 'shots', 'team_name']

# TODO 5: Show top goalscorers
st.write("Top 10 goalscorers:")
top_scorers = player_stats.sort_values('goals', ascending=False).head(10)
st.dataframe(top_scorers)

# TODO 6: Group by team to answer our main question!
st.subheader("Step 2: Team Statistics - Our Main Answer!")

# Group by team and sum up goals and shots
team_stats = player_stats.groupby('team_name').agg({
    'goals': 'sum',          # Total team goals
    'shots': 'sum',          # Total team shots
    'player_name': 'count'   # Number of players who shot
}).reset_index()

# Rename columns
team_stats.columns = ['team_name', 'total_goals', 'total_shots', 'players_who_shot']

# Calculate shooting percentage
team_stats['shooting_percentage'] = (team_stats['total_goals'] / team_stats['total_shots']) * 100

# Sort by goals (highest first)
team_stats = team_stats.sort_values('total_goals', ascending=False)

# TODO 7: Show your results!
st.subheader("🥇 ANSWER: Teams Ranked by Goals!")
st.dataframe(team_stats)

# TODO 8: Try pandas functions
st.subheader("Step 3: Exploring with Pandas Functions")

# Use pandas functions to explore the data
most_goals = team_stats['total_goals'].max()
fewest_goals = team_stats['total_goals'].min()
avg_goals = team_stats['total_goals'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Most Goals by a Team", most_goals)
with col2:
    st.metric("Fewest Goals", fewest_goals)
with col3:
    st.metric("Average Goals per Team", f"{avg_goals:.1f}")

# TODO 9: Create a visualization
st.subheader("Step 4: Visualization")

# Bar chart of top teams
fig = px.bar(
    team_stats.head(10),  # Top 10 teams
    x='team_name',
    y='total_goals',
    title='Top 10 Teams by Goals Scored - 2023 Women\'s World Cup',
    labels={'total_goals': 'Goals Scored', 'team_name': 'Team'},
    color='total_goals',
    color_continuous_scale='viridis'
)
fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# TODO 10: Add your conclusions
st.subheader("My Findings")
st.write("""
Based on my analysis of the 2023 Women's World Cup:

**Key Findings:**
- [TODO: Fill in which team scored the most goals]
- [TODO: Fill in an interesting pattern you noticed]
- [TODO: Add one more insight]

**What I learned:**
- How to load soccer data using Python
- How to group data by players and teams
- How to use pandas functions like .sum(), .max(), .mean()
- How to create visualizations to tell a story with data!
""")

# Add a fun personal touch
if st.button("🎉 I'm a Data Scientist!"):
    st.balloons()
    st.write("You analyzed real professional soccer data just like the pros!")

st.write("---")
st.write("*Analysis by Reese using StatsBomb data*")
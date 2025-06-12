import streamlit as st
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Sbopen
import plotly.express as px
import altair as alt

st.title("Hi, my name is Reese! I would like to tell you a few things about me.")

from streamlit_extras.let_it_rain import rain

if st.button("Click here to see a hobby of mine!"):
    st.toast(":open_book:")

if st.button("Here's some of my favorite books..."):
    st.write("Jane Eyre, Pride and Prejudice, Hatchet, All Creatures Great and Small, and All the Light We Cannot See")

favorite_book = "Jane Eyre"

user_answer = st.text_input("Try and Guess My Favorite Book!")

st.write(f"You got it right, it's :blue[{user_answer}]!")

if user_answer == favorite_book:
    st.balloons()


st.button("I just won a million dollars!")

st.title("🏆 Reese's 2023 Women's World Cup Analysis")
st.header("Which team is the best at scoring goals?")

# Cache the data loading functions (same as in statsbomb.py)
@st.cache_data
def load_match_data(competition_id, season_id):
    """Load match data from StatsBomb API with caching for performance."""
    try:
        parser = Sbopen()
        return parser.match(competition_id=competition_id, season_id=season_id)
    except Exception as e:
        st.error(f"Error loading match data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_event_data(match_id):
    """Load event data for a specific match with caching."""
    try:
        parser = Sbopen()
        return parser.event(match_id)[0]
    except Exception as e:
        st.error(f"Error loading event data for match {match_id}: {e}")
        return pd.DataFrame()

# Set our tournament
competition_id = 72    # Women's World Cup
season_id = 107        # 2023 tournament

# Load the match data
st.write("Loading 2023 Women's World Cup matches...")
df_matches = load_match_data(competition_id, season_id)

if not df_matches.empty:
    st.success(f"✅ Successfully loaded {len(df_matches)} matches!")


@st.cache_data
def get_all_tournament_data(df_matches):
    """Get all player shooting data from the tournament."""
    match_ids = df_matches["match_id"].tolist()
    all_shooting_data = []

    progress_bar = st.progress(0)
    st.write(f"Loading detailed data from {len(match_ids)} matches...")

    for i, match_id in enumerate(match_ids):
        try:
            # Load event data for this match
            df_events = load_event_data(match_id)

            if not df_events.empty:
                # Filter for shots only (we want to analyze shooting!)
                shots = df_events[df_events['type_name'] == 'Shot'].copy()

                if not shots.empty:
                    # Add useful columns for our analysis
                    shots['is_goal'] = shots['outcome_name'] == 'Goal'
                    shots['match_id'] = match_id

                    # Keep only the columns we need (check if they exist first)
                    columns_to_keep = [
                        'match_id', 'player_name', 'player_id', 'team_name',
                        'shot_statsbomb_xg', 'is_goal', 'x', 'y'
                    ]

                    # Only keep columns that actually exist in the data
                    available_columns = [col for col in columns_to_keep if col in shots.columns]
                    shots_clean = shots[available_columns]

                    all_shooting_data.append(shots_clean)

            # Update progress
            progress_bar.progress((i + 1) / len(match_ids))

        except Exception as e:
            st.write(f"Could not load match {match_id}: {e}")
            continue

    progress_bar.empty()

    if all_shooting_data:
        return pd.concat(all_shooting_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Load all the shooting data
if not df_matches.empty:
    with st.spinner("Loading all shooting data from the tournament..."):
        df_all_shots = get_all_tournament_data(df_matches)

    if not df_all_shots.empty:
        st.success(f"✅ Found {len(df_all_shots)} total shots in the tournament!")



if not df_all_shots.empty:

    # Calculate these values
    total_shots = len(df_all_shots)
    total_goals = df_all_shots['is_goal'].sum()
    if 'shot_statsbomb_xg' in df_all_shots.columns:
        avg_xg = df_all_shots['shot_statsbomb_xg'].mean()
    else:
        avg_xg = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Shots", total_shots)
    with col2:
        st.metric("Total Goals", total_goals)
    with col3:
        st.metric("Avg xG per Shot", f"{avg_xg:.3f}")

# Step 7: Grouping by player
st.subheader("📊 Grouping Data by Player")

if not df_all_shots.empty:
    st.write("""
    Now let's group our data by player to see individual statistics!
    This is like making a pivot table in Excel.
    """)

    st.code("""
    # Group by player and calculate their stats
    # Note: We use 'is_goal' for both sum (goals) and count (shots) to avoid column conflicts
    player_stats = df_all_shots.groupby('player_name').agg({
        'is_goal': ['sum', 'count'], # Total goals scored AND total shots taken
        'team_name': 'first'         # Get the team name (same for all rows per player)
    }).reset_index()

    # Flatten column names and rename to be clearer
    player_stats.columns = ['player_name', 'goals', 'shots', 'team_name']

    # Calculate shooting percentage
    player_stats['shooting_percentage'] = (player_stats['goals'] / player_stats['shots']) * 100
    """)

    # Actually do this calculation
    player_stats = df_all_shots.groupby('player_name').agg({
        'is_goal': ['sum', 'count'], # Total goals scored AND total shots taken
        'team_name': 'first'         # Get the team name (same for all rows per player)
    }).reset_index()

    # Flatten column names and rename to be clearer
    player_stats.columns = ['player_name', 'goals', 'shots', 'team_name']
    player_stats['shooting_percentage'] = (player_stats['goals'] / player_stats['shots']) * 100

    # Add xG if available
    if 'shot_statsbomb_xg' in df_all_shots.columns:
        player_xg = df_all_shots.groupby('player_name')['shot_statsbomb_xg'].sum().reset_index()
        player_stats = player_stats.merge(player_xg, on='player_name', how='left')
        player_stats = player_stats.rename(columns={'shot_statsbomb_xg': 'total_xg'})

    #st.write("Here are our top goalscorers:")
    top_scorers = player_stats.sort_values('goals', ascending=False).head(10)
    #st.dataframe(top_scorers)

# Step 8: Grouping by team
st.subheader("Grouping Data by Team (Our Main Question!)")

if not df_all_shots.empty:
    st.write("""
    Finally! Let's answer our main question: **Which teams scored the most goals?**
    We'll group our player data by team.
    """)

    st.code("""
    # Group by team and sum up all the goals and shots
    team_stats = player_stats.groupby('team_name').agg({
        'goals': 'sum',        # Total goals by all players on the team
        'shots': 'sum',        # Total shots by all players on the team
        'player_name': 'count' # Number of different players who shot
    }).reset_index()

    # Rename the player count column
    team_stats.columns = ['team_name', 'total_goals', 'total_shots', 'players_who_shot']

    # Calculate team shooting percentage
    team_stats['team_shooting_percentage'] = (team_stats['total_goals'] / team_stats['total_shots']) * 100

    # Sort by goals scored (highest first)
    team_stats = team_stats.sort_values('total_goals', ascending=False)
    """)

    # Do the actual calculation
    team_stats = player_stats.groupby('team_name').agg({
        'goals': 'sum',
        'shots': 'sum',
        'player_name': 'count'
    }).reset_index()

    team_stats.columns = ['team_name', 'total_goals', 'total_shots', 'players_who_shot']
    team_stats['team_shooting_percentage'] = (team_stats['total_goals'] / team_stats['total_shots']) * 100
    team_stats = team_stats.sort_values('total_goals', ascending=False)

    st.subheader("🥇 RESULTS: Teams Ranked by Goals Scored!")
    st.dataframe(team_stats)


# Step 10: Create visualizations
st.subheader("📈 Creating Visualizations")

if 'team_stats' in locals() and not team_stats.empty:
    st.write("""
    Now let's create some charts to visualize our findings!
    """)

    # Bar chart of goals by team
    st.subheader("Goals Scored by Team")
    fig_goals = px.bar(
        team_stats.head(15),  # Top 15 teams
        x='team_name',
        y='total_goals',
        title='Goals Scored by Team in 2023 Women\'s World Cup',
        labels={'total_goals': 'Total Goals', 'team_name': 'Team'}
    )
    fig_goals.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_goals, use_container_width=True)


    goals_shots = alt.Chart(team_stats).mark_circle().encode(
            x='total_shots',
            y='total_goals',
            size=alt.Size('team_shooting_percentage',legend=None),
            color=alt.Color('team_name',legend=None),
            tooltip=['team_name','total_goals','total_shots','team_shooting_percentage']).properties(height=600).interactive()
    st.altair_chart(goals_shots, theme="streamlit", use_container_width=True)

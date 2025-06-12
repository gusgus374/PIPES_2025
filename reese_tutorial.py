"""
🏆 Reese's 2023 Women's World Cup Analysis Tutorial
==================================================

Welcome Reese! Today you're going to become a soccer data scientist!
We'll analyze the 2023 Women's World Cup to find out which teams scored the most goals.

This tutorial will walk you through:
1. Loading the 2023 Women's World Cup data
2. Getting player statistics (goals and shots)
3. Grouping data by players and teams
4. Using pandas functions to analyze the data
5. Creating visualizations

Let's get started! 🚀

"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Sbopen
import plotly.express as px

st.title("🏆 Reese's 2023 Women's World Cup Analysis")
st.header("Which teams scored the most goals?")

# Step 1: Understanding our data source
st.subheader("📚 Step 1: Understanding StatsBomb Data")
st.write("""
**What is StatsBomb?**
StatsBomb provides professional soccer data that real clubs use! They track every single event
in a soccer match - every pass, shot, goal, tackle, everything!

**What we're analyzing:**
The 2023 FIFA Women's World Cup (Australia/New Zealand)
""")

# Show a friendly message
coach_message = st.chat_message(name="Coach", avatar="⚽")
with coach_message:
    st.write("Hi Reese! Let's dive into some real soccer data analysis. "
             "We're going to find out which teams were the most dangerous in front of goal!")

# Step 2: Load the data
st.subheader("🔧 Step 2: Loading the 2023 Women's World Cup Data")

st.code("""
# First, let's set up our data connection
# StatsBomb has different tournaments with special ID numbers
# 2023 Women's World Cup: competition_id=72, season_id=107

competition_id = 72    # Women's World Cup
season_id = 107        # 2023 tournament
""")

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

    # Show what the match data looks like
    st.subheader("👀 Step 3: What does our match data look like?")
    st.write("Here are the first few matches from the tournament:")

    # Display some columns that are easy to understand
    display_cols = ['match_date', 'home_team_name', 'away_team_name', 'home_score', 'away_score']
    available_cols = [col for col in display_cols if col in df_matches.columns]
    st.dataframe(df_matches[available_cols].head(10))

    st.write(f"""
    **What we can see:**
    - There were {len(df_matches)} total matches
    - We can see team names, dates, and final scores
    - But we want MORE detail - we want to see individual player goals and shots!
    """)

# Step 4: Get detailed player data
st.subheader("🎯 Step 4: Getting Player-Level Data")

st.write("""
Now we need to load the **event data**. This contains every single action in every match:
- Every shot taken
- Every goal scored
- Every pass made
- Everything!

We'll focus on shots and goals.
""")

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

        # Show what our shooting data looks like
        st.subheader("🎯 Step 5: Understanding Our Shooting Data")
        st.write("Here's what our shooting data looks like:")
        st.dataframe(df_all_shots.head(10))

        st.write("""
        **Key columns explained:**
        - `player_name`: The player who took the shot
        - `team_name`: Which team they play for
        - `is_goal`: True if the shot was a goal, False if it was saved/missed (we create this from `outcome_name`)
        - `shot_statsbomb_xg`: Expected Goals (xG) - how likely this shot was to be a goal

        **Note:** These column names come from StatsBomb's official data structure -
        professional soccer data has specific naming conventions!
        """)

# Step 6: Pandas data manipulation
st.subheader("🐼 Step 6: Using Pandas to Analyze Our Data")

if not df_all_shots.empty:
    st.write("""
    Now for the fun part! We'll use **pandas** functions to answer our questions.
    Pandas is like Excel, but much more powerful for data analysis.
    """)

    # Demonstrate basic pandas functions
    st.subheader("6a. Basic Pandas Functions")

    st.code("""
    # Let's try some basic pandas functions on our shooting data:

    # How many total shots were there?
    total_shots = len(df_all_shots)

    # How many goals were scored?
    total_goals = df_all_shots['is_goal'].sum()  # sum() adds up all True values

    # What was the average xG per shot?
    avg_xg = df_all_shots['shot_statsbomb_xg'].mean()
    """)

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
st.subheader("📊 Step 7: Grouping Data by Player")

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

    st.write("Here are our top goalscorers:")
    top_scorers = player_stats.sort_values('goals', ascending=False).head(10)
    st.dataframe(top_scorers)

# Step 8: Grouping by team
st.subheader("🏆 Step 8: Grouping Data by Team (Our Main Question!)")

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

# Step 9: More pandas functions to explore
st.subheader("🔍 Step 9: More Pandas Functions to Try")

if not df_all_shots.empty and 'team_stats' in locals():
    st.write("""
    Let's try some more pandas functions to learn about our data:
    """)

    st.code("""
    # Try these pandas functions:

    # Maximum values
    most_goals = team_stats['total_goals'].max()
    most_shots = team_stats['total_shots'].max()

    # Minimum values
    fewest_goals = team_stats['total_goals'].min()
    fewest_shots = team_stats['total_shots'].min()

    # Average values
    avg_goals_per_team = team_stats['total_goals'].mean()
    avg_shots_per_team = team_stats['total_shots'].mean()

    # Find specific teams
    spain_stats = team_stats[team_stats['team_name'] == 'Spain']
    usa_stats = team_stats[team_stats['team_name'] == 'United States']
    """)

    # Calculate these
    most_goals = team_stats['total_goals'].max()
    most_shots = team_stats['total_shots'].max()
    fewest_goals = team_stats['total_goals'].min()
    fewest_shots = team_stats['total_shots'].min()
    avg_goals_per_team = team_stats['total_goals'].mean()
    avg_shots_per_team = team_stats['total_shots'].mean()

    # Display in metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Most Goals by Team", most_goals)
    with col2:
        st.metric("Fewest Goals", fewest_goals)
    with col3:
        st.metric("Avg Goals per Team", f"{avg_goals_per_team:.1f}")
    with col4:
        st.metric("Avg Shots per Team", f"{avg_shots_per_team:.1f}")

# Step 10: Create visualizations
st.subheader("📈 Step 10: Creating Visualizations")

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

    # Scatter plot: Goals vs Shots
    st.subheader("Goals vs Shots Analysis")
    fig_scatter = px.scatter(
        team_stats,
        x='total_shots',
        y='total_goals',
        hover_data=['team_name'],
        title='Goals vs Shots: Team Efficiency Analysis',
        labels={'total_shots': 'Total Shots', 'total_goals': 'Total Goals'}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Step 11: Your turn!
st.subheader("🚀 Step 11: Your Turn to Modify reese.py!")

st.write("""
**Congratulations Reese!** You've learned how to:
1. ✅ Load StatsBomb data
2. ✅ Filter for specific events (shots and goals)
3. ✅ Group data by players and teams
4. ✅ Use pandas functions like `.sum()`, `.mean()`, `.max()`, `.min()`
5. ✅ Create visualizations

**Now it's time to put this in your own reese.py file!**

Here's what you should do:
1. Copy the code sections you want to use
2. Paste them into your reese.py file
3. Customize the visualizations with your own style
4. Add your own analysis questions
5. Prepare to present your findings!

**Some ideas for your presentation:**
- Which team was most efficient (best shooting percentage)?
- Which players scored the most goals?
- How did your favorite team perform?
- What patterns do you see in the data?

**Remember:** You're now thinking like a real data scientist! 🎉
""")

# Sample code for reese.py
st.subheader("📝 Sample Code for Your reese.py File")
st.code("""
import streamlit as st
import pandas as pd
import plotly.express as px
from mplsoccer import Sbopen

st.title("Reese's 2023 Women's World Cup Analysis")
st.subheader("Which teams scored the most goals?")

# Load data function (copy from tutorial)
@st.cache_data
def load_match_data(competition_id, season_id):
    parser = Sbopen()
    return parser.match(competition_id=competition_id, season_id=season_id)

# Your analysis code here...
# (Copy the sections you want from the tutorial above)

st.write("My findings show that...")
# Add your conclusions here!
""")

coach_message = st.chat_message(name="Coach", avatar="⚽")
with coach_message:
    st.write("Great job Reese! You're ready to analyze soccer data like a pro. "
             "Remember to explain your findings clearly in your presentation tomorrow. "
             "Focus on the story the data tells about which teams were most dangerous in attack!")
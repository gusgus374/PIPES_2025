"""
🌟 Shaun's Player Comparison Analysis Tutorial
=============================================

Welcome Shaun! Today you're going to analyze individual player performance and
make comparisons across different tournaments and eras.

We'll compare:
- Lamine Yamal (Spain) - using available tournament data
- Lionel Messi - World Cup data for comparison

This tutorial will teach you:
1. Loading data from different tournaments
2. Player-specific filtering and analysis
3. Creating comparative metrics
4. Handling data from different competitions
5. Building side-by-side comparisons
6. Advanced player performance analysis

Let's become a scouting analyst! 🎯

"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Sbopen, Pitch
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("🌟 Shaun's Player Comparison Analysis")
st.header("Individual Player Analysis: Comparing Generational Talents")

# Show a friendly message
coach_message = st.chat_message(name="Coach", avatar="⚽")
with coach_message:
    st.write("Hey Shaun! Today we're doing advanced player analysis - comparing individual "
             "performances across different tournaments. This is exactly what scouts do when "
             "they're evaluating talent!")
    st.write("We'll analyze player performances and learn to compare them fairly "
             "across different competitions and eras.")

# Step 1: Understanding Player Analysis
st.subheader("📊 Step 1: Understanding Player Comparison Analysis")
st.write("""
**What makes player comparison different from team analysis?**
- We focus on individual metrics, not team totals
- We need to account for different tournaments and playing time
- Age and experience are important factors
- We use per-90 minute statistics for fair comparison

**Key Metrics for Attacking Players:**
- Goals and Assists (basic productivity)
- xG and xA (expected productivity)
- Dribbles and Key Passes (creativity)
- Progressive actions (advancing play)
- Shooting efficiency
""")

# Step 2: Available Tournaments
st.subheader("🏆 Step 2: Tournament Selection and Data Loading")

# Define available tournaments for our analysis
tournament_options = {
    "Euro 2024": {
        "competition_id": 55,
        "season_id": 282,
        "description": "Lamine Yamal's breakout tournament"
    },
    "La Liga (Barcelona - Young Messi Era)": {
        "competition_id": 11,
        "season_id": 37,
        "description": "Young Messi at Barcelona"
    },
    "2022 FIFA World Cup (Qatar)": {
        "competition_id": 43,
        "season_id": 3,
        "description": "Messi's World Cup triumph"
    },
    "2018 FIFA World Cup (Russia)": {
        "competition_id": 43,
        "season_id": 106,
        "description": "Earlier World Cup data"
    }
}

st.write("""
**Data Strategy:**
- We'll use StatsBomb's free tournament data
- Focus on World Cup data where we have comprehensive coverage
- Learn techniques that apply to any tournament comparison
- This teaches you how to work with available data in real analysis projects
""")

# Cache the data loading functions
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

@st.cache_data
def get_player_data_from_tournament(df_matches, player_name, team_name=None):
    """Get all data for a specific player from a tournament."""
    match_ids = df_matches["match_id"].tolist()
    player_data = []

    progress_bar = st.progress(0)
    st.write(f"Searching for {player_name} in {len(match_ids)} matches...")

    for i, match_id in enumerate(match_ids):
        try:
            # Load event data for this match
            df_events = load_event_data(match_id)

            if not df_events.empty and 'player_name' in df_events.columns:
                # Filter for our specific player
                # Use fuzzy matching in case of slight name variations
                player_events = df_events[
                    df_events['player_name'].str.contains(player_name, case=False, na=False)
                ]

                # If team name provided, filter by team too
                if team_name and 'team_name' in df_events.columns:
                    player_events = player_events[
                        player_events['team_name'].str.contains(team_name, case=False, na=False)
                    ]

                if not player_events.empty:
                    player_events['match_id'] = match_id
                    player_data.append(player_events)

            # Update progress
            progress_bar.progress((i + 1) / len(match_ids))

        except Exception as e:
            continue

    progress_bar.empty()

    if player_data:
        return pd.concat(player_data, ignore_index=True)
    else:
        return pd.DataFrame()

# Step 3: Load tournament data and search for players
st.subheader("🔍 Step 3: Finding Our Players")

# Let's start with 2022 World Cup
st.write("**Loading 2022 World Cup data...**")
wc2022_matches = load_match_data(43, 3)

if not wc2022_matches.empty:
    st.success(f"✅ Loaded {len(wc2022_matches)} matches from 2022 World Cup")

    # Search for Messi
    with st.spinner("Searching for Messi in 2022 World Cup..."):
        messi_data = get_player_data_from_tournament(wc2022_matches, "Messi", "Argentina")

    if not messi_data.empty:
        st.success(f"✅ Found {len(messi_data)} events for Messi!")

        # Show sample of Messi's data
        with st.expander("👀 Messi's Data Sample"):
            sample_cols = ['minute', 'type_name', 'player_name', 'team_name']
            available_cols = [col for col in sample_cols if col in messi_data.columns]
            st.dataframe(messi_data[available_cols].head(10))
    else:
        st.warning("⚠️ No Messi data found in 2022 World Cup")

# Step 4: Player Analysis Functions
st.subheader("⚡ Step 4: Player Analysis Functions")

st.write("""
Now let's create functions to analyze individual player performance.
These functions will calculate key metrics that scouts use to evaluate players.
""")

st.code("""
def analyze_player_performance(player_data):
    '''Analyze a player's performance from their event data'''

    if player_data.empty:
        return {}

    # Basic info
    matches_played = player_data['match_id'].nunique()

    # Calculate minutes played (estimate from last event in each match)
    minutes_per_match = player_data.groupby('match_id')['minute'].max()
    total_minutes = minutes_per_match.sum()

    # Goals and shots
    shots = player_data[player_data['type_name'] == 'Shot']
    goals = shots[shots['outcome_name'] == 'Goal'] if not shots.empty else pd.DataFrame()

    # Passes
    passes = player_data[player_data['type_name'] == 'Pass']
    successful_passes = passes[passes['outcome_name'].isna()] if not passes.empty else pd.DataFrame()

    # Dribbles
    dribbles = player_data[player_data['type_name'] == 'Dribble']
    successful_dribbles = dribbles[dribbles['outcome_name'] == 'Complete'] if not dribbles.empty else pd.DataFrame()

    # Calculate per-90 stats
    minutes_factor = 90 / total_minutes if total_minutes > 0 else 0

    stats = {
        'matches_played': matches_played,
        'minutes_played': total_minutes,
        'goals': len(goals),
        'shots': len(shots),
        'goals_per_90': len(goals) * minutes_factor,
        'shots_per_90': len(shots) * minutes_factor,
        'passes': len(passes),
        'successful_passes': len(successful_passes),
        'pass_completion': len(successful_passes) / len(passes) * 100 if len(passes) > 0 else 0,
        'passes_per_90': len(passes) * minutes_factor,
        'dribbles': len(dribbles),
        'successful_dribbles': len(successful_dribbles),
        'dribble_success': len(successful_dribbles) / len(dribbles) * 100 if len(dribbles) > 0 else 0,
        'dribbles_per_90': len(dribbles) * minutes_factor
    }

    # Add xG if available
    if not shots.empty and 'shot_statsbomb_xg' in shots.columns:
        total_xg = shots['shot_statsbomb_xg'].sum()
        stats['xg'] = total_xg
        stats['xg_per_90'] = total_xg * minutes_factor

    return stats
""")

# Implement the function
def analyze_player_performance(player_data):
    """Analyze a player's performance from their event data"""

    if player_data.empty:
        return {}

    # Basic info
    matches_played = player_data['match_id'].nunique()

    # Calculate minutes played (estimate from last event in each match)
    minutes_per_match = player_data.groupby('match_id')['minute'].max()
    total_minutes = minutes_per_match.sum()

    # Goals and shots
    shots = player_data[player_data['type_name'] == 'Shot']
    goals = shots[shots['outcome_name'] == 'Goal'] if not shots.empty else pd.DataFrame()

    # Passes
    passes = player_data[player_data['type_name'] == 'Pass']
    successful_passes = passes[passes['outcome_name'].isna()] if not passes.empty else pd.DataFrame()

    # Dribbles
    dribbles = player_data[player_data['type_name'] == 'Dribble']
    successful_dribbles = dribbles[dribbles['outcome_name'] == 'Complete'] if not dribbles.empty else pd.DataFrame()

    # Calculate per-90 stats
    minutes_factor = 90 / total_minutes if total_minutes > 0 else 0

    stats = {
        'matches_played': matches_played,
        'minutes_played': total_minutes,
        'goals': len(goals),
        'shots': len(shots),
        'goals_per_90': len(goals) * minutes_factor,
        'shots_per_90': len(shots) * minutes_factor,
        'passes': len(passes),
        'successful_passes': len(successful_passes),
        'pass_completion': len(successful_passes) / len(passes) * 100 if len(passes) > 0 else 0,
        'passes_per_90': len(passes) * minutes_factor,
        'dribbles': len(dribbles),
        'successful_dribbles': len(successful_dribbles),
        'dribble_success': len(successful_dribbles) / len(dribbles) * 100 if len(dribbles) > 0 else 0,
        'dribbles_per_90': len(dribbles) * minutes_factor
    }

    # Add xG if available
    if not shots.empty and 'shot_statsbomb_xg' in shots.columns:
        total_xg = shots['shot_statsbomb_xg'].sum()
        stats['xg'] = total_xg
        stats['xg_per_90'] = total_xg * minutes_factor

    return stats

# Step 5: Analyze our players
st.subheader("📈 Step 5: Player Performance Analysis")

if 'messi_data' in locals() and not messi_data.empty:
    st.write("**Analyzing Messi's 2022 World Cup Performance...**")

    messi_stats = analyze_player_performance(messi_data)

    if messi_stats:
        st.write("**Messi's Statistics:**")

        # Display in organized columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Matches Played", messi_stats['matches_played'])
            st.metric("Minutes Played", f"{messi_stats['minutes_played']:.0f}")
            st.metric("Goals", messi_stats['goals'])

        with col2:
            st.metric("Shots", messi_stats['shots'])
            st.metric("Goals per 90", f"{messi_stats['goals_per_90']:.2f}")
            st.metric("Shots per 90", f"{messi_stats['shots_per_90']:.2f}")

        with col3:
            st.metric("Pass Completion %", f"{messi_stats['pass_completion']:.1f}%")
            st.metric("Dribble Success %", f"{messi_stats['dribble_success']:.1f}%")
            if 'xg_per_90' in messi_stats:
                st.metric("xG per 90", f"{messi_stats['xg_per_90']:.2f}")

# Step 6: Comparison Framework
st.subheader("🔄 Step 6: Player Comparison Framework")

st.write("""
Now let's create a framework for comparing players. This is where it gets interesting!
""")

st.code("""
def create_player_comparison(player1_stats, player2_stats, player1_name, player2_name):
    '''Create a comprehensive comparison between two players'''

    # Metrics to compare
    comparison_metrics = [
        'goals_per_90', 'shots_per_90', 'pass_completion',
        'dribbles_per_90', 'dribble_success'
    ]

    comparison_data = []

    for metric in comparison_metrics:
        if metric in player1_stats and metric in player2_stats:
            comparison_data.append({
                'Metric': metric.replace('_', ' ').title(),
                player1_name: player1_stats[metric],
                player2_name: player2_stats[metric],
                'Difference': player1_stats[metric] - player2_stats[metric]
            })

    return pd.DataFrame(comparison_data)
""")

def create_player_comparison(player1_stats, player2_stats, player1_name, player2_name):
    """Create a comprehensive comparison between two players"""

    # Metrics to compare
    comparison_metrics = [
        'goals_per_90', 'shots_per_90', 'pass_completion',
        'dribbles_per_90', 'dribble_success'
    ]

    comparison_data = []

    for metric in comparison_metrics:
        if metric in player1_stats and metric in player2_stats:
            comparison_data.append({
                'Metric': metric.replace('_', ' ').title(),
                player1_name: player1_stats[metric],
                player2_name: player2_stats[metric],
                'Difference': player1_stats[metric] - player2_stats[metric]
            })

    return pd.DataFrame(comparison_data)

# Step 7: Interactive Player Selection
st.subheader("🎯 Step 7: Interactive Player Analysis")

st.write("""
**Your Task:** Now you'll set up the analysis to compare any two players!
""")

# Tournament selection
selected_tournament = st.selectbox(
    "Choose tournament for analysis:",
    list(tournament_options.keys()),
    key="tournament_select"
)

tournament_config = tournament_options[selected_tournament]
competition_id = tournament_config["competition_id"]
season_id = tournament_config["season_id"]

# Load selected tournament
with st.spinner(f"Loading {selected_tournament}..."):
    tournament_matches = load_match_data(competition_id, season_id)

if not tournament_matches.empty:
    st.success(f"✅ Loaded {len(tournament_matches)} matches from {selected_tournament}")

    # Player input section
    st.subheader("👥 Player Selection")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Player 1:**")
        player1_name = st.text_input("Enter Player 1 Name:", value="Lamine Yamal")
        player1_team = st.text_input("Player 1 Team (optional):", value="Spain")

    with col2:
        st.write("**Player 2:**")
        player2_name = st.text_input("Enter Player 2 Name:", value="Messi")
        player2_team = st.text_input("Player 2 Team (optional):", value="Barcelona")

    if st.button("🔍 Analyze Players"):
        # Analysis for both players
        with st.spinner(f"Analyzing {player1_name} and {player2_name}..."):

            # Get data for both players
            player1_data = get_player_data_from_tournament(
                tournament_matches, player1_name, player1_team if player1_team else None
            )
            player2_data = get_player_data_from_tournament(
                tournament_matches, player2_name, player2_team if player2_team else None
            )

            # Analyze both players
            if not player1_data.empty:
                player1_stats = analyze_player_performance(player1_data)
                st.success(f"✅ Found data for {player1_name}")
            else:
                st.warning(f"⚠️ No data found for {player1_name}")
                player1_stats = {}

            if not player2_data.empty:
                player2_stats = analyze_player_performance(player2_data)
                st.success(f"✅ Found data for {player2_name}")
            else:
                st.warning(f"⚠️ No data found for {player2_name}")
                player2_stats = {}

            # Create comparison if both players found
            if player1_stats and player2_stats:
                st.subheader("📊 Player Comparison Results")

                # Side-by-side stats
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**{player1_name} Statistics:**")
                    st.metric("Goals per 90", f"{player1_stats.get('goals_per_90', 0):.2f}")
                    st.metric("Shots per 90", f"{player1_stats.get('shots_per_90', 0):.2f}")
                    st.metric("Pass Completion %", f"{player1_stats.get('pass_completion', 0):.1f}%")
                    st.metric("Dribbles per 90", f"{player1_stats.get('dribbles_per_90', 0):.2f}")

                with col2:
                    st.write(f"**{player2_name} Statistics:**")
                    st.metric("Goals per 90", f"{player2_stats.get('goals_per_90', 0):.2f}")
                    st.metric("Shots per 90", f"{player2_stats.get('shots_per_90', 0):.2f}")
                    st.metric("Pass Completion %", f"{player2_stats.get('pass_completion', 0):.1f}%")
                    st.metric("Dribbles per 90", f"{player2_stats.get('dribbles_per_90', 0):.2f}")

                # Detailed comparison table
                comparison_df = create_player_comparison(
                    player1_stats, player2_stats, player1_name, player2_name
                )

                if not comparison_df.empty:
                    st.subheader("📋 Detailed Comparison")
                    st.dataframe(comparison_df, use_container_width=True)

                    # Create a simple bar chart comparison
                    st.subheader("📊 Visual Comparison")

                    # Prepare data for visualization
                    metrics_to_plot = ['goals_per_90', 'shots_per_90', 'dribbles_per_90']
                    metric_labels = ['Goals per 90', 'Shots per 90', 'Dribbles per 90']

                    plot_data = {
                        'Metric': metric_labels + metric_labels,
                        'Value': [],
                        'Player': []
                    }

                    for metric in metrics_to_plot:
                        plot_data['Value'].append(player1_stats.get(metric, 0))
                        plot_data['Player'].append(player1_name)
                        plot_data['Value'].append(player2_stats.get(metric, 0))
                        plot_data['Player'].append(player2_name)

                    plot_df = pd.DataFrame(plot_data)

                    fig = px.bar(plot_df, x='Metric', y='Value', color='Player',
                               title=f'Performance Comparison: {player1_name} vs {player2_name}',
                               barmode='group')
                    st.plotly_chart(fig, use_container_width=True)

# Step 8: Advanced Analysis Ideas
st.subheader("🚀 Step 8: Advanced Analysis Ideas")

st.write("""
**For your presentation, consider these advanced analyses:**

1. **Age-Adjusted Comparison**: Compare performance relative to player age
2. **Tournament Progression**: How did performance change throughout the tournament?
3. **Position Heat Maps**: Where on the field do these players operate?
4. **Impact Analysis**: Which actions led to goals or dangerous situations?
5. **Pressure Analysis**: How do they perform under pressure vs low pressure?

**Key Questions to Answer:**
- What makes each player unique in their style?
- How do their strengths complement their teams?
- What can young players learn from elite performers?
""")

# Step 9: Your Turn Section
st.subheader("🚀 Step 9: Your Turn to Build the Analysis!")

st.write("""
**Congratulations Shaun!** You've learned:

1. ✅ **Player-specific data loading** from tournament data
2. ✅ **Individual performance metrics** calculation
3. ✅ **Per-90 minute statistics** for fair comparison
4. ✅ **Comparative analysis** techniques
5. ✅ **Interactive player selection** and analysis
6. ✅ **Visualization frameworks** for player comparison

**Now it's time to put this in your shaun.py file!**

**Your Mission:**
1. Copy the analysis framework to your file
2. Set up the player comparison system
3. Focus on Lamine Yamal vs Messi comparison
4. Add your own insights about generational talent
5. Create compelling visualizations

**Remember**: The goal isn't just to compare numbers, but to understand what makes each player special!
""")

# Sample starter code
st.subheader("📝 Starter Code for Your shaun.py File")
st.code("""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import Sbopen

st.title("Shaun's Player Comparison: Yamal vs Messi")
st.subheader("Analyzing Generational Talent")

# Your player analysis functions here...
# (Copy from the tutorial above)

# Tournament selection
tournament = st.selectbox("Choose Tournament:", [...])

# Player analysis
player1_name = st.text_input("Player 1:", value="Lamine Yamal")
player2_name = st.text_input("Player 2:", value="Messi")

# Your analysis code here...

st.write("My analysis shows that...")
# Add your conclusions about what makes these players special!
""")

coach_message = st.chat_message(name="Coach", avatar="⚽")
with coach_message:
    st.write("Outstanding work Shaun! You're now equipped to analyze individual players like a professional scout. "
             "Focus on what makes each player unique - their playing style, efficiency, and impact on the game. "
             "This type of analysis is exactly what clubs use to identify and compare talent!")

st.write("---")
st.write("*Remember: The goal isn't just to compare numbers, but to understand what makes each player special!*")
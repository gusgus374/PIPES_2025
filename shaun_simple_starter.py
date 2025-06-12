"""
🌟 Shaun's Player Comparison Project
==================================

Copy this code into your shaun.py file and complete the TODOs!
This will help you compare Lamine Yamal and Messi's performances.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import Sbopen

# TODO 1: Add your title and introduction
st.title("🌟 Shaun's Player Analysis: Yamal vs Messi")
st.write("Comparing generational talents across different eras!")

# TODO 2: Load data functions (provided for you)
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

@st.cache_data
def get_player_data(df_matches, player_name, team_name=None):
    """Get all data for a specific player from a tournament"""
    match_ids = df_matches["match_id"].tolist()
    player_data = []

    progress = st.progress(0)
    for i, match_id in enumerate(match_ids):
        try:
            events = load_event_data(match_id)

            if not events.empty and 'player_name' in events.columns:
                # Find player events (fuzzy matching)
                player_events = events[
                    events['player_name'].str.contains(player_name, case=False, na=False)
                ]

                # Filter by team if provided
                if team_name and 'team_name' in events.columns:
                    player_events = player_events[
                        player_events['team_name'].str.contains(team_name, case=False, na=False)
                    ]

                if not player_events.empty:
                    player_events['match_id'] = match_id
                    player_data.append(player_events)

            progress.progress((i + 1) / len(match_ids))
        except:
            continue

    progress.empty()

    if player_data:
        return pd.concat(player_data, ignore_index=True)
    return pd.DataFrame()

# TODO 3: Player analysis function
def analyze_player(player_data):
    """Analyze a player's performance from their event data"""

    if player_data.empty:
        return {}

    # Basic info
    matches_played = player_data['match_id'].nunique()

    # Calculate minutes played
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

    return {
        'matches_played': matches_played,
        'minutes_played': total_minutes,
        'goals': len(goals),
        'shots': len(shots),
        'goals_per_90': len(goals) * minutes_factor,
        'shots_per_90': len(shots) * minutes_factor,
        'pass_completion': len(successful_passes) / len(passes) * 100 if len(passes) > 0 else 0,
        'dribbles_per_90': len(dribbles) * minutes_factor,
        'dribble_success': len(successful_dribbles) / len(dribbles) * 100 if len(dribbles) > 0 else 0
    }

# TODO 4: Load tournament data
st.subheader("Step 1: Tournament Selection")

tournament_options = {
    "Euro 2024": {"competition_id": 55, "season_id": 182},
    "La Liga (Barcelona - Young Messi Era)": {"competition_id": 11, "season_id": 37},
    "2022 FIFA World Cup (Qatar)": {"competition_id": 43, "season_id": 3},
    "2018 FIFA World Cup (Russia)": {"competition_id": 43, "season_id": 106}
}

selected_tournament = st.selectbox("Choose Tournament:", list(tournament_options.keys()))
tournament_config = tournament_options[selected_tournament]

# Load tournament data
st.write(f"Loading {selected_tournament}...")
tournament_matches = load_match_data(
    tournament_config["competition_id"],
    tournament_config["season_id"]
)
st.success(f"✅ Loaded {len(tournament_matches)} matches!")

# TODO 5: Player selection
st.subheader("Step 2: Player Selection")

col1, col2 = st.columns(2)

with col1:
    st.write("**Player 1:**")
    player1_name = st.text_input("Player 1 Name:", value="Lamine Yamal")
    player1_team = st.text_input("Player 1 Team:", value="Spain")

with col2:
    st.write("**Player 2:**")
    player2_name = st.text_input("Player 2 Name:", value="Messi")
    player2_team = st.text_input("Player 2 Team:", value="Barcelona")

# TODO 6: Analyze players when button is clicked
if st.button("🔍 Analyze Both Players"):

    # Get player data
    with st.spinner(f"Loading data for {player1_name}..."):
        player1_data = get_player_data(tournament_matches, player1_name, player1_team)

    with st.spinner(f"Loading data for {player2_name}..."):
        player2_data = get_player_data(tournament_matches, player2_name, player2_team)

    # Analyze both players
    if not player1_data.empty and not player2_data.empty:
        player1_stats = analyze_player(player1_data)
        player2_stats = analyze_player(player2_data)

        st.success("✅ Found data for both players!")

        # TODO 7: Display player statistics
        st.subheader("Step 3: Player Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**{player1_name} Stats:**")
            st.metric("Matches Played", player1_stats['matches_played'])
            st.metric("Goals", player1_stats['goals'])
            st.metric("Goals per 90", f"{player1_stats['goals_per_90']:.2f}")
            st.metric("Shots per 90", f"{player1_stats['shots_per_90']:.2f}")
            st.metric("Pass Completion %", f"{player1_stats['pass_completion']:.1f}%")

        with col2:
            st.write(f"**{player2_name} Stats:**")
            st.metric("Matches Played", player2_stats['matches_played'])
            st.metric("Goals", player2_stats['goals'])
            st.metric("Goals per 90", f"{player2_stats['goals_per_90']:.2f}")
            st.metric("Shots per 90", f"{player2_stats['shots_per_90']:.2f}")
            st.metric("Pass Completion %", f"{player2_stats['pass_completion']:.1f}%")

        # TODO 8: Create comparison table
        st.subheader("Step 4: Direct Comparison")

        comparison_data = {
            'Metric': ['Goals per 90', 'Shots per 90', 'Pass Completion %', 'Dribbles per 90'],
            player1_name: [
                player1_stats['goals_per_90'],
                player1_stats['shots_per_90'],
                player1_stats['pass_completion'],
                player1_stats['dribbles_per_90']
            ],
            player2_name: [
                player2_stats['goals_per_90'],
                player2_stats['shots_per_90'],
                player2_stats['pass_completion'],
                player2_stats['dribbles_per_90']
            ]
        }

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)

        # TODO 9: Create visualization
        st.subheader("Step 5: Visual Comparison")

        # Prepare data for bar chart
        metrics = ['Goals per 90', 'Shots per 90', 'Dribbles per 90']
        plot_data = {
            'Metric': metrics + metrics,
            'Value': [
                player1_stats['goals_per_90'],
                player1_stats['shots_per_90'],
                player1_stats['dribbles_per_90'],
                player2_stats['goals_per_90'],
                player2_stats['shots_per_90'],
                player2_stats['dribbles_per_90']
            ],
            'Player': [player1_name] * 3 + [player2_name] * 3
        }

        plot_df = pd.DataFrame(plot_data)

        # Create bar chart
        fig = px.bar(plot_df, x='Metric', y='Value', color='Player',
                    title=f'Performance Comparison: {player1_name} vs {player2_name}',
                    barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    else:
        if player1_data.empty:
            st.warning(f"⚠️ No data found for {player1_name}")
        if player2_data.empty:
            st.warning(f"⚠️ No data found for {player2_name}")

# TODO 10: Add your conclusions
st.subheader("My Analysis")
st.write("""
Based on my comparison analysis:

**Key Findings:**
- [TODO: Which player had better goal scoring stats?]
- [TODO: Who was more efficient in front of goal?]
- [TODO: What differences did you notice in their playing styles?]

**What I learned:**
- How to load and analyze individual player data
- How to create fair comparisons using per-90 minute stats
- How to visualize player performance differences
- How to think like a scout when evaluating talent!

**Why this matters:**
This type of analysis helps us understand what makes players special
and how different talents can be compared fairly across tournaments.
""")

# Add some fun
if st.button("🏆 I'm a Player Analyst!"):
    st.balloons()
    st.write("You just analyzed players like a professional scout!")

st.write("---")
st.write("*Analysis by Shaun using StatsBomb professional data*")
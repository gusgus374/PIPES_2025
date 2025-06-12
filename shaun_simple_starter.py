"""
🌟 Shaun's Player Comparison Project
==================================

**Your Mission:** Compare Lamine Yamal at Euro 2024 to a young Lionel Messi
at Barcelona in the 2004/2005 season.

Complete the TODOs below to build your analysis!
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from mplsoccer import Sbopen

# --- Page Setup ---
st.set_page_config(layout="wide")
st.title("🌟 Shaun's Player Analysis: Yamal vs. Messi")
st.write("Comparing a rising star to a young legend across different competitions and eras.")

# --- Data Loading Functions (Provided for you) ---
@st.cache_data
def load_all_events(competition_id, season_id):
    """Loads all event data for a specific competition season."""
    parser = Sbopen()
    try:
        df_matches = parser.match(competition_id=competition_id, season_id=season_id)
        match_ids = df_matches['match_id'].tolist()

        all_events = []
        progress_text = f"Loading {len(match_ids)} matches for competition {competition_id}..."
        progress_bar = st.progress(0, text=progress_text)

        for i, match_id in enumerate(match_ids):
            events = parser.event(match_id)[0]
            all_events.append(events)
            progress_bar.progress((i + 1) / len(match_ids), text=f"Loaded match {i+1}/{len(match_ids)}")

        progress_bar.empty()
        return pd.concat(all_events, ignore_index=True)

    except Exception:
        st.error(f"Could not load data for competition {competition_id}, season {season_id}. The data might not be available in StatsBomb's free data.")
        return pd.DataFrame()

# TODO 1: Define the competition and season IDs
YAMAL_COMP_ID = 55      # Euro
YAMAL_SEASON_ID = 282   # 2024 Season

MESSI_COMP_ID = 11      # La Liga
MESSI_SEASON_ID = 37    # 2004/2005 Season

# --- Data Loading Section ---
st.subheader("1. Loading Data from Two Different Competitions")

# Load Yamal's data
st.write("Loading Lamine Yamal's Euro 2024 data...")
yamal_events = load_all_events(YAMAL_COMP_ID, YAMAL_SEASON_ID)
if not yamal_events.empty:
    yamal_data = yamal_events[yamal_events['player_name'].str.contains("Lamine Yamal", na=False)]
    st.success(f"✅ Found {len(yamal_data)} events for Lamine Yamal.")
else:
    yamal_data = pd.DataFrame()

# Load Messi's data
st.write("Loading young Lionel Messi's 2004/05 La Liga data...")
messi_events = load_all_events(MESSI_COMP_ID, MESSI_SEASON_ID)
if not messi_events.empty:
    messi_data = messi_events[messi_events['player_name'].str.contains("Lionel Messi", na=False)]
    st.success(f"✅ Found {len(messi_data)} events for Lionel Messi.")
else:
    messi_data = pd.DataFrame()

# --- Analysis Function ---
def analyze_player(player_df, player_name):
    """Calculates key per-90 stats for a player."""
    if player_df.empty:
        return None

    # Calculate total minutes played (estimated)
    minutes_played = player_df.groupby('match_id')['minute'].max().sum()
    if minutes_played == 0:
        return None

    per_90_factor = 90 / minutes_played

    # TODO 2: Calculate stats
    # Find all the shots the player took
    shots = player_df[player_df['type_name'] == 'Shot']
    # Find all the goals the player scored
    goals = shots[shots['outcome_name'] == 'Goal']
    # Find all the dribbles the player attempted
    dribbles = player_df[player_df['type_name'] == 'Dribble']
    # Find successful dribbles
    successful_dribbles = dribbles[dribbles['outcome_name'] == 'Complete']

    # Create a dictionary with all the calculated stats
    stats = {
        "Player": player_name,
        "Minutes Played": minutes_played,
        "Goals per 90": len(goals) * per_90_factor,
        "Shots per 90": len(shots) * per_90_factor,
        "Dribbles per 90": len(dribbles) * per_90_factor,
        "Dribble Success (%)": (len(successful_dribbles) / len(dribbles) * 100) if len(dribbles) > 0 else 0
    }
    return stats

# --- Run Analysis and Display ---
st.subheader("2. Comparing Their Performance")

# Run the analysis for both players
yamal_stats = analyze_player(yamal_data, "Lamine Yamal (Euro 2024)")
messi_stats = analyze_player(messi_data, "Lionel Messi (La Liga '04/05)")

# TODO 3: Create the comparison DataFrame
if yamal_stats and messi_stats:
    # Combine the stats dictionaries into a list
    comparison_list = [yamal_stats, messi_stats]
    # Create the DataFrame
    df_comparison = pd.DataFrame(comparison_list)

    st.subheader("Comparison Table")
    st.dataframe(df_comparison.set_index("Player").round(2), use_container_width=True)

    # TODO 4: Create the visualization
    st.subheader("Visual Comparison")

    # "Melt" the dataframe to prepare it for plotting
    df_melted = df_comparison.melt(
        id_vars='Player',
        value_vars=['Goals per 90', 'Shots per 90', 'Dribbles per 90'],
        var_name='Metric',
        value_name='Value'
    )

    # Create the bar chart
    fig = px.bar(
        df_melted,
        x='Metric',
        y='Value',
        color='Player',
        barmode='group',
        title='Per 90 Minute Comparison: Yamal vs. Young Messi'
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Could not generate comparison. Check if data was loaded correctly for both players.")

# --- Your Conclusions ---
st.subheader("3. Your Analysis and Hot Takes!")
st.write("Based on the data, what are your thoughts? This is where you become the analyst.")

# TODO 5: Write your conclusions
your_analysis = st.text_area(
    "What's your hot take? What does the data tell you about these two players at similar stages?",
    "Based on the data, I noticed that..."
)

if st.button("Submit My Hot Take 🔥"):
    st.success("Great analysis! That's what professional scouting is all about.")
    st.balloons()
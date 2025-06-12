"""
🌟 Shaun's Cross-Era Player Comparison
======================================

Welcome Shaun! Today, you're going to do one of the most exciting things in sports analytics:
compare players from **different competitions and different eras**.

This is how scouts and analysts answer questions like "How did a young Messi compare
to today's rising stars like Lamine Yamal?"

**Your Mission:**
1.  Load Lamine Yamal's data from Euro 2024.
2.  Load a young Lionel Messi's data from the 2004/2005 La Liga season.
3.  Analyze and compare their performance using per-90-minute stats.

Let's get started! 🎯
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from mplsoccer import Sbopen

st.title("🌟 Shaun's Player Comparison")
st.header("Lamine Yamal (Euro 2024) vs. Young Messi (La Liga 2004/05)")

# --- Coach's Introduction ---
coach_message = st.chat_message(name="Coach", avatar="⚽")
with coach_message:
    st.write("Hey Shaun! This is a real-world data science challenge. We have two separate datasets "
             "from different tournaments and different times. Our job is to process them separately "
             "and then bring the results together to make a fair comparison. This is a powerful skill!")

# --- Step 1: Data Loading Functions ---
st.subheader("🔧 Step 1: Setup Our Data Tools")
st.write("First, we need our functions to get the data from StatsBomb.")

with st.echo():
    # These functions will help us load the data we need.
    # We use @st.cache_data to make our app run faster after the first load.
    @st.cache_data
    def load_match_data(competition_id, season_id):
        """Loads all matches for a given competition and season."""
        parser = Sbopen()
        try:
            df_matches = parser.match(competition_id=competition_id, season_id=season_id)
            return df_matches
        except Exception as e:
            st.error(f"Could not load matches for competition {competition_id}, season {season_id}. Error: {e}")
            return pd.DataFrame()

    @st.cache_data
    def get_all_events_for_competition(competition_id, season_id):
        """Gets all event data for every match in a competition."""
        df_matches = load_match_data(competition_id, season_id)
        if df_matches.empty:
            return pd.DataFrame()

        all_events = []
        match_ids = df_matches['match_id'].tolist()

        progress_bar = st.progress(0, text=f"Loading {len(match_ids)} matches...")
        for i, match_id in enumerate(match_ids):
            try:
                parser = Sbopen()
                events = parser.event(match_id)[0]  # Get the event dataframe
                events['match_id'] = match_id
                all_events.append(events)
            except Exception:
                continue # Skip if a match fails
            progress_bar.progress((i + 1) / len(match_ids), text=f"Loading match {i+1}/{len(match_ids)}")

        progress_bar.empty()

        if not all_events:
            return pd.DataFrame()

        return pd.concat(all_events, ignore_index=True)


# --- Step 2: Load Data for Lamine Yamal ---
st.subheader("🇪🇸 Step 2: Get Lamine Yamal's Euro 2024 Data")

with st.echo():
    # Define competition and season IDs for Euro 2024
    EURO_2024_COMP_ID = 55
    EURO_2024_SEASON_ID = 282 # Corrected ID!

    # Load all events from Euro 2024
    st.write("Loading all event data from Euro 2024...")
    euro_2024_events = get_all_events_for_competition(EURO_2024_COMP_ID, EURO_2024_SEASON_ID)

    # Filter for Lamine Yamal's events
    if not euro_2024_events.empty:
        st.success("✅ Euro 2024 data loaded!")
        yamal_data = euro_2024_events[
            euro_2024_events['player_name'].str.contains("Lamine Yamal", na=False)
        ]
        st.write(f"Found {len(yamal_data)} events for Lamine Yamal in Euro 2024.")
    else:
        st.warning("Could not load Euro 2024 data.")
        yamal_data = pd.DataFrame()


# --- Step 3: Load Data for Young Lionel Messi ---
st.subheader("🐐 Step 3: Get Young Messi's 2004/05 La Liga Data")

with st.echo():
    # Define competition and season IDs for La Liga 2004/2005
    LA_LIGA_0405_COMP_ID = 11
    LA_LIGA_0405_SEASON_ID = 37

    # Load all events from La Liga 2004/2005
    st.write("Loading all event data from La Liga 2004/2005...")
    laliga_0405_events = get_all_events_for_competition(LA_LIGA_0405_COMP_ID, LA_LIGA_0405_SEASON_ID)

    # Robustly find Messi's full name in the data
    if not laliga_0405_events.empty:
        st.success("✅ La Liga 2004/05 data loaded!")
        # Find all unique player names containing 'Messi' (case-insensitive)
        messi_names = laliga_0405_events['player_name'].dropna().unique()
        messi_names = [name for name in messi_names if 'messi' in name.lower()]
        if messi_names:
            messi_full_name = messi_names[0]  # Use the first match
            st.write(f"Found Messi's full name in data: **{messi_full_name}**")
            messi_data = laliga_0405_events[
                laliga_0405_events['player_name'] == messi_full_name
            ]
            st.write(f"Found {len(messi_data)} events for {messi_full_name} in the 2004/05 season.")
        else:
            st.warning("Could not find any player with 'Messi' in their name in this dataset.")
            messi_data = pd.DataFrame()
    else:
        st.warning("Could not load La Liga 2004/05 data.")
        messi_data = pd.DataFrame()


# --- Step 4: Analysis Function ---
st.subheader("⚙️ Step 4: Create Our Player Analysis Function")
st.write("This function will calculate key stats for any player's event data. We use 'per 90 minutes' stats to make a fair comparison, even if they played different amounts of time.")

with st.echo():
    def analyze_player(player_data, player_name):
        """Calculates key performance metrics for a player."""
        if player_data.empty:
            st.warning(f"No data for {player_name}, cannot analyze.")
            return None

        # --- Calculate Minutes Played ---
        # We estimate this by taking the highest minute recorded for the player in each match.
        minutes_played = player_data.groupby('match_id')['minute'].max().sum()
        if minutes_played == 0:
            return None # Avoid division by zero

        # This factor helps us scale stats to a "per 90 minutes" basis
        per_90_factor = 90 / minutes_played

        # --- Analyze Shots and Goals ---
        shots = player_data[player_data['type_name'] == 'Shot']
        goals = shots[shots['outcome_name'] == 'Goal']

        # --- Analyze Dribbles ---
        dribbles = player_data[player_data['type_name'] == 'Dribble']
        successful_dribbles = dribbles[dribbles['outcome_name'] == 'Complete']

        # --- Return a dictionary of stats ---
        stats = {
            "Player": player_name,
            "Minutes Played": minutes_played,
            "Goals": len(goals),
            "Shots": len(shots),
            "Goals per 90": len(goals) * per_90_factor,
            "Shots per 90": len(shots) * per_90_factor,
            "Dribbles per 90": len(dribbles) * per_90_factor,
            "Dribble Success (%)": (len(successful_dribbles) / len(dribbles) * 100) if len(dribbles) > 0 else 0
        }
        return stats

# --- Step 5: Run the Analysis ---
st.subheader("📊 Step 5: Analyze Both Players")
st.write("Now we'll use our function to analyze both Yamal and Messi.")

all_stats = []
if not yamal_data.empty:
    yamal_stats = analyze_player(yamal_data, "Lamine Yamal (Euro 2024)")
    if yamal_stats:
        all_stats.append(yamal_stats)
        st.success("✅ Lamine Yamal analyzed.")

if not messi_data.empty:
    messi_stats = analyze_player(messi_data, "Lionel Messi (La Liga '04/05)")
    if messi_stats:
        all_stats.append(messi_stats)
        st.success("✅ Lionel Messi analyzed.")

# --- Step 6: Compare and Visualize ---
st.subheader("📈 Step 6: The Comparison!")
st.write("With both players analyzed, we can now combine their stats into a single table and chart.")

if len(all_stats) == 2:
    # Create a DataFrame from our list of stats
    df_comparison = pd.DataFrame(all_stats)

    st.subheader("Comparison Table")
    st.dataframe(df_comparison.set_index("Player").round(2))

    # --- Visualization ---
    st.subheader("Visual Comparison")

    # We need to "melt" the DataFrame to make it easy to plot with Plotly Express
    df_melted = df_comparison.melt(
        id_vars='Player',
        value_vars=['Goals per 90', 'Shots per 90', 'Dribbles per 90'],
        var_name='Metric',
        value_name='Value'
    )

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
    st.info("Could not generate comparison because data for one or both players is missing.")

# --- Final Thoughts ---
coach_message = st.chat_message(name="Coach", avatar="⚽")
with coach_message:
    st.write("Amazing work, Shaun! You loaded data from two different competitions, processed "
             "it, and created a fair comparison. This is a top-tier skill in analytics.")
    st.write("**Key Takeaway:** The numbers give us clues, but they don't tell the whole story. "
             "A 17-year-old Yamal playing at the Euros is in a very different context than a "
             "young Messi breaking into a legendary Barcelona team. Your job as an analyst is "
             "to use the data to start the conversation, not end it.")
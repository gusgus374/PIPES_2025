"""
Copyright (c) 2024 DataRook Inc.

StatsBomb World Cup Data Analysis Module

This module provides comprehensive analysis of StatsBomb's free World Cup event data
for educational purposes. It demonstrates professional-grade soccer analytics using
event-level data from multiple World Cup tournaments.

Key Features:
- Multi-tournament support (2018/2022 Men's WC, 2019/2023 Women's WC)
- Player-friendly nickname display with robust ID mapping
- Professional radar chart comparisons with percentile rankings
- Advanced metrics: xG, progressive carries, key passes, danger passes
- Educational scaffolding with Coach Gus persona

Target Audience: Students aged 10-18 learning STEM through soccer analytics
Educational Level: Advanced/Reference (event-level data analysis)
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen, VerticalPitch, Radar, FontManager
import pandas as pd
#from sklearn.preprocessing import StandardScaler
from scipy import stats

st.title("Exploring World Cup data from StatsBomb")
st.subheader("Professional Soccer Analytics with Event-Level Data")

# Add cache clearing option for debugging
if st.button("🔄 Clear Cache (for debugging)", help="Clear all cached data and reload"):
    st.cache_data.clear()
    st.rerun()

# Add Coach Gus introduction
coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
with coach_message:
    st.write("Welcome to the world of professional soccer analytics! "
             "Today we're going to explore the same type of data that top clubs "
             "like Liverpool FC use to analyze player performance.")
    st.write("We'll be using StatsBomb's free World Cup data - this is "
             "**event-level data**, meaning we can see every single pass, shot, "
             "carry, and dribble that happened in the tournament!")

# Tournament Selection Interface
st.header("🏆 Select Tournament")

tournament_options = {
    "2022 FIFA World Cup (Qatar)": {
        "competition_id": 43,
        "season_id": 3
    },
    "2018 FIFA World Cup (Russia)": {
        "competition_id": 43,
        "season_id": 106
    },
    "2023 FIFA Women's World Cup (Australia/New Zealand)": {
        "competition_id": 72,
        "season_id": 107
    },
    "2019 FIFA Women's World Cup (France)": {
        "competition_id": 72,
        "season_id": 30
    }
}

selected_tournament = st.selectbox(
    "Choose a World Cup tournament to analyze:",
    list(tournament_options.keys()),
    index=0  # Default to 2022 World Cup
)

tournament_config = tournament_options[selected_tournament]
competition_id = tournament_config["competition_id"]
season_id = tournament_config["season_id"]

coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
with coach_message:
    st.write(f"Great choice! You've selected the **{selected_tournament}**. "
             "This tournament has some of the most exciting soccer data available!")
    st.write("Let's load the data and start our analysis...")

# Cache the StatsBomb data loading for better performance
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
def load_all_events_data(match_ids):
    """Load all event data for multiple matches with caching."""
    parser = Sbopen()
    all_events_df = pd.DataFrame()
    progress_bar = st.progress(0)

    for i, idx in enumerate(match_ids):
        try:
            df_game_events = parser.event(idx)[0]
            all_events_df = pd.concat([all_events_df, df_game_events], ignore_index=True)
        except Exception as e:
            st.warning(f"Could not load data for match {idx}: {e}")

        # Update progress bar
        progress_bar.progress((i + 1) / len(match_ids))

    progress_bar.empty()
    return all_events_df

@st.cache_data
def load_lineup_data(match_id):
    """Load lineup data for a specific match with caching."""
    try:
        parser = Sbopen()
        return parser.lineup(match_id)
    except Exception as e:
        st.error(f"Error loading lineup data for match {match_id}: {e}")

# Load tournament data
with st.spinner(f"Loading {selected_tournament} data..."):
    df_match = load_match_data(competition_id, season_id)

if df_match.empty:
    st.error("Could not load tournament data. Please try a different tournament.")
    st.stop()

st.success(f"✅ Successfully loaded {len(df_match)} matches from {selected_tournament}!")

# Display tournament info
with st.expander("📊 Tournament Information", expanded=False):
    st.write(f"**Tournament**: {selected_tournament}")
    st.write(f"**Total Matches**: {len(df_match)}")
    st.write(f"**Teams**: {len(set(df_match['home_team_name'].tolist() + df_match['away_team_name'].tolist()))}")

    # Show sample of match data
    st.subheader("Sample Matches")
    display_cols = ['match_date', 'home_team_name', 'away_team_name', 'home_score', 'away_score']
    available_cols = [col for col in display_cols if col in df_match.columns]
    if available_cols:
        st.dataframe(df_match[available_cols].head(10), use_container_width=True)
# Get available teams for this tournament
all_teams = sorted(set(df_match['home_team_name'].tolist() + df_match['away_team_name'].tolist()))

# Helper function to find available players
@st.cache_data
def get_all_tournament_players(df_match):
    """Get all players from the tournament with their IDs, names, and teams.

    This function loads lineup data from matches to build a comprehensive
    player database with nicknames. We use a robust sampling strategy to
    ensure we capture players from all teams in the tournament.

    Args:
        df_match: DataFrame containing match information for the tournament

    Returns:
        dict: player_id -> player_info dictionary containing:
            - player_id: Unique StatsBomb player identifier
            - player_name: Full official player name
            - player_nickname: Shorter, more user-friendly name
            - team_name: Team the player represents
    """
    try:
        match_ids = df_match["match_id"].tolist()
        all_players = {}  # player_id -> player_info
        teams_found = set()  # Track which teams we've found players for

        progress_bar = st.progress(0)
        st.write("Loading player database from lineup data...")

        # Get all unique teams from the match data
        all_teams = set(df_match['home_team_name'].tolist() + df_match['away_team_name'].tolist())

        # Strategy 1: Try to get at least one match per team
        # This ensures we don't miss major teams like Argentina
        team_matches = {}
        for _, match_row in df_match.iterrows():
            home_team = match_row['home_team_name']
            away_team = match_row['away_team_name']
            match_id = match_row['match_id']

            # Store first match for each team
            if home_team not in team_matches:
                team_matches[home_team] = match_id
            if away_team not in team_matches:
                team_matches[away_team] = match_id

        # Strategy 2: Add systematic sampling for broader coverage
        systematic_sample = match_ids[::3]  # Every 3rd match

        # Strategy 3: Add some random matches for additional coverage
        import random
        random.seed(42)  # For reproducible results
        additional_sample = random.sample(match_ids, min(10, len(match_ids)))

        # Combine all sampling strategies
        sample_matches = list(set(list(team_matches.values()) + systematic_sample + additional_sample))

        st.write(f"Sampling {len(sample_matches)} matches to ensure coverage of all {len(all_teams)} teams...")

        for i, match_id in enumerate(sample_matches):
            try:
                # Load lineup data which contains player_nickname
                df_lineup = load_lineup_data(match_id)
                if not df_lineup.empty:
                    # Lineup data has: player_id, player_name, player_nickname, team_name
                    required_cols = ['player_id', 'team_name']
                    if all(col in df_lineup.columns for col in required_cols):

                        for _, row in df_lineup.iterrows():
                            player_id = row['player_id']
                            team_name = row['team_name']
                            teams_found.add(team_name)  # Track teams we've found

                            if player_id not in all_players:
                                # Get nickname from lineup data (this is the key improvement!)
                                nickname = row.get('player_nickname', '')
                                full_name = row.get('player_name', 'Unknown')

                                # Prioritize nickname, but ensure it's not empty or just whitespace
                                if pd.notna(nickname) and str(nickname).strip():
                                    display_name = str(nickname).strip()
                                elif pd.notna(full_name) and str(full_name).strip():
                                    display_name = str(full_name).strip()
                                else:
                                    display_name = f'Player_{player_id}'

                                all_players[player_id] = {
                                    'player_id': player_id,
                                    'player_name': full_name,
                                    'player_nickname': display_name,  # This will be the friendly name!
                                    'team_name': team_name
                                }

                progress_bar.progress((i + 1) / len(sample_matches))

                # Early exit if we've found players for all teams
                if len(teams_found) >= len(all_teams):
                    st.write(f"✅ Found players for all {len(all_teams)} teams!")
                    break

            except Exception as e:
                # If lineup data fails, try to get basic info from event data
                try:
                    df_event = load_event_data(match_id)
                    if not df_event.empty and 'player_id' in df_event.columns:
                        player_cols = ['player_id', 'player_name', 'team_name']
                        available_cols = [col for col in player_cols if col in df_event.columns]

                        if 'player_id' in available_cols and 'team_name' in available_cols:
                            players_df = (df_event[available_cols]
                                         .dropna(subset=['player_id', 'team_name'])
                                         .drop_duplicates(subset=['player_id']))

                            for _, row in players_df.iterrows():
                                player_id = row['player_id']
                                team_name = row['team_name']
                                teams_found.add(team_name)

                                if player_id not in all_players:
                                    full_name = row.get('player_name', 'Unknown')
                                    all_players[player_id] = {
                                        'player_id': player_id,
                                        'player_name': full_name,
                                        'player_nickname': full_name,  # No nickname available from event data
                                        'team_name': team_name
                                    }
                except:
                    continue  # Skip this match entirely if both lineup and event data fail

        progress_bar.empty()

        # Report on coverage
        missing_teams = all_teams - teams_found
        if missing_teams:
            st.warning(f"⚠️ Could not find players for: {', '.join(sorted(missing_teams))}")
            st.write("This might be due to missing lineup data for some matches.")
        else:
            st.success(f"✅ Successfully found players for all {len(all_teams)} teams!")

        return all_players

    except Exception as e:
        st.error(f"Error loading tournament players: {e}")
        return {}

@st.cache_data
def get_players_by_team(all_players, team_name):
    """Get all players for a specific team."""
    team_players = {}
    for player_id, player_info in all_players.items():
        if player_info['team_name'] == team_name:
            team_players[player_id] = player_info
    return team_players

def get_player_data_by_id(df_match, player_id, team_name):
    """Extracts data from StatsBomb event dataframes for a given player ID and team.

    This function uses player_id for data retrieval, which is much more reliable
    than name-based matching. StatsBomb uses unique player IDs that don't change,
    while names can have variations (nicknames vs full names, spelling differences).

    Args:
        df_match: The StatsBomb match dataframe containing match information
        player_id: The unique StatsBomb player identifier (integer)
        team_name: The name of the player's team (used to filter relevant matches)

    Returns:
        pandas.DataFrame: Contains all events for the specified player across
                         all matches where their team played in this tournament
    """
    # Get all matches where the specified team played (home or away)
    match_ids = df_match.loc[(df_match["home_team_name"] == team_name)
                             | (df_match["away_team_name"] == team_name)]["match_id"].tolist()

    # Initialize an empty dataframe to store the player's events
    # We'll concatenate data from all matches
    player_df = pd.DataFrame()

    # Loop through each match where the team played
    for idx in match_ids:
        # Use cached event data loading for performance
        df_event = load_event_data(idx)

        # Check if we have valid event data and the player_id column exists
        if not df_event.empty and 'player_id' in df_event.columns:
            # Filter by player_id (most reliable method)
            # This avoids issues with name variations, special characters, etc.
            player_df_game = df_event[df_event['player_id'] == player_id]

            # Add any found data to the main dataframe
            if not player_df_game.empty:
                player_df = pd.concat([player_df, player_df_game], ignore_index=True)

    return player_df

# Load all tournament players
with st.spinner("Loading tournament player database..."):
    all_tournament_players = get_all_tournament_players(df_match)

if not all_tournament_players:
    st.error("Could not load player data for this tournament. Please try a different tournament.")
    st.stop()

st.success(f"✅ Loaded {len(all_tournament_players)} players from the tournament!")

# Debug: Show team distribution
with st.expander("🔍 Debug: Team Distribution", expanded=False):
    team_counts = {}
    for player_id, player_info in all_tournament_players.items():
        team = player_info['team_name']
        team_counts[team] = team_counts.get(team, 0) + 1

    st.write("**Teams found in player database:**")
    for team, count in sorted(team_counts.items()):
        st.write(f"- {team}: {count} players")

# Player and Team Selection
st.header("🎯 Select Player and Team")

# First, let user select team
# We use all available teams from the match data
selected_team = st.selectbox("Pick Team", all_teams)

# Get players for the selected team
# This filters our player database to only show players from the selected team
team_players = get_players_by_team(all_tournament_players, selected_team)

if not team_players:
    st.warning(f"No players found for {selected_team} in the loaded data.")
    st.info("This might be because the team didn't play in the sampled matches. Try selecting a different team.")

    # Debug: Show what teams we do have
    # This helps users understand what data is actually available
    available_teams = set()
    for player_info in all_tournament_players.values():
        available_teams.add(player_info['team_name'])

    st.write("**Available teams in player database:**")
    st.write(sorted(list(available_teams)))
    st.stop()

# Show available players for the selected team
# This expandable section lets users see all available players before selecting
with st.expander(f"🔍 Available players for {selected_team} ({len(team_players)} players)", expanded=False):
    st.write("Here are the players available in the data:")
    # Display in columns for better readability
    cols = st.columns(3)
    for i, (player_id, player_info) in enumerate(team_players.items()):
        # We show the nickname (user-friendly name) here
        display_name = player_info['player_nickname']
        cols[i % 3].write(f"• {display_name}")

# Create a user-friendly player selection mapping
# This maps the display names (nicknames) to the internal player IDs
# Users see friendly names like "Lionel Messi" instead of "Lionel Andrés Messi Cuccittini"
player_options = {}
for player_id, player_info in team_players.items():
    # Use the nickname we prepared earlier (which falls back to full name if needed)
    display_name = player_info['player_nickname']
    player_options[display_name] = player_id

if not player_options:
    st.error(f"No players available for {selected_team}")
    st.stop()

# Player selection dropdown
# Users see the friendly display names, but we store the reliable player_id
selected_player_display = st.selectbox(
    "Pick Player",
    list(player_options.keys()),  # Show the friendly nicknames
    help="Select a player from the available list"
)

# Get the corresponding player ID and info
# This is the reliable identifier we'll use for all data operations
selected_player_id = player_options[selected_player_display]
selected_player_info = all_tournament_players[selected_player_id]

# Load player data using the reliable player_id
# This ensures we get the correct player data regardless of name variations
with st.spinner(f"Loading data for {selected_player_display}..."):
    player_data = get_player_data_by_id(df_match, selected_player_id, selected_team)

if player_data.empty:
    st.error(f"❌ Could not find event data for {selected_player_display} in {selected_team}")
    st.info("This player might not have participated in any events in the available matches.")
    st.stop()
else:
    st.success(f"✅ Found {len(player_data)} events for {selected_player_display}")

# Update the player_dataframes for compatibility with existing code
player_dataframes = {selected_player_display: player_data}
players = [selected_player_display]
teams = [selected_team]

# Set selected_player for compatibility with existing code
selected_player = selected_player_display

def calculate_progressive_carries(player_df):
    """Calculates the progressive carries for a given player's dataframe.

    Args:
        player_df: The pandas dataframe containing the events for the player.

    Returns:
        The progressive carries dataframe.
    """
    if player_df.empty or 'type_name' not in player_df.columns:
        return pd.DataFrame()

    carries = player_df[player_df['type_name'] == 'Carry']
    if carries.empty or not all(col in carries.columns for col in ['x', 'end_x', 'y']):
        return pd.DataFrame()

    # Progressive carries are defined as carries that move the ball at least 5 yards towards the opponent's goal
    progressive_carries = carries[(carries['end_x'] - carries['x'] >= 5) & (carries['y'] <= 80) & (carries['y'] >= 20)]
    return progressive_carries

def calculate_key_passes(player_df):
    """Calculates the key passes for a given player's dataframe.

    Args:
        player_df: The pandas dataframe containing the events for the player.

    Returns:
        The key passes dataframe.
    """
    if player_df.empty or 'type_name' not in player_df.columns:
        return pd.DataFrame()

    passes = player_df[player_df['type_name'] == 'Pass']
    if passes.empty or 'pass_shot_assist' not in passes.columns:
        return pd.DataFrame()

    key_passes = passes[passes['pass_shot_assist'].notna() &
                       passes['pass_shot_assist']]
    return key_passes

def calculate_passes_into_penalty_area(player_df):
    """Calculates the number of passes into the penalty area for a given player's dataframe.

    Args:
        player_df: The pandas dataframe containing the events for the player.

    Returns:
        The number of passes into the penalty area.
    """
    if player_df.empty or 'type_name' not in player_df.columns:
        return 0

    passes = player_df[player_df['type_name'] == 'Pass']
    if passes.empty or not all(col in passes.columns for col in ['end_x', 'end_y']):
        return 0

    passes_into_penalty_area = passes[(passes['end_x'] >= 102) & (passes['end_y'] <= 62) & (passes['end_y'] >= 18)]
    return len(passes_into_penalty_area)

def calculate_shot_creating_actions(player_df):
    """Calculates the number of shot-creating actions for a given player's dataframe.

    Args:
        player_df: The pandas dataframe containing the events for the player.

    Returns:
        The number of shot-creating actions.
    """
    if player_df.empty or 'type_name' not in player_df.columns:
        return 0

    # Shot creating actions are defined as passes and dribbles that lead to a shot within two actions
    shots = player_df[player_df['type_name'] == 'Shot']
    if shots.empty or 'id' not in shots.columns or 'related_events' not in shots.columns:
        return 0

    shot_creating_actions = 0
    for shot_id in shots['id']:
        related_events = shots[shots['related_events'].apply(lambda x: shot_id in x if isinstance(x, list) else False)]
        if len(related_events[(related_events['type_name'] == 'Pass') |
                               (related_events['type_name'] == 'Dribble')]) > 0:
            shot_creating_actions += 1
    return shot_creating_actions

def calculate_xg_xa(player_df):
    """Calculates the xG and xA for a given player's dataframe.

    Args:
        player_df: The pandas dataframe containing the events for the player.

    Returns:
        A tuple containing the player's total xG and xA.
    """
    if player_df.empty or 'type_name' not in player_df.columns:
        return 0.0, 0.0

    shots = player_df[player_df['type_name'] == 'Shot']
    total_xg = 0.0
    if not shots.empty and 'shot_statsbomb_xg' in shots.columns:
        total_xg = shots['shot_statsbomb_xg'].fillna(0).sum()

    passes = player_df[player_df['type_name'] == 'Pass']
    total_xa = 0.0
    if not passes.empty and 'pass_goal_assist' in passes.columns:
        total_xa = passes['pass_goal_assist'].fillna(0).sum()

    return total_xg, total_xa

def calculate_minutes_played(player_df):
    """Calculates the total minutes played by a player in an event dataframe.

    Args:
        player_df: The pandas DataFrame containing the events for the player.

    Returns:
        The total minutes played by the player.
    """
    if player_df.empty:
        return 0

    # Group the dataframe by match ID
    matches = player_df.groupby('match_id')

    # Calculate minutes played in each match
    minutes_played = 0
    for idx, match_df in matches:
        # Find the last event for the player in the match
        last_event = match_df['minute'].max()
        # Add the minutes from the last event to the total minutes played
        minutes_played += last_event

    return minutes_played

# Get list of games by selected team
match_ids = df_match.loc[(df_match["home_team_name"] == selected_team) |
                        (df_match["away_team_name"] == selected_team)]["match_id"].tolist()
no_games = len(match_ids)

st.header("Important Actions")

coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
with coach_message:
    st.write("Let's calculate some advanced metrics for our players. "
             "These are the same types of statistics that professional analysts use!")

# Calculate player metrics
@st.cache_data
def calculate_player_metrics(player_dataframes):
    player_metrics = {}
    for player, df in player_dataframes.items():
        progressive_carries = calculate_progressive_carries(df)
        key_passes = calculate_key_passes(df)
        passes_into_penalty_area = calculate_passes_into_penalty_area(df)
        total_xg, total_xa = calculate_xg_xa(df)

        player_metrics[player] = {
            'Progressive Carries': len(progressive_carries),
            'Key Passes': len(key_passes),
            'Passes into Penalty Area': passes_into_penalty_area,
            'xG': total_xg,
            'xA': total_xa,
            'xG+xA': total_xg + total_xa
        }
    return player_metrics

player_metrics = calculate_player_metrics(player_dataframes)

# Display selected player's progressive carries
selected_player_data = get_player_data_by_id(df_match, selected_player_id, selected_team)
carries = calculate_progressive_carries(selected_player_data)

if not carries.empty:
    pitch = Pitch(line_color='black')
    fig2, ax2 = pitch.grid(grid_height=0.9, title_height=0.06, axis=False, endnote_height=0.04,
                            title_space=0, endnote_space=0)

    pitch.arrows(carries.x, carries.y, carries.end_x, carries.end_y, color="blue", ax=ax2['pitch'])
    pitch.scatter(carries.x, carries.y, alpha=0.2, s=500, color='blue', ax=ax2['pitch'])

    # Update title to reflect selected tournament
    tournament_short_name = selected_tournament.split('(')[0].strip()  # Remove location info
    plt.title(f"{selected_player_display} Progressive Carries in {tournament_short_name}")
    st.pyplot(fig2)
else:
    st.write(f"No progressive carries data available for {selected_player_display}")

# ... existing code for dangerous passes section ...

st.header("🎯 Player Comparison Radar Charts")

coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
with coach_message:
    st.write("Now for the really cool part - radar charts! "
             "These show how players compare to each other across multiple metrics.")
    st.write("We'll compare our selected players against all midfielders in the tournament. "
             "This is exactly how professional scouts analyze players!")

# Load all events data for midfielder analysis
@st.cache_data
def get_midfielder_data(df_match):
    """Get all midfielder data from the tournament for comparison.

    This function loads all event data and filters for players who play
    in midfield positions. It's used for radar chart comparisons.

    Args:
        df_match: DataFrame containing match information

    Returns:
        dict: player_nickname -> player_dataframe for all midfielders
    """
    match_ids = df_match["match_id"].tolist()
    all_events_df = load_all_events_data(match_ids)

    midfielder_dataframes = {}

    if not all_events_df.empty and 'player_id' in all_events_df.columns:
        # Check which columns are actually available in the events data
        # Not all StatsBomb datasets have the same columns
        required_cols = ['player_id', 'team_name']
        optional_cols = ['player_name', 'player_nickname', 'position_name']

        # Build list of available columns
        available_cols = required_cols.copy()
        for col in optional_cols:
            if col in all_events_df.columns:
                available_cols.append(col)

        # Only proceed if we have the minimum required columns
        if all(col in all_events_df.columns for col in required_cols):
            # Get unique players with their team info
            player_info_df = (all_events_df[available_cols]
                              .dropna(subset=required_cols)
                              .drop_duplicates(subset=['player_id']))

            # Filter for midfielders only if position data is available
            if 'position_name' in available_cols:
                midfielders = player_info_df[player_info_df['position_name'].str.contains('Midfield', na=False)]
            else:
                # If no position data, we can't filter for midfielders
                # Return empty dict to avoid errors
                st.warning("Position data not available - skipping midfielder analysis")
                return {}

            for _, row in midfielders.iterrows():
                player_id = row['player_id']
                team_name = row['team_name']

                # Use nickname if available, otherwise use full name, otherwise use player_id
                if 'player_nickname' in row and pd.notna(row['player_nickname']):
                    player_display_name = row['player_nickname']
                elif 'player_name' in row and pd.notna(row['player_name']):
                    player_display_name = row['player_name']
                else:
                    player_display_name = f'Player_{player_id}'

                # Get player data using ID (most reliable method)
                player_df = get_player_data_by_id(df_match, player_id, team_name)

                if not player_df.empty:
                    midfielder_dataframes[player_display_name] = player_df

    return midfielder_dataframes

# Calculate per-90 metrics for all midfielders
@st.cache_data
def calculate_midfielder_metrics_per90(midfielder_dataframes):
    """Calculate per-90 metrics for all midfielders."""
    midfielder_metrics_per90 = {}

    for player, df in midfielder_dataframes.items():
        minutes = calculate_minutes_played(df)
        if minutes > 0:  # Only include players with playing time
            progressive_carries_count = len(calculate_progressive_carries(df))
            key_passes_count = len(calculate_key_passes(df))
            passes_into_penalty_area_count = calculate_passes_into_penalty_area(df)
            total_xg, total_xa = calculate_xg_xa(df)

            # Calculate per-90 metrics
            midfielder_metrics_per90[player] = {
                'Progressive Carries': (progressive_carries_count / minutes) * 90,
                'Key Passes': (key_passes_count / minutes) * 90,
                'Passes into Penalty Area': (passes_into_penalty_area_count / minutes) * 90,
                'xG': (total_xg / minutes) * 90,
                'xA': (total_xa / minutes) * 90,
                'xG+xA': ((total_xg + total_xa) / minutes) * 90
            }

    return midfielder_metrics_per90

# Calculate per-90 metrics for our selected players
@st.cache_data
def calculate_selected_players_per90(player_dataframes):
    """Calculate per-90 metrics for our selected players."""
    player_metrics_per90 = {}

    for player, df in player_dataframes.items():
        minutes = calculate_minutes_played(df)
        if minutes > 0:
            progressive_carries_count = len(calculate_progressive_carries(df))
            key_passes_count = len(calculate_key_passes(df))
            passes_into_penalty_area_count = calculate_passes_into_penalty_area(df)
            total_xg, total_xa = calculate_xg_xa(df)

            player_metrics_per90[player] = {
                'Progressive Carries': (progressive_carries_count / minutes) * 90,
                'Key Passes': (key_passes_count / minutes) * 90,
                'Passes into Penalty Area': (passes_into_penalty_area_count / minutes) * 90,
                'xG': (total_xg / minutes) * 90,
                'xA': (total_xa / minutes) * 90,
                'xG+xA': ((total_xg + total_xa) / minutes) * 90
            }

    return player_metrics_per90

# Load midfielder data and calculate metrics
with st.spinner("Loading midfielder comparison data..."):
    midfielder_dataframes = get_midfielder_data(df_match)
    midfielder_metrics_per90 = calculate_midfielder_metrics_per90(midfielder_dataframes)
    player_metrics_per90 = calculate_selected_players_per90(player_dataframes)

# Calculate percentile ranks
@st.cache_data
def calculate_percentile_ranks(player_metrics_per90, midfielder_metrics_per90):
    """Calculate percentile ranks for players compared to all midfielders."""
    categories = ['Progressive Carries', 'Key Passes', 'Passes into Penalty Area', 'xG', 'xA', 'xG+xA']
    percentile_ranks = {}

    for metric in categories:
        # Get all midfielder values for this metric
        all_midfielder_values = [midfielder_metrics_per90[player][metric]
                               for player in midfielder_metrics_per90
                               if metric in midfielder_metrics_per90[player]]

        # Calculate percentile for each of our players
        for player in player_metrics_per90:
            if metric in player_metrics_per90[player]:
                percentile_ranks[player, metric] = stats.percentileofscore(
                    all_midfielder_values, player_metrics_per90[player][metric]
                )

    return percentile_ranks

percentile_ranks = calculate_percentile_ranks(player_metrics_per90, midfielder_metrics_per90)

# Radar chart plotting function
def plot_radar_chart(player, percentile_ranks, ax):
    """Plots a radar chart for a given player and their percentile rankings."""
    categories = ['Progressive Carries', 'Key Passes', 'Passes into Penalty Area',
                  'xG', 'xA', 'xG+xA']
    num_categories = len(categories)

    # Get values for this player
    values = [percentile_ranks.get((player, metric), 0) for metric in categories]
    values += values[:1]  # Complete the circle

    # Calculate angles for each axis
    angles = [n / float(num_categories) * 2 * np.pi for n in range(num_categories)]
    angles += angles[:1]

    # Plot the radar chart
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw axis labels
    ax.set_thetagrids(np.degrees(angles[:-1]), categories)

    # Set y-axis
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20th", "40th", "60th", "80th", "100th"], size=8)
    ax.grid(True)

    # Choose colors
    if player == 'Jude Bellingham':
        line_color = 'red'
        fill_color = 'red'
    else:
        line_color = 'blue'
        fill_color = 'blue'

    # Plot the data
    ax.plot(angles, values, linewidth=2, linestyle='solid', color=line_color)
    ax.fill(angles, values, color=fill_color, alpha=0.25)

    # Add title
    ax.set_title(f"{player}\nPer 90 Minutes vs All Midfielders", size=10, pad=20)

    return ax

# Create radar charts for selected players
st.subheader("Player Performance Radar Charts")

# Allow user to select multiple players for comparison
# First, create a list of all available players from the tournament
all_available_players = []
for player_id, player_info in all_tournament_players.items():
    display_name = player_info['player_nickname']
    team_name = player_info['team_name']
    # Format as "Player Name (Team)" for clarity
    player_option = f"{display_name} ({team_name})"
    all_available_players.append((player_option, player_id, display_name))

# Sort by player name for easier selection
all_available_players.sort(key=lambda x: x[0])

# Create the selection interface
st.write("**Select players to compare in radar charts:**")
st.write("💡 You can compare up to 4 players from any team in the tournament")

# Multi-select with the currently selected player as default
current_player_option = f"{selected_player_display} ({selected_team})"
if current_player_option in [opt[0] for opt in all_available_players]:
    default_selections = [current_player_option]
else:
    default_selections = []


selected_player_options = st.multiselect(
    "Choose players for radar comparison:",
    options=[opt[0] for opt in all_available_players],  # Show "Player (Team)" format
    default=default_selections,
    max_selections=4,
    help="Select 1-4 players to compare their performance metrics"
)

if selected_player_options:
    # Convert selected options back to player info
    selected_players_for_radar = []
    selected_player_ids = []

    for selected_option in selected_player_options:
        # Find the corresponding player info
        for player_option, player_id, display_name in all_available_players:
            if player_option == selected_option:
                selected_players_for_radar.append(display_name)
                selected_player_ids.append(player_id)
                break

    # Load data for all selected players
    radar_player_dataframes = {}
    for i, (display_name, player_id) in enumerate(zip(selected_players_for_radar, selected_player_ids)):
        # Find the team for this player
        player_team = all_tournament_players[player_id]['team_name']

        with st.spinner(f"Loading data for {display_name}... ({i+1}/{len(selected_players_for_radar)})"):
            player_df = get_player_data_by_id(df_match, player_id, player_team)
            if not player_df.empty:
                radar_player_dataframes[display_name] = player_df
            else:
                st.warning(f"No event data found for {display_name}")

    if radar_player_dataframes:
        # Calculate per-90 metrics for selected players
        radar_player_metrics_per90 = calculate_selected_players_per90(radar_player_dataframes)

        # Calculate percentile ranks for radar players
        radar_percentile_ranks = calculate_percentile_ranks(radar_player_metrics_per90, midfielder_metrics_per90)

        # Create subplot grid
        num_players = len(radar_player_dataframes)
        cols = min(2, num_players)
        rows = (num_players + 1) // 2

        fig, axes = plt.subplots(rows, cols, figsize=(12, 6*rows),
                                subplot_kw={'projection': 'polar'})

        # Handle single subplot case
        if num_players == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes if isinstance(axes, np.ndarray) else [axes]
        else:
            axes = axes.flatten()

        # Plot radar charts
        for i, player in enumerate(selected_players_for_radar):
            if i < len(axes):
                plot_radar_chart(player, radar_percentile_ranks, axes[i])

        # Hide unused subplots
        for i in range(num_players, len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        st.pyplot(fig)

        # Add explanation
        coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
        with coach_message:
            st.write("🎯 **How to read these radar charts:**")
            st.write("-Each point shows what percentile the player is in compared to ALL midfielders in the tournament")
            st.write("-100th percentile = best in tournament, 50th percentile = average")
            st.write("-The larger the colored area, the better the overall performance!")
            st.write("- This is exactly how pro scouts compare players across different leagues and competitions!")

        # Show comparison table
        st.subheader("📊 Selected Players Comparison")
        if radar_player_metrics_per90:
            comparison_df = pd.DataFrame(radar_player_metrics_per90).T
            st.dataframe(comparison_df, use_container_width=True)
    else:
        st.warning("No valid player data found for radar chart comparison.")
else:
    st.info("Please select at least one player to create radar charts.")

# ... rest of existing code ...

st.subheader("Forward Dribbles and Driving Runs")

st.subheader("Passing into Dangerous Areas")

with st.echo():
    # Declare an empty dataframe
    danger_passes = pd.DataFrame()
    danger_carries = pd.DataFrame()
    for idx in match_ids:
        # Open the event data from this game
        df = load_event_data(idx)
        team1, team2 = df.team_name.unique()
        if selected_team != team1:
            other_team = team1
        elif selected_team != team2:
            other_team = team2
        else:
            other_team = "Unknown"  # Fallback for edge cases

        if (selected_player_display in df['player_name'].unique() or
            selected_player_display in df.get('player_nickname',
                                             pd.Series()).unique()):
            # Try to find by nickname first, then by full name
            if 'player_nickname' in df.columns and selected_player_display in df['player_nickname'].unique():
                mask_player = (df.type_name == 'Pass') & (df.player_nickname == selected_player_display)
            else:
                mask_player = (df.type_name == 'Pass') & (df.player_name == selected_player_display)

            df_pass = df.loc[mask_player, ['x', 'y', 'end_x', 'end_y']]

            pitch = Pitch(line_color='black')
            fig1, ax1 = pitch.grid(grid_height=0.9, title_height=0.06,
                                  axis=False, endnote_height=0.04,
                                  title_space=0, endnote_space=0)

            pitch.arrows(df_pass.x, df_pass.y, df_pass.end_x, df_pass.end_y,
                        color="blue", ax=ax1['pitch'])

            pitch.scatter(df_pass.x, df_pass.y, alpha=0.2, s=500,
                         color='blue', ax=ax1['pitch'])
            ax1['title'].text(0.5, 0.5,
                             str(selected_player_display) + "'s passes against " + other_team,
                             ha='center', va='center', fontsize=30)
            st.pyplot(fig1)

        #prepare the dataframe of passes by team that were not throw-ins
        mask_team = (df.type_name == 'Pass') & (df.team_name == selected_team) & (df.sub_type_name!= "Throw-in")
        df_passes = df.loc[mask_team, ['x', 'y', 'end_x', 'end_y', 'player_name']]
        #get the list of all players who made a pass
        names = df_passes['player_name'].unique()

        #draw 4x4 pitches
        pitch = Pitch(line_color='black', pad_top=20)
        fig, axs = pitch.grid(ncols= 4, nrows= 4, grid_height= 0.85, title_height= 0.06, axis = False,
                               endnote_height=0.04, title_space=0.04, endnote_space=0.01)

        #for each player
        for name, ax, in zip(names, axs['pitch'].flat[:len(names)]):
            #put player name over the plot
            ax.text(60, -10, name, ha='center', va='center', fontsize=14)
            #take only passes by this player
            player_df = df_passes.loc[df_passes['player_name'] == name]
            #scatter
            pitch.scatter(player_df.x, player_df.y, alpha = 0.2, s = 50, color = "blue", ax=ax)
            #plot arrow
            pitch.arrows(player_df.x, player_df.y, player_df.end_x, player_df.end_y, color = "blue", ax=ax, width = 1)

        #we have more than enough pitches - remove them
        for ax in axs['pitch'][-1, 16 - (len(names)+2):]:
            ax.remove()

        #Another way to set title using mplsoccer
        axs['title'].text(0.5, 0.5, str(selected_team) + "'s passes against " + other_team, ha='center',
                           va = 'center', fontsize=30)
        st.pyplot(fig)

        for period in [1,2]:
            #keep only accurate passes by team that were not set pieces in this period
            mask_pass = (df.team_name == selected_team) & (df.type_name == "Pass") & (df.outcome_name.isnull()) & \
            (df.period == period) & (df.sub_type_name.isnull())
            mask_carry = (df.team_name == selected_team) & (df.type_name == "Carry") & (df.outcome_name.isnull()) & \
            (df.period == period) & (df.sub_type_name.isnull())
            #keep only necessary columns
            passes = df.loc[mask_pass, ["x", "y", "end_x", "end_y", "minute", "second", "player_name"]]
            carries = df.loc[mask_carry, ["x", "y", "end_x", "end_y", "minute", "second", "player_name"]]
            #keep only shots by team in this period
            mask_shot = (df.team_name == selected_team) & (df.type_name == "Shot") & (df.period == period)
            mask_highXGshot = (df.team_name == selected_team) & (df.type_name == "Shot") & \
            (df.shot_statsbomb_xg > 0.07) & (df.period == period)
            #keep only necessary columns
            shots = df.loc[mask_highXGshot, ["minute", "second"]]
            #convert time to seconds
            shot_times = shots['minute']*60+shots['second']
            shot_window = 15
            #find starts of the window
            shot_start = shot_times - shot_window
            #condition to avoid negative shot starts
            shot_start = shot_start.apply(lambda i: i if i>0 else (period-1)*45)
            #convert to seconds
            pass_times = passes['minute']*60+passes['second']
            carry_times = carries['minute']*60+carries['second']
            #check if pass is in any of the windows for this half
            pass_to_shot = pass_times.apply(lambda x: True in ((shot_start < x) & (x < shot_times)).unique())
            carry_to_shot = carry_times.apply(lambda x: True in ((shot_start < x) & (x < shot_times)).unique())

            #keep only danger passes
            danger_passes_period = passes.loc[pass_to_shot]
            danger_carries_period = carries.loc[carry_to_shot]
            #concatenate dataframe with a previous one to keep danger passes from the whole tournament
            danger_passes = pd.concat([danger_passes, danger_passes_period], ignore_index = True)
            danger_carries = pd.concat([danger_carries, danger_carries_period], ignore_index = True)

with st.echo():
    #plot pitch
    pitch = Pitch(line_color='black')
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False, endnote_height=0.04,
                          title_space=0, endnote_space=0)
    #scatter the location on the pitch
    pitch.scatter(danger_passes.x, danger_passes.y, s=100, color='blue', edgecolors='grey',
                   linewidth=1, alpha=0.2, ax=ax["pitch"])
    #plot arrows for carries
    pitch.arrows(danger_passes.x, danger_passes.y, danger_passes.end_x, danger_passes.end_y,
                  color = "blue", ax=ax['pitch'])
    pitch.arrows(danger_carries.x, danger_carries.y, danger_carries.end_x, danger_carries.end_y,
                  color = "red", ax=ax['pitch'])
    #add title
    fig.suptitle('Location of danger passes and carries with high XG by ' + selected_team, fontsize = 30)
    st.pyplot(fig)

st.subheader("Scoring Important Goals")

coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
with coach_message:
    st.write("🎯 **What we've learned today:**")
    st.write("- Event-level data gives us incredible insights into player performance")
    st.write("- We can track every action a player makes and see how it contributes to the team")
    st.write("- Professional clubs use this exact type of analysis to scout players and improve tactics")
    st.write("- You now have the tools to analyze soccer like the pros!")

st.header("Player Analysis Summary")
st.write(f"""
         ### Featured Analysis:
         - **Primary Player**: {selected_player_display} ({selected_team})
         - **Data Source**: StatsBomb's professional event-level data
         - **Analysis Type**: Individual performance metrics and comparative radar charts

         ### Key Features Demonstrated:
         - **Player-friendly names** loaded from lineup data (nicknames vs full official names)
         - **Multi-player radar comparisons** across the entire tournament
         - **Professional-grade metrics** used by top clubs for scouting and analysis
         - **Percentile rankings** against all midfielders in the tournament

         This analysis showcases how modern soccer analytics can reveal detailed insights
         about player performance using the same data that professional clubs use for
         scouting, tactical analysis, and player development.
         """)

# Display summary metrics table
st.subheader("📊 Player Metrics Summary")
if player_metrics:
    metrics_df = pd.DataFrame(player_metrics).T
    st.dataframe(metrics_df, use_container_width=True)

coach_message = st.chat_message(name="Coach Gus", avatar="./media/profile_coachGus.JPG")
with coach_message:
    st.write("🚀 **Next Steps:**")
    st.write("- Try changing the selected player and team to explore different playing styles")
    st.write("- Look at how the radar charts change for different positions")
    st.write("- Think about how these metrics might apply to analyzing your own GPS data!")
    st.write("- Remember: this is the same type of analysis used by top clubs around the world!")

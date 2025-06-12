# Shaun's Tutorial Session Instructions

## Files Created
1. **`shaun_tutorial.py`** - Complete step-by-step tutorial with player comparison framework
2. **`shaun_simple_starter.py`** - Simplified template for his to work on
3. **`shaun_instructions.md`** - This file (instructor notes)

## Session Structure (90 minutes)

### Phase 1: Tutorial Walkthrough (30 minutes)
- Run `streamlit run shaun_tutorial.py`
- Walk through the player analysis framework
- Focus on understanding these concepts:
  - Individual player data extraction from tournament data
  - Per-90 minute statistics for fair comparison
  - Fuzzy player name matching (handling variations)
  - Player-specific vs team-level analysis

### Phase 2: Independent Work (45 minutes)
- Give him `shaun_simple_starter.py` to copy into his `shaun.py` file
- He works through the TODOs independently
- You provide guidance when needed
- Key learning objectives:
  1. Understanding player-specific data filtering
  2. Calculating meaningful individual metrics
  3. Creating fair comparisons across tournaments
  4. Building comparative visualizations

### Phase 3: Personalization (15 minutes)
- Help him focus on Lamine Yamal vs Messi comparison
- Add insights about what makes each player special
- Practice explaining findings for tomorrow's presentation

## Key Player Analysis Concepts to Emphasize

1. **Player Data Extraction**:
   ```python
   # Fuzzy matching for player names
   player_events = events[events['player_name'].str.contains(player_name, case=False, na=False)]
   ```

2. **Per-90 Minute Statistics**:
   - Fair comparison across different playing time
   - Standard metric in professional scouting
   - Formula: `(stat_total / minutes_played) * 90`

3. **Key Metrics for Attackers**:
   - Goals per 90 (productivity)
   - Shots per 90 (attacking involvement)
   - Dribbles per 90 (creativity/style)
   - Pass completion % (technical ability)

4. **Comparison Framework**: Individual performance → Standardized metrics → Visual comparison

## Data Strategy Notes
- **Primary**: Euro 2024 for Lamine Yamal data (competition_id: 55, season_id: 182)
- **Primary**: La Liga Barcelona data for young Messi (competition_id: 11, season_id: 37)
- **Alternative**: 2022 World Cup for mature Messi comparison
- **Alternative**: 2018 World Cup for different era comparison
- **Perfect Match**: This gives Yamal vs young Messi - much better for generational comparison!

## Common Issues to Watch For
- Player name variations (e.g., "Lionel Messi" vs "L. Messi")
- Code includes fuzzy matching to handle this
- Minutes calculation is estimated from last event per match
- Some players may not appear in certain tournaments
- Help him understand why per-90 stats are crucial for fair comparison

## Presentation Prep - Key Questions to Address
1. **What question are you answering?**
   - "How does Lamine Yamal's style compare to Messi's?"

2. **What makes this analysis valuable?**
   - Individual player scouting techniques
   - Fair comparison across different eras/tournaments

3. **Key findings to highlight:**
   - Efficiency differences (goals per shot)
   - Playing style differences (dribbling vs passing)
   - What makes each player unique

4. **What he learned:**
   - Professional scouting analysis techniques
   - How to standardize comparisons
   - Individual vs team analysis approaches

## Extension Ideas (if he finishes early)
- Add more metrics (key passes, progressive carries)
- Age-adjusted analysis (performance per age)
- Tournament progression analysis (how performance changed)
- Position heat map analysis
- Pressure situation analysis

## Success Metrics
By the end, Shaun should be able to:
- Extract individual player data from tournament datasets
- Calculate and explain per-90 minute statistics
- Create meaningful comparisons between players from different contexts
- Explain what makes each player's style unique
- Present findings about generational talent comparison

## Technical Learning Goals
- **Data filtering**: Player-specific extraction from large datasets
- **Statistical normalization**: Per-90 calculations for fair comparison
- **Comparative analysis**: Building side-by-side metrics
- **Visualization**: Creating clear comparison charts
- **Professional insight**: Understanding what scouts look for in players

## Coaching Points
- Emphasize that numbers don't tell the whole story
- Help him understand context (different tournaments, eras, team styles)
- Focus on what makes each player special, not just who's "better"
- This is the same type of analysis used by professional clubs for scouting
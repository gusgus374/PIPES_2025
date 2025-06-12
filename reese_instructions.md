# Reese's Tutorial Session Instructions

## Files Created
1. **`reese_tutorial.py`** - Complete step-by-step tutorial with explanations
2. **`reese_simple_starter.py`** - Simplified template for her to work on
3. **`reese_instructions.md`** - This file (instructor notes)

## Session Structure (90 minutes)

### Phase 1: Tutorial Walkthrough (30 minutes)
- Run `streamlit run reese_tutorial.py`
- Walk through each step together
- Let her see the full pipeline working
- Focus on understanding these concepts:
  - Loading data from StatsBomb
  - Filtering for shots and goals
  - Grouping by player vs. grouping by team
  - Using pandas functions: `.sum()`, `.max()`, `.min()`, `.mean()`

### Phase 2: Independent Work (45 minutes)
- Give her `reese_simple_starter.py` to copy into her `reese.py` file
- She works through the TODOs independently
- You provide guidance when needed
- Key learning objectives:
  1. Understanding data grouping (player → team aggregation)
  2. Using pandas aggregate functions
  3. Creating visualizations
  4. Drawing conclusions from data

### Phase 3: Personalization (15 minutes)
- Help her customize the styling/colors
- Add her own insights to the conclusions section
- Practice explaining her findings for tomorrow's presentation

## Key Pandas Concepts to Emphasize

1. **`.groupby()`** - Like making categories
   ```python
   player_stats = data.groupby('player_name')  # Group by player
   team_stats = player_stats.groupby('team_name')  # Then group by team
   ```

2. **Aggregation functions**:
   - `.sum()` - Add up all values (perfect for counting goals)
   - `.count()` - Count number of items (perfect for counting shots)
   - `.mean()` - Average value
   - `.max()` - Highest value
   - `.min()` - Lowest value

3. **Data pipeline**: Individual events → Player stats → Team stats

## Common Issues to Watch For
- StatsBomb API can be slow - remind her about caching
- **Column names verified**: All column references use official StatsBomb schema:
  - `outcome_name` (for shot outcomes like 'Goal')
  - `type_name` (for event types like 'Shot')
  - `player_name`, `team_name`, `shot_statsbomb_xg`
- Help her understand the difference between counting shots vs. summing goals
- Code includes error handling for potentially missing columns

## Presentation Prep
Help her prepare to explain:
1. What question she answered
2. How she got the data (StatsBomb)
3. The steps: events → players → teams
4. Her key findings
5. What she learned about data science

## Extension Ideas (if she finishes early)
- Add shooting percentage analysis
- Compare men's vs women's tournaments
- Look at individual player efficiency
- Add more visualization types

## Success Metrics
By the end, she should be able to:
- Explain what groupby does in simple terms
- Use basic pandas functions confidently
- Describe her data pipeline
- Present clear findings about which teams scored most goals
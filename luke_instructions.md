# Instructor Notes: Luke's Project - Money Makes the Ball Go Round

## Session Structure
1. **Introduction**
   - Discuss the role of money in soccer and why salary data is interesting.
   - Introduce the ASA API and itscalledsoccer Python package.
2. **Data Loading**
   - Guide students to use the API to get salary, player, and goals data.
3. **Data Merging & Cleaning**
   - Merge dataframes on player_id.
   - Calculate player age from birth_date.
   - Filter for players with both salary and goals data.
4. **Visualization 1: Goals vs Salary**
   - Scatter plot with regression line.
   - Discuss what a regression line means.
5. **Visualization 2: Salary vs Age**
   - Bar graph of average salary by age.
   - Discuss trends and outliers.
6. **Discussion & Wrap-up**
   - What did we learn? What are the limitations?
   - Encourage students to try other variables (e.g., assists, xG).

## Key Concepts
- Using a soccer analytics API (ASA, itscalledsoccer)
- Merging and cleaning real-world data
- Calculating age from birth date
- Scatter plots and regression lines (interpreting relationships)
- Bar charts for group comparisons
- Data interpretation: correlation does not imply causation

## Teaching Tips
- If students get API errors, check their internet connection and package installation.
- Encourage students to look at the dataframes with `st.write()` or `st.dataframe()` to understand the data.
- Remind students that salary is influenced by many factors (not just goals): experience, position, marketability, etc.
- For advanced students: try log-scaling salary, or look at other performance metrics.

## References
- [ASA API Docs: get_mls_players_salaries](https://app.americansocceranalysis.com/api/v1/__docs__/#/Major%20League%20Soccer%20(MLS)/get_mls_players_salaries)
- [itscalledsoccer Python Reference](https://american-soccer-analysis.github.io/itscalledsoccer/reference/)
- `2_US_Pro_Soccer.py` (provided by instructor)
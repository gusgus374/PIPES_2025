import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from itscalledsoccer.client import AmericanSoccerAnalysis
from sklearn.linear_model import LinearRegression

st.title("Hello Visitor!")

st.subheader("This is Luke's Page. home to the best info and worst code")


if st.button("this does nothing"):
   st.write("you should have believed me")


food_lover = st.checkbox("I like food")
if food_lover:
    st.write("I hope so")
fav_meal = st.select_slider("select your favorite meal", options= ["breakfast", "second breakfast", "elevenzies", "brunch", "lunch", "tea time", "dinner" ,"supper", "bed time snack", "midnight snack"],)
st.write("my favorite meal is", fav_meal )


st.title(":green[Money Makes the Ball Go Round]")
st.header("MLS Player Value: Salary vs. Performance")

# --- Step 1: Load Data ---
st.subheader("Step 1: Load MLS Salary and Performance Data")
st.write("We'll use the American Soccer Analysis API to get player salary and goals data for the most recent MLS season.")
with st.expander("Click to see the code"):
    with st.echo():
        asa = AmericanSoccerAnalysis()
        # Get all MLS data (all seasons) - get individual season stats, not cumulative
        salary_df = asa.get_player_salaries(leagues="mls")
        players_df = asa.get_players(leagues="mls")

        # Get all seasons of goals data - this will give us individual season stats
        all_seasons = ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013"]
        goals_dfs = []

        for season in all_seasons:
            try:
                season_goals = asa.get_player_xgoals(leagues="mls", season_name=season)
                season_goals['season_name'] = season  # Add season column
                goals_dfs.append(season_goals)
            except:
                # Skip seasons that don't have data
                continue

        # Combine all seasons
        goals_df = pd.concat(goals_dfs, ignore_index=True)
        teams_df = asa.get_teams(leagues="mls")

        # Clean the team_id column immediately after loading
        goals_df['team_id'] = goals_df['team_id'].apply(lambda x: ','.join(map(str, x)) if isinstance(x, list) else str(x))

        # Ensure season_name columns have the same data type (string) for merging
        salary_df['season_name'] = salary_df['season_name'].astype(str)
        goals_df['season_name'] = goals_df['season_name'].astype(str)
        players_df['season_name'] = players_df['season_name'].astype(str)

# --- Step 2: Merge Data ---
st.subheader("Step 2: Merge Salary and Goals Data")
st.write("We'll merge the salary, player info, and goals data into one DataFrame, keeping each player's data for every season they played.")

with st.expander("Click to see the code"):
    with st.echo():
        # Step 1: Merge salary and goals data (both have season info)
        merged = pd.merge(salary_df, goals_df, on=["player_id", "team_id", "season_name"], how="inner")

        # Step 2: Add player info (name, birth_date, etc.)
        # Filter players_df to match the seasons we have in our merged data
        player_info = players_df.groupby('player_id').last().reset_index()
        merged = pd.merge(merged, player_info[["player_id", "player_name", "birth_date"]], on="player_id", how="left")

        # Step 3: Add team names
        team_id_to_name = dict(zip(teams_df['team_id'], teams_df['team_name']))
        merged['team_name'] = merged['team_id'].map(team_id_to_name)

        # Step 4: Calculate age for each season
        # Convert birth_date to datetime
        merged["birth_date"] = pd.to_datetime(merged["birth_date"], errors="coerce")
        # For each season, calculate age at the start of that season (assuming seasons start in March)
        merged["season_start_date"] = pd.to_datetime(merged["season_name"].astype(str) + "-03-01")
        # Calculate age in days first, then convert to years, handling NaN values
        age_days = (merged["season_start_date"] - merged["birth_date"]).dt.days
        merged["age_in_season"] = (age_days / 365.25).round()
        # Only convert to int where we have valid ages (not NaN)
        merged["age_in_season"] = merged["age_in_season"].where(merged["age_in_season"].notna(), None)
        merged["age_in_season"] = merged["age_in_season"].astype('Int64')  # Use nullable integer type

        # Step 5: Clean up columns and remove rows with missing data
        merged = merged[["player_name", "team_name", "season_name", "base_salary", "guaranteed_compensation",
                        "birth_date", "age_in_season", "xgoals", "goals"]]
        merged = merged.dropna(subset=["base_salary", "goals", "age_in_season"])

st.write(f"Final dataset has {len(merged)} player-seasons (each row is one player in one season)")
st.write("Sample of the data:")
#st.dataframe(merged.head(10))

# --- Step 3: Visual 1 - Goals vs Salary ---
st.subheader("Step 3: Do Higher-Paid Players Score More Goals?")
st.write("Let's plot goals vs. salary and fit a regression line.")
# --- Explanation of Linear Regression ---
st.subheader("Understanding Linear Regression")
st.write("""
Linear regression is a method used to model the relationship between two variables by fitting a straight line to the data points. The equation of a straight line can be expressed as:
""")
st.latex(r'y = mx + b')

st.write("""
Where:
- \\( y \\) is the dependent variable (the outcome we want to predict, e.g., goals scored).
- \\( x \\) is the independent variable (the predictor, e.g., salary).
- \\( m \\) is the slope of the line, which indicates how much \\( y \\) changes for a one-unit change in \\( x \\).
- \\( b \\) is the y-intercept, which is the value of \\( y \\) when \\( x = 0 \\).

### How It Works

1. **Data Points**: We start with a set of data points, each representing a pair of values for \\( x \\) and \\( y \\).
2. **Best Fit Line**: The goal of linear regression is to find the line that best fits these data points. This line minimizes the distance (or error) between the actual data points and the predicted values on the line.
3. **Slope Interpretation**: The slope \\( m \\) tells us how much we expect \\( y \\) to increase (or decrease) when \\( x \\) increases by one unit. For example, if \\( m = 0.5 \\), it means that for every additional dollar in salary, we expect the number of goals scored to increase by 0.5.
""")
with st.echo():
    # Scatter plot with regression line using Altair
    X = merged[["base_salary"]].values
    y = merged["goals"].values
    reg = LinearRegression().fit(X, y)
    merged["predicted_goals"] = reg.predict(X)

    # Create scatter plot with regression line
    scatter = alt.Chart(merged).mark_circle().encode(
        x=alt.X('base_salary', title='Base Salary ($)', scale=alt.Scale(type='log')),
        y=alt.Y('goals', title='Goals'),
        tooltip=['player_name', 'team_name', 'base_salary', 'goals','season_name', 'age_in_season']
    )

    line = alt.Chart(merged).mark_line(color='red').encode(
        x='base_salary',
        y='predicted_goals'
    )

    chart1 = (scatter + line).properties(
        title='MLS: Goals vs. Salary',
        width=600,
        height=400
    ).interactive()

    st.altair_chart(chart1, use_container_width=True)
    st.write(f"Regression slope: {reg.coef_[0]:.4f} goals per $1 salary")

# --- Step 4: Visual 2 - Salary vs Age ---
st.subheader("Step 4: How Does Salary Vary by Age?")
st.write("Now let's see how salary changes with player age.")

with st.echo():
    # Bar graph: average salary by age using Altair
    age_salary = merged.groupby("age_in_season")["base_salary"].mean().reset_index()

    chart2 = alt.Chart(age_salary).mark_bar().encode(
        x=alt.X('age_in_season:Q', title='Age'),
        y=alt.Y('base_salary:Q', title='Average Base Salary ($)'),
        tooltip=['age_in_season', 'base_salary']
    ).properties(
        title='MLS: Average Salary by Age',
        width=600,
        height=400
    ).interactive()

    st.altair_chart(chart2, use_container_width=True)

# --- Step 5: Summary ---
st.subheader("Summary & Discussion")
st.write("""
- We used real MLS salary and performance data.
- We found a (weak/strong?) relationship between salary and goals.
- Salary tends to (increase/decrease) with age, but there are exceptions.
- Remember: Salary isn't just about goals! Experience, position, and marketability matter too.
""")

#st.info("Try changing the code to look at other stats, or compare different leagues!")

# End of tutorial

# References:
# - https://app.americansocceranalysis.com/api/v1/__docs__/#/Major%20League%20Soccer%20(MLS)/get_mls_players_salaries
# - https://american-soccer-analysis.github.io/itscalledsoccer/reference/
# - 2_US_Pro_Soccer.py (provided by instructor)
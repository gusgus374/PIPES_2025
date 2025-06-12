# Shaun's Tutorial Session Instructions

## Files Created
1. **`shaun_tutorial.py`** - A complete, simplified tutorial on cross-competition analysis.
2. **`shaun_simple_starter.py`** - A focused starter template for Shaun to complete.
3. **`shaun_instructions.md`** - This file (instructor notes).

## Session Goal: Cross-Competition Analysis
The main goal is to teach Shaun how to compare two players from **different datasets**. This is a more advanced and realistic data science scenario than comparing players within the same file.

**Core Question:** How does Lamine Yamal's performance at Euro 2024 compare to a young Lionel Messi's during the 2004/2005 La Liga season?

## Session Structure (90 minutes)

### Phase 1: Understanding the Concept (20 minutes)
- **Problem:** We have two players in two separate competitions. We can't just filter one file.
- **Solution:**
  1. Load the Euro 2024 dataset.
  2. Isolate all of Yamal's events.
  3. Load the La Liga 2004/05 dataset.
  4. Isolate all of Messi's events.
  5. Analyze each player's data *separately*.
  6. Combine the final, summarized stats for comparison.
- Walk through `shaun_tutorial.py` to demonstrate this workflow.

### Phase 2: Independent Work (50 minutes)
- Give him `shaun_simple_starter.py` to copy into his `shaun.py` file.
- Shaun's task is to fill in the `TODO` sections. This reinforces the logic:
  - Defining the correct IDs.
  - Calculating the key stats in the `analyze_player` function.
  - Combining the final stats into a comparison DataFrame.
  - Building the final visualization.
- This is a less complex but more conceptually important task.

### Phase 3: Analysis and Storytelling (20 minutes)
- Once the code works, shift focus to the "so what?"
- Help him interpret the comparison table and chart.
- Discuss the context (Euros vs. La Liga, team quality, player age).
- Help him write his "Hot Take" and practice explaining his findings for the presentation.

## Key Data Science Concepts to Emphasize

1.  **Handling Disparate Data Sources:** This is the core lesson. Emphasize that in the real world, data rarely comes in one clean file. The process of loading, filtering, and standardizing data from different sources is fundamental.

2.  **Per-90-Minute Statistics:** Reinforce why this is crucial for a fair comparison. Yamal and Messi will have played different numbers of minutes, so raw totals (like total goals) are misleading.

3.  **Data "Melting" for Visualization:** Briefly explain the concept of converting a "wide" DataFrame into a "long" one to make it compatible with plotting libraries like Plotly Express.
    -   **Wide:** One row per player, one column per metric.
    -   **Long:** One row per observation (e.g., one row for Yamal's "Goals per 90", another for Messi's).

## Correct Data IDs
-   **Lamine Yamal (Euro 2024):**
    -   `competition_id = 55`
    -   `season_id = 282`
-   **Lionel Messi (La Liga 2004/05):**
    -   `competition_id = 11`
    -   `season_id = 37`

## Presentation Prep
Help Shaun structure his story:
1.  **The Question:** "I wanted to compare a modern prodigy, Lamine Yamal, to a young legend, Lionel Messi, to see how they stack up."
2.  **The Challenge:** "They never played in the same competition at that age, so I had to pull data from two different seasons: Euro 2024 and La Liga 2004/05."
3.  **The Method:** "I loaded both datasets, isolated each player, calculated their 'per 90 minute' stats to be fair, and then combined them."
4.  **The Findings:** "My chart shows that..." (He explains the visual).
5.  **The "Hot Take":** "While Player X was better at..., Player Y excelled at... This shows that..." (He adds his own context and analysis).

This narrative is much more compelling than just showing a chart. It tells the story of his data science process.
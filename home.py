import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import time
import numpy.random as rnd


with st.echo(code_location="below"):
    import streamlit as st
    import pandas as pd
    import altair as alt
    import streamlit.components.v1 as components
    st.title("Welcome to our 2025 UTK PIPES Soccer Data Science App!")

    st.image("./resources/hard_at_work.jpeg",width=600)


    st.header("Soccer... and Data... *and* Science?")
    st.subheader("One of the biggest soccer clubs in the world, Liverpool FC, hired particle physicists to help improve their soccer team")

    col1, col2 = st.columns(2)
    col1.write("They used their knowledge of this:")
    col2.write("And combined it with soccer data to create this (known as the Pitch Control model):")
    with col2:
        iframe_src2 = "https://www.youtube.com/embed/Nc3uFWnPlsQ?si=pUx4ouf0EhWYMrVE"
        components.iframe(iframe_src2,600,500)

    with col1:
        iframe_src = "https://phet.colorado.edu/sims/html/charges-and-fields/latest/charges-and-fields_en.html"
        components.iframe(iframe_src,height=500)
        st.caption("Hint: make sure to click the 'Voltage' checkbox then drag and drop the red and blue particels around")
    st.subheader("Soccer and Science.")
    st.header("What about that data thing? What *is* data?")
    st.write("Well first we collect information like: 'What is your hobby? 'Where do you go to school?' 'What is your favorite sport?' 'What do you want to study?'")
    st.write("and then we organize it!")

    #data_def = "A single measurable piece of information. IDK. Only way to compare a certain instance with another. "
    data_def = "A bunch of information that we can compare and analyze. It is sometimes quantitative and sometimes qualitative."
    st.header(f"Maybe :red[data] is... {data_def}")
    campers_info = {
    'Name':['Luke', 'Shaun', 'Reese'],
    'Favorite Subject':['Math', 'History', 'Math'],
    'Educational Interest':['Engineering','Kiniseology','Animal Biology'],
    'Hobby':["Lifting", "Soccer", "Reading"],
    'Favorite Sport':["Football", "Soccer", "Soccer"],
    'Favorite Food':["NY Pizza/Stir Fry", "NY Strip Steak", "Chik-Fil-a"],
    'Grade Level': [12,12,11],
    'Career Interest':["Whatever makes money", "Athletic Trainer", "Large Animal Vet"],
    'Current School':["Sweetwater", "Sequoyah", "Sequoyah"],
    'Favorite Number':[4, 10, 15]
    }
    campers_db = pd.DataFrame(data=campers_info)
    st.dataframe(campers_db)

    st.header("So, Data is a *Collection* of *Structured* *Information*")

    st.header("Okay, so I know what Soccer is but what do we mean by ''Data Science''?")

    st.image("./resources/datascience.png")

    st.header("Hacking Skills = ~Computer Programming~ *Magic*")
    iframe_src2 = "https://www.youtube.com/embed/Qgr4dcsY-60?si=gsK8I_rpz0cpH5UO"
    components.iframe(iframe_src2,400,300)
    st.header("We will be exploring some soccer data with...")
    st.subheader("Magic.")
    st.markdown("Well... actually just writing some *python code*... which feels like magic, I promise.")

    st.markdown("In fact, everything you are currently seeing on the screen was written using python code!!!. Have a look for youself:")

st.subheader("See? Magic.")
coach_message = st.chat_message(name="Coach Gus",avatar="./resources/profile_coachGus.JPG")
coach_message.write("Now I'm going to ``cast a spell`` (:wink:) to generate a button:")

st.code("""
        #this spell is actually just python code
st.button("I'm a Button")
        """)
st.button("I'm a Button")

coach_message = st.chat_message(name="Coach Gus",avatar="./resources/profile_coachGus.JPG")
coach_message.write("Okay cool! We can click on our newly casted button but... that's about it. Let's try a slightly more advanced spell:")

st.code("""
if st.button("Click me for a celebration"):
        st.balloons()
        """)

if st.button("Click me for a celebration"):
        st.balloons()

st.write("Using our magic analogy, we borrow some *spells* from our *spellbooks*:")
st.code("""
        import streamlit as st
        import pandas as pd
        """)
st.write('streamlit and pandas are just some of the spellbooks we will use. This is just python code other people have written and kindly made available for others to use. No need to reinvent the wheel right?')
st.caption('(instead of "spellbook" the technical term for the word after "import" is a **python library**)')

st.header("Soccer Data Science")
st.write("Looking back at the Venn Diagram above, Data Science is Hacking Skills + Substantive Expertise + Math & Statistics Knowledge ")
st.write("Let's define these terms in our own words")
st.write("**:red[Hacking Skills]** = making the computer do stuff with code")
st.write("**:blue[Substantive Expertise]** = Deep knowledge about a specific topic, like the game of soccer")
st.write("**:green[Math and Statistics Knowledge]** = The ability to analyze things using mathematical tools")

st.divider()

st.subheader('Explore some data with us!')

st.page_link("./luke.py", label="Mo' money mo' goals?")
st.page_link("./shaun.py", label="Young Messi vs. Lamine Yamal")
st.page_link("./reese.py", label="Best attack in the world?")


st.divider()
st.divider()
st.header("Simulating goals scored in a professional match")
#minutes in a match
match_minutes = 90

st.write(f"There are :red[{match_minutes} minutes] in a full-length soccer game")

#average goals per match
goals_per_match = 2.79
st.write(f"The average total goals scored is :red[{goals_per_match}] per game")
#probability of a goal per minute
prob_per_minute = np.array(goals_per_match/match_minutes)

st.metric("The probability of a goal per minute is", prob_per_minute)

with st.popover("Let's play simulate a game"):
    if st.button("run simulation"):
        goals = 0

        for minute in range(match_minutes):
            #generate a random number
            r=rnd.rand(1,1)

            if (r < prob_per_minute):
                #Goal - if the random number is less than the goal probability
                st.write('minute ' + str(minute) + ': :partying_face:')
                goals = goals + 1
                time.sleep(0)
            else:
                st.write('minute ' + str(minute) + ': :no_entry:')
                time.sleep(0.1)
        st.write("Final whistle. \n \nThere were " + str(goals) + ' goals.')
        st.subheader("What if we ran this for 380 games?")

def simulateMatch(time, prob):
    # time - number of time units
    # prob - probability per time unit of a goal
    # display_match == True then display simulation output for match.

    # Count the number of goals
    goals = 0

    for minute in range(time):
        # Generate a random number between 0 and 1.
        r = rnd.rand(1, 1)
        # Prints an X when there is a goal and a zero otherwise.
        if (r < prob):
            # Goal - if the random number is less than the goal probability.
            goals = goals + 1

    return goals

# Number of matches
num_matches = 380

# Loop over all the matches and print the number of goals.
goals = np.zeros(num_matches)
for i in range(num_matches):
    goals[i] = simulateMatch(match_minutes, prob_per_minute)
    time.sleep(0.1)


# Create a histogram

# Convert goals array to a DataFrame for Altair
goals_df = pd.DataFrame({'goals': goals})

# Create the Altair histogram
chart = alt.Chart(goals_df).mark_bar(
    color='white',
    stroke='black',
    strokeWidth=1,
    opacity=0.8
    ).encode(
    x=alt.X('goals:O',
    title='Number of goals',
    scale=alt.Scale(domain=list(range(11))),
    axis=alt.Axis(values=list(range(11)))
    ),
    y=alt.Y('count():Q',
    title='Number of matches',
    scale=alt.Scale(domain=[0, 100]),
    axis=alt.Axis(values=list(range(0, 101, 20)))
    )
    ).properties(width=600,height=400).resolve_scale(y='independent'
)

with st.expander("The same simulation as above, repeated 380 times!"):
    st.altair_chart(chart, use_container_width=True)
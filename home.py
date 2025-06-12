import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

with st.echo(code_location="below"):
    import streamlit as st
    import pandas as pd
    import altair as alt
    import streamlit.components.v1 as components
    st.title("Welcome to our 2025 UTK PIPES Soccer Data Science App!")
    st.image("./resources/hard_at_work.jpeg",)


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
st.write("**Hacking Skills** = making the computer do stuff with code")
st.write("**Substantive Expertise** = Deep knowledge about a specific topic, like the game of soccer")
st.write("**Math and Statistics Knowledge** = The ability to analyze things using mathematical tools")

st.subheader('So Soccer Data Scientists ask questions like...')
st.subheader('Explore some data with us!')



st.divider()
list = [27,68,71,87,91,100]
#st.write(len(list))
my_sum = 0
for number in list:
    my_sum = my_sum + number

average = my_sum/len(list)
#st.write(my_sum)
#st.write(average)
#st.write(27 + 68 + 71 + 87 + 91 + 100)
#st.write(27*6)

#if st.button("CELEBRATE"):
#    st.balloons()


framespersecond = 25

minspergame = 90

seconds_in_a_min = 60

seconds_in_a_game = framespersecond * minspergame * seconds_in_a_min
#st.write(seconds_in_a_game*12)


#uploaded_file = st.file_uploader("CLICK TO UPLOAD")
#st.header("Make sure to upload a file in order to view the data!")

#if uploaded_file is not None:
 #   db = pd.read_csv(uploaded_file)

  #  st.dataframe(db)

    #st.bar_chart(data=animal_db, x="Name",y="Speed (km/H)")

    #st.scatter_chart(animal_db,x="Name",y="Speed (km/H)")

   # db["goals per shot"] = db["Goals"]/db["Total Shots (inc. Blocks)"]

    #variable_x = st.selectbox("Pick Your X Variable!",db.columns.to_list(),1)
   #variable_y = st.selectbox("Pick Your Y Variable!",db.columns.to_list(),0)


    #st.scatter_chart(db,x=variable_x,y=variable_y)



    #variable_size = st.selectbox("What determines the size of the dots?",db.columns.to_list(),3)
    #variable_color = st.selectbox("What determines the color of the data points?",db.columns.to_list(),2)



    #st.write(goalspershot)

    #chart = alt.Chart(db).mark_circle().encode(
     #       x=variable_x,
      #      y=variable_y,
       #     size=alt.Size(variable_size,legend=None),
        #    color=alt.Color(variable_color,legend=None),
         #   tooltip=["Player","Team","Age","Goals","Total Shots (inc. Blocks)"]).properties(height=500).interactive()

    #st.altair_chart(chart, theme="streamlit", use_container_width=True)


import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components

st.set_page_config(
    page_title="footyLab • Play to Learn | DataRook, Inc.",
    page_icon="./resources/footylab_v2_icon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://datarook.com/',
        'Report a bug': "https://datarook.com/#copyright",
        'About': "# This is a version of FootyLab created for the 2025 UTK PIPES Investigators Camp. Contact gus@datarook.com to learn more"
    }
)


reese = st.Page("./reese.py", title="Reese's App")
luke = st.Page("./luke.py", title="Luke's App")
shaun = st.Page("./shaun.py", title="Shaun's App")
statsbomb = st.Page("./statsbomb.py", title="StatsBomb")
reese_tutorial = st.Page("./reese_tutorial.py", title="Reese's Tutorial")
shaun_tutorial = st.Page("./shaun_tutorial.py", title="Shaun's Tutorial")
us_pro_soccer = st.Page("./2_US_Pro_Soccer.py", title="US Pro Soccer")
luke_tutorial = st.Page("./luke_tutorial.py", title="Luke's Tutorial")

pg = st.navigation([st.Page("home.py", title="Home"),reese, luke, shaun])
pg.run()

st.logo("./resources/footyLab_v2_96_NB.png",link="https://datarook.com/")


import streamlit as st
st.title("Hello, I'm Shaun and here's my hot take list")
st.header("The best playmaker OAT?")
user_answer = st.text_input("Who is the best playmaker??")
st.write(f":red {user_answer}")
best_playmaker = "Lionel Messi"
if user_answer == best_playmaker:
    st.balloons()

st.header("Whos the most prolific striker?")
user_answer = st.text_input("Who is the most prolific striker?")
st.write(f":red {user_answer}")
best_striker = "Johan Cruyff"
if user_answer == best_striker:
    st.balloons()
st.header("Best midfielder of all time?")
user_answer = st.text_input("Who is the best midfielder/catalyst?")
st.write(f":red {user_answer}")
best_midfielder = "Iniesta"
if user_answer == best_midfielder:
    st.balloons()
st.header("How was my interactive app? (be honest duud)")
st.feedback("stars")
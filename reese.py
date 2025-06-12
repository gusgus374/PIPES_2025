import streamlit as st


st.title("Hi, my name is Reese! I would like to tell you a few things about me.")

from streamlit_extras.let_it_rain import rain

if st.button("Click here to see a hobby of mine!"):
    st.toast(":open_book:")

if st.button("Here's some of my favorite books..."):
    st.write("Jane Eyre, Pride and Prejudice, Hatchet, All Creatures Great and Small, and All the Light We Cannot See")

favorite_book = "Jane Eyre"

user_answer = st.text_input("Try and Guess My Favorite Book!")

st.write(f"You got it right, it's :blue[{user_answer}]!")

if user_answer == favorite_book:
    st.balloons()


st.button("I just won a million dollars!")
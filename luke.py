import streamlit as st

st.title("Hello Visitor!")

st.subheader("This is Luke's Page. home to the best info and worst code")


if st.button("this does nothing"):
   st.write("you should have believed me")


food_lover = st.checkbox("I like food")
if food_lover:
    st.write("I hope so")
fav_meal = st.select_slider("select your favorite meal", options= ["breakfast", "second breakfast", "elevenzies", "brunch", "lunch", "tea time", "dinner" ,"supper", "bed time snack", "midnight snack"],)
st.write("my favorite meal is", fav_meal )
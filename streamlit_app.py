import streamlit as st

st.title("TalentScout Hiring Assistant — Setup Mode")
st.write("This is a starting point for our chatbot interface.")
name = st.text_input("What's your name?")

if name:
    st.success(f"Nice to meet you, {name}!")
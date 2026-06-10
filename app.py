import streamlit as st
st.title(".env file writer") 

user_input = st.text_input

choose mode = st.text_input

if choose mode:
 mode = "env. file making"
else:
  mode = 'normal'
  

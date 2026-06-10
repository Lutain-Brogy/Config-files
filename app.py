import streamlit as st
st.title(".env file writer") 

user_input = st.text_input
choose_selection = st.selectbox(
    'Choose the type of file you want to write today',
    [".env", "none"]
)

if choose_selection == '.env':
    st.write('Hello')

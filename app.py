import streamlit as st
st.title(".env file writer") 

user_input = st.text_input
choose_selection = st.selectbox(
    'Choose the type of file you want to write today',
    [".env", "none"]
)

if choose_selection == '.env':
    env_selection = st.selectbox(
        'Choose the .env file type you want',
        ['Ai API .env type']
    )

  if env_selection == 'Ai API .env type':
    A = user_input('Type the defualt provider')

    st.code(f'''
# Default provider
DEFAULT_PROVIDER={A} 
''')
        

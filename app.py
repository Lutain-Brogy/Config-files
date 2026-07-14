import streamlit as st

st.title("Firestore Mini RuleSense")

mode = st.selectbox('Choose',
                    ["Rule","Learn"])
if mode == 'Rule':
  sentence = st.text_input("Enter sentence")

match = re.search(r"At collection (\w+) and document (\w+)", sentence)

if match:
    A = match.group(1)
    B = match.group(2)

    rule = f"""
match /{A}/{B} {{
  allow read: if request.auth != null;
}}
"""
    st.code(rule, language="javascript")

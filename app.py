import streamlit as st
import re

st.title("Firestore Mini RuleSense")

mode = st.selectbox(
    'Operation type',
    ["Standard", "Learning"]
)

if mode == 'Standard':

    Rule = st.selectbox(
        'What to do today?',
        ["Public rule", "Authenticated rule", "Create role", "Time based rule"]
    )

    if Rule == "Public rule":

        sentence = st.text_input(
            "Write your rule sentence:",
            "At collection users and document profile, allow read for everybody"
        )

        match = re.search(
            r"At collection (\w+) and document (\w+), (\w+) (\w+) for everybody",
            sentence
        )

        if match:

            A = match.group(1)  # collection
            B = match.group(2)  # document
            C = match.group(3)  # allow/deny
            D = match.group(4)  # read/write


            if C == "allow":
                condition = "true"
            elif C == "deny":
                condition = "false"


            rule = f"""
rules_version = '2';

service cloud.firestore {{
  match /databases/{{database}}/documents {{

    match /{A}/{B}/{{any}} {{
      allow {D}: if {condition};
    }}

  }}
}}
"""

            st.code(rule, language="javascript")

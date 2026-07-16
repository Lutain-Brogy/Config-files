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



    if Rule == 'Authenticated rule':
        sentence = st.text_input(
    "Write your rule sentence:",
    "At collection users and document profile, allow read for logged in"
)

match = re.search(
    r"At collection (\w+) and document (\w+), (\w+) (\w+) for logged in (\w+)",
    sentence
)

if match:

    # Sentence variables
    A = match.group(1)  # collection
    B = match.group(2)  # document
    C = match.group(4)  # allow / deny
    D = match.group(3)  # read / write / update / delete
    E = match.group(5)  # user condition

    if D == 'allow':
        D_choice = '!'
    else:
        '='



    # Condition selector
    user_type = st.selectbox(
        "Choose user condition:",
        [
            "logged in",
            "UID",
            "Role",
            "Admin",
            "Owner"
        ]
    )


    if user_type == "logged in":
        st.write('Place ; after null please')
        condition = ''


    elif user_type == "UID":
        condition = (f"&& request.auth.uid == ''")


    elif user_type == "Role":
        condition = (f"&& request.auth.token.role == ''")


    elif user_type == "Admin":
        condition = "&& request.auth.token.role == 'admin'"


    elif user_type == "Owner":
        condition = "&& request.auth.uid == resource.data.ownerId"



    # Generate rule
    use = rule = f"""
rules_version = '2';

service cloud.firestore {{
  match /databases/{{database}}/documents {{

    match /{A}/{B}/{{any}} {{
      allow {C}: if request.auth {D_choice}= null
                 {condition}
    }}

  }}
}}
"""


    st.code(rule, language="javascript")



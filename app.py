import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import re
from datetime import datetime
import pytz

st.title("My Schedule Assistant")

# Firebase init
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Input (ONLY ONCE)
user_input = st.text_input("You:")

# Default mode
mode = "normal"

# Detect mode from user input
if user_input:
    user_input_lower = user_input.lower()

    if "new contact" in user_input_lower:
        mode = "contact_saving"

    elif "new schedule" in user_input_lower:
        mode = "scheduling"

    elif "add a block" in user_input_lower:
        mode = "blocks"

    elif "my schedules" in user_input_lower:
        mode = "show_schedules"

    elif "my contacts" in user_input_lower:
        mode = "show_contacts"

    elif "fix a contact" in user_input_lower:
        mode = "contact_editing"

    elif "fix schedule" in user_input_lower:
        mode = "schedule_modifying"

    else:
        mode = "normal"
        
# setting contacts
if mode == "contact_saving":
    st.subheader("📇 Contact Saving Mode")

    st.write("Please save your contact using the following fields:")

    st.markdown("""
    a. **Name**  
    b. **Country**  
    c. **Timezone**  
    d. **Phone**  
    e. **Email**  
    f. **Notes**
    """)

    if st.button("Save Contact"):
        db.collection("contacts").add({
            "raw_input": user_input,
            "timestamp": datetime.now().isoformat()
        })

        st.success("Your contact has been saved ✔")
        st.write("Type 'My contacts' to view them.")

# contact editing
if "edit_contact_id" in st.session_state:

    if "edit_step" not in st.session_state:
        st.session_state["edit_step"] = "choose_action"

    if st.session_state["edit_step"] == "choose_action":

        st.write("Do you wish to delete or edit this contact?")

        action = st.radio("Choose action:", ["Edit", "Delete"])

        if st.button("Confirm Action"):
            st.session_state["action"] = action
            st.session_state["edit_step"] = action.lower()

    elif st.session_state["edit_step"] == "delete":

        st.write("Are you sure you want to delete this contact?")

        if st.button("Yes, Delete"):
            db.collection("contacts").document(
                st.session_state["edit_contact_id"]
            ).delete()

            st.success("Contact deleted ✔")

            del st.session_state["edit_contact_id"]
            del st.session_state["edit_step"]

    elif st.session_state["edit_step"] == "edit":

        st.write("Edit contact details:")

        contact_doc = db.collection("contacts").document(
            st.session_state["edit_contact_id"]
        ).get()

        contact_data = contact_doc.to_dict()

        name = st.text_input("Name", value=contact_data.get("name", ""))
        country = st.text_input("Country", value=contact_data.get("country", ""))
        timezone = st.text_input("Timezone", value=contact_data.get("timezone", ""))
        phone = st.text_input("Phone", value=contact_data.get("phone", ""))
        email = st.text_input("Email", value=contact_data.get("email", ""))
        notes = st.text_area("Notes", value=contact_data.get("notes", ""))

        if st.button("Save Changes"):
            db.collection("contacts").document(
                st.session_state["edit_contact_id"]
            ).update({
                "name": name,
                "country": country,
                "timezone": timezone,
                "phone": phone,
                "email": email,
                "notes": notes
            })

            st.success("Contact updated ✔")

            del st.session_state["edit_contact_id"]
            del st.session_state["edit_step"]

# scheduling
import string

user_block = ""

if mode == "scheduling":

    st.write("Who would you like to set a schedule with? Choose using letters.")

    contacts = db.collection("contacts").get()

    letters = list(string.ascii_lowercase)
    contact_map = {}

    for i, doc in enumerate(contacts):
        if i >= len(letters):
            break

        contact = doc.to_dict()
        label = letters[i]

        contact_map[label] = {
            "id": doc.id,
            "name": contact.get("name", "Unknown")
        }

        st.write(f"{label}. {contact_map[label]['name']}")

    selected = st.text_input("Enter letter (e.g. a, b, c):").lower()

    if selected and selected in contact_map:
        st.session_state["schedule_contact_id"] = contact_map[selected]["id"]

        st.success(f"Selected: {contact_map[selected]['name']}")

        st.write("Write your block here:")
        user_block = st.text_area("Schedule details")

# Process the schedule block
if user_block and "schedule_contact_id" in st.session_state:

    contact_doc = db.collection("contacts").document(
        st.session_state["schedule_contact_id"]
    ).get()

    contact = contact_doc.to_dict()
    country = contact.get("country")

    country_to_tz = {
        "Botswana": "Africa/Gaborone",
        "Cuba": "America/Havana"
    }

    other_tz_name = country_to_tz.get(country)

    if other_tz_name:

        local_tz = pytz.timezone("Africa/Gaborone")
        other_tz = pytz.timezone(other_tz_name)

        now = datetime.now()

        local_time = local_tz.localize(now)
        partner_time = local_time.astimezone(other_tz)

        user_time = local_time.strftime("%Y-%m-%d %H:%M")
        partner_time_str = partner_time.strftime("%Y-%m-%d %H:%M")
        # SAVE SCHEDULE
              db.collection("schedules").add({
            "contact_id": st.session_state["schedule_contact_id"],
            "block": user_block,
            "user_time": user_time,
            "partner_time": partner_time_str
        })

        st.success("Schedule saved ✔")

        st.write("📅 Here is your saved schedule:")

        schedules = db.collection("schedules").get()
        letters = list("abcdefghijklmnopqrstuvwxyz")

        for i, doc in enumerate(schedules):
            if i >= len(letters):
                break

            data = doc.to_dict()

            st.write(f"""
{letters[i]}.
Block: {data.get('block', '')}

User time: {data.get('user_time', '')}
Partner time: {data.get('partner_time', '')}
""")

      st.write("Type 'fix schedule' to edit or delete a schedule.")
st.write("Type 'new schedule' to create another schedule.")
st.write("Type 'my schedules' to view all saved schedules.")

# schedule modifying

if "schedule_step" not in st.session_state:
    st.session_state["schedule_step"] = "choose_action"

if mode == "schedule_modifying":

    st.write("Do you wish to delete or edit a block?")

    action = st.radio("Choose action:", ["Edit", "Delete"])

    if st.button("Continue"):

        # ---------------- DELETE FLOW ----------------
        if action == "Delete":

            st.write("📅 Select a schedule to delete:")

            schedules = db.collection("schedules").get()
            letters = list("abcdefghijklmnopqrstuvwxyz")
            schedule_map = {}

            for i, doc in enumerate(schedules):
                if i >= len(letters):
                    break

                data = doc.to_dict()
                label = letters[i]

                schedule_map[label] = {
                    "id": doc.id,
                    "block": data.get("block", "")
                }

                st.write(f"{label}. {schedule_map[label]['block']}")

            selected = st.text_input("Choose letter to delete:").lower()

            if selected and selected in schedule_map:
                db.collection("schedules").document(
                    schedule_map[selected]["id"]
                ).delete()

                st.success("Schedule deleted ✔")

        # ---------------- EDIT FLOW ----------------
        elif action == "Edit":

            st.write("📅 Select a schedule to edit:")

            schedules = db.collection("schedules").get()
            letters = list("abcdefghijklmnopqrstuvwxyz")
            schedule_map = {}

            for i, doc in enumerate(schedules):
                if i >= len(letters):
                    break

                data = doc.to_dict()
                label = letters[i]

                schedule_map[label] = {
                    "id": doc.id,
                    "block": data.get("block", "")
                }

                st.write(f"{label}. {schedule_map[label]['block']}")

            selected = st.text_input("Choose letter to edit:").lower()

            if selected and selected in schedule_map:
                st.session_state["edit_schedule_id"] = schedule_map[selected]["id"]
                st.success("Schedule selected ✔")


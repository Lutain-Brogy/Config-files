import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import re
from datetime import datetime
import pytz

st.title("My schedule assistant")

# Firebase init
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Input (ONLY ONCE)
user_input = st.text_input("You:")

mode = "normal"

if user_input:
    user_input_lower = user_input.lower()

    if "new contact" in user_input_lower:
        mode = "contact_saving"
    elif "new schedule" in user_input_lower or "meet" in user_input_lower:
        mode = "scheduling"
    elif "add a block" in user_input_lower:
        mode = "blocks"
    elif "my schedules" in user_input_lower:
        mode = "show_schedules"
    elif "my contacts" in user_input_lower:
        mode = "show_contacts"
    else:
        mode = "normal"


# ---------------- SCHEDULING ----------------
if mode == "scheduling":
    st.write("Scheduling mode detected")

    if st.button("Process Schedule"):

        match = re.search(r"meet (\w+) at (\d{2}:\d{2})", user_input.lower())

        if match:
            name = match.group(1).capitalize()
            time_str = match.group(2)

            contact_query = db.collection("contacts").where("name", "==", name).get()

            if contact_query:

                contact = contact_query[0].to_dict()
                country = contact["country"]

                country_to_tz = {
                    "Botswana": "Africa/Gaborone",
                    "Cuba": "America/Havana"
                }

                other_tz_name = country_to_tz.get(country)

                if other_tz_name:

                    local_tz = pytz.timezone("Africa/Gaborone")
                    other_tz = pytz.timezone(other_tz_name)

                    local_time = datetime.strptime(time_str, "%H:%M")
                    local_time = local_tz.localize(local_time)

                    other_time = local_time.astimezone(other_tz)

                    local_result = local_time.strftime("%H:%M")
                    other_result = other_time.strftime("%H:%M")

                    st.write(f"Meet {name} at {local_result}")
                    st.write(f"{name} time: {other_result}")

                    db.collection("schedules").add({
                        "task": f"Meet {name}",
                        "your_time": local_result,
                        "their_time": other_result
                    })

                    st.success("Schedule saved")

                else:
                    st.write("No timezone found for contact country")

            else:
                st.write("Not a contact")


# ---------------- SHOW SCHEDULES ----------------
if mode == "show_schedules":
    st.write("📅 Your schedules:")

    schedules = db.collection("schedules").stream()

    for s in schedules:
        st.write(s.to_dict())


# ---------------- SHOW CONTACTS ----------------
if mode == "show_contacts":
    st.write("📇 Your contacts:")

    contacts = db.collection("contacts").stream()

    for c in contacts:
        st.write(c.to_dict())


# ---------------- CONTACT SAVING ----------------
if mode == "contact_saving":
    st.write("Add a new contact:")

    name = st.text_input("Name")
    phone = st.text_input("Phone")
    city = st.text_input("City")
    country = st.text_input("Country")
    notes = st.text_area("Notes")

    if st.button("Save Contact"):
        db.collection("contacts").add({
            "name": name,
            "phone": phone,
            "city": city,
            "country": country,
            "notes": notes
        })

        st.success("Contact saved!")


# ---------------- BLOCKS ----------------
if mode == "blocks":
    st.write("Add your block it will be added to your schedule.")

    block_input = st.text_input("Write your block:")

    if st.button("Save Block") and block_input:
        db.collection("schedules").add({
            "block": block_input
        })

        st.success("Block saved to schedules!")

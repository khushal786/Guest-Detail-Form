import streamlit as st
import pandas as pd
import datetime
import psycopg2

# PostgreSQL connection setup
def get_db_connection():
    connection = psycopg2.connect(
        host="104.198.165.4",
        database="postgres",
        user="postgres",
        password="postgres108"
    )
    return connection

# Initialize the form data dictionary
form_data = {}

# Collect the number of guests
num_guests = st.number_input("Number of Guests", min_value=1, max_value=10, step=1)

# Dynamic input fields for guest names, ages, and contact numbers
guests = []
contact_present = False  # Flag to check if at least one contact number is present
for i in range(num_guests):
    guest_name = st.text_input(f"Name of Guest {i+1}")
    guest_age = st.number_input(f"Age of Guest {i+1} (2 digits only)", min_value=10, max_value=99, step=1)
    guest_contact = st.text_input(f"Contact Number of Guest {i+1} (10 digits, optional)")

    if guest_contact:
        contact_present = True
        if len(guest_contact) != 10:
            st.warning(f"Contact number for Guest {i+1} must be exactly 10 digits.")

    guests.append({"name": guest_name, "age": guest_age, "contact": guest_contact})

form_data["guests"] = guests

# Ensure at least one contact number is provided
if not contact_present:
    st.error("Please provide at least one contact number.")

# Mode of travel for arrival
arrival_travel_mode = st.selectbox("Mode of travel for arrival", ["air", "road", "train"])
form_data["arrival_travel_mode"] = arrival_travel_mode

# New field: Arrival Location
arrival_location = st.text_input("Arrival Location", placeholder="Enter the location of arrival")
form_data["arrival_location"] = arrival_location

# Date and time of arrival (separate fields)
arrival_date = st.date_input("Date of Arrival")
arrival_time = st.time_input("Time of Arrival", value=datetime.time(22, 0))
form_data["arrival_date"] = arrival_date
form_data["arrival_time"] = arrival_time

# Checkout date with restriction and default time logic
st.markdown("**Checkout Date Description:** Allowed checkout dates are 26th and 27th January 2025 only.")
checkout_date = st.date_input("Checkout Date", value=datetime.date(2025, 1, 26))

if checkout_date not in [datetime.date(2025, 1, 26), datetime.date(2025, 1, 27)]:
    st.error("Please select a valid checkout date (26th or 27th January 2025).")

# Default checkout time for 27th January 2025
if checkout_date == datetime.date(2025, 1, 27):
    checkout_time = datetime.time(10, 0)
    st.markdown("Checkout time is set to **10:00 AM** by default for 27th January 2025.")
else:
    checkout_time = st.time_input("Checkout Time", value=datetime.time(10, 0))

form_data["checkout_date"] = checkout_date
form_data["checkout_time"] = checkout_time

# Mode of travel for departure
departure_travel_mode = st.selectbox("Mode of travel for departure", ["air", "road", "train"])
form_data["departure_travel_mode"] = departure_travel_mode

# Date and time of departure (separate fields)
departure_date = st.date_input("Date of Departure")
departure_time = st.time_input("Time of Departure", value=datetime.time(22, 0))
form_data["departure_date"] = departure_date
form_data["departure_time"] = departure_time

# Button to save the form data to PostgreSQL
if st.button("Submit"):
    # Validate data before submission
    if not contact_present:
        st.error("At least one contact number must be provided.")
    elif checkout_date not in [datetime.date(2025, 1, 26), datetime.date(2025, 1, 27)]:
        st.error("Invalid checkout date. Please select 26th or 27th January 2025.")
    elif not arrival_location:
        st.error("Please provide the arrival location.")
    else:
        # Convert the form data to a DataFrame
        guests_data = pd.DataFrame(form_data["guests"])

        # Add the other fields to the dataframe
        guests_data['arrival_date'] = form_data["arrival_date"]
        guests_data['arrival_time'] = form_data["arrival_time"].strftime('%H:%M')
        guests_data['checkout_date'] = form_data["checkout_date"]
        guests_data['checkout_time'] = form_data["checkout_time"].strftime('%H:%M')
        guests_data['departure_date'] = form_data["departure_date"]
        guests_data['departure_time'] = form_data["departure_time"].strftime('%H:%M')
        guests_data['arrival_travel_mode'] = form_data["arrival_travel_mode"]
        guests_data['arrival_location'] = form_data["arrival_location"]  # New field
        guests_data['departure_travel_mode'] = form_data["departure_travel_mode"]

        # Save the data to PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()

        for index, row in guests_data.iterrows():
            cursor.execute("""
                INSERT INTO guest_data (name, age, contact, arrival_date, arrival_time, checkout_date, checkout_time, 
                                        departure_date, departure_time, arrival_travel_mode, arrival_location, departure_travel_mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['name'], row['age'], row['contact'], row['arrival_date'], row['arrival_time'], 
                  row['checkout_date'], row['checkout_time'], row['departure_date'], row['departure_time'], 
                  row['arrival_travel_mode'], row['arrival_location'], row['departure_travel_mode']))
        
        conn.commit()
        cursor.close()
        conn.close()

        st.success("Data saved successfully. Your Presence is awaited!")

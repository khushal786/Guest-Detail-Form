import streamlit as st
import pandas as pd
import datetime
import psycopg2

st.image("image_header.png")

# PostgreSQL connection setup
def get_db_connection():
    connection = psycopg2.connect(
        host="34.55.180.159",
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
aadhaar_valid = True  # Flag for Aadhaar validation
for i in range(num_guests):
    guest_name = st.text_input(f"Name of Guest {i+1}")
    guest_age = st.number_input(f"Age of Guest {i+1} (2 digits only)", min_value=10, max_value=99, step=1)

    # Aadhaar Number Field
    guest_aadhaar = st.text_input(f"Aadhaar Number of Guest {i+1} (12 digits)")
    if not guest_aadhaar or not guest_aadhaar.isdigit() or len(guest_aadhaar) != 12:
        aadhaar_valid = False
        st.warning(f"Aadhaar number for Guest {i+1} must be exactly 12 digits and cannot be empty.")

    guest_contact = st.text_input(f"Contact Number of Guest {i+1} (10 digits, optional)")
    if guest_contact:
        contact_present = True
        if len(guest_contact) != 10:
            st.warning(f"Contact number for Guest {i+1} must be exactly 10 digits.")

    guests.append({
        "name": guest_name,
        "age": guest_age,
        "aadhaar": guest_aadhaar,
        "contact": guest_contact
    })

form_data["guests"] = guests

# Ensure at least one contact number is provided
if not contact_present:
    st.error("Please provide at least one contact number.")

# Mode of travel for arrival
arrival_travel_mode = st.selectbox("Mode of travel for arrival", ["air", "bus", "train", "Own Vechile"])
form_data["arrival_travel_mode"] = arrival_travel_mode

# Conditional fields based on "Self" option
if arrival_travel_mode != "Own Vechile":
    # Ensure default None for transport-related fields
    form_data["arrival_train_number"] = None
    form_data["departure_train_number"] = None
    form_data["arrival_flight_number"] = None
    form_data["departure_flight_number"] = None
    form_data["arrival_airline_name"] = None
    form_data["departure_airline_name"] = None

    # Arrival location
    arrival_location = st.text_input("Arrival Location", placeholder="Enter the location of arrival")
    form_data["arrival_location"] = arrival_location

    # Date and time of arrival
    arrival_date = st.date_input("Date of Arrival")
    arrival_time = st.time_input("Time of Arrival", value=datetime.time(22, 0))
    form_data["arrival_date"] = arrival_date
    form_data["arrival_time"] = arrival_time

    # Mode of travel for departure
    departure_travel_mode = st.selectbox("Mode of travel for departure", ["air", "bus", "train", "Own Vechile"])
    form_data["departure_travel_mode"] = departure_travel_mode

    # Date and time of departure
    departure_date = st.date_input("Date of Departure")
    departure_time = st.time_input("Time of Departure", value=datetime.time(22, 0))
    form_data["departure_date"] = departure_date
    form_data["departure_time"] = departure_time

    # Train number for arrival and departure
    if arrival_travel_mode == "train":
        form_data["arrival_train_number"] = st.text_input("Train Number for Arrival")
        if not form_data["arrival_train_number"]:
            st.warning("Train Number for Arrival is required as you selected 'train' as the arrival mode.")

    if departure_travel_mode == "train":
        form_data["departure_train_number"] = st.text_input("Train Number for Departure")
        if not form_data["departure_train_number"]:
            st.warning("Train Number for Departure is required as you selected 'train' as the departure mode.")
    else:
        form_data["departure_train_number"] = None

    # Flight number and airline name for arrival and departure
    if arrival_travel_mode == "air":
        form_data["arrival_flight_number"] = st.text_input("Flight Number for Arrival")
        form_data["arrival_airline_name"] = st.text_input("Airline Name for Arrival")
        if not form_data["arrival_flight_number"]:
            st.warning("Please enter the flight number for arrival as 'air' is selected as the arrival mode.")
        if not form_data["arrival_airline_name"]:
            st.warning("Please enter the airline name for arrival as 'air' is selected as the arrival mode.")
    else:
        form_data["arrival_flight_number"] = None
        form_data["arrival_airline_name"] = None

    if departure_travel_mode == "air":
        form_data["departure_flight_number"] = st.text_input("Flight Number for Departure")
        form_data["departure_airline_name"] = st.text_input("Airline Name for Departure")
        if not form_data["departure_flight_number"]:
            st.warning("Please enter the flight number for departure as 'air' is selected as the departure mode.")
        if not form_data["departure_airline_name"]:
            st.warning("Please enter the airline name for departure as 'air' is selected as the departure mode.")
    else:
        form_data["departure_flight_number"] = None
        form_data["departure_airline_name"] = None
        
else:
    # Default None for all transport-related keys when "Own Vechile"
    form_data["arrival_location"] = None
    form_data["arrival_date"] = None
    form_data["arrival_time"] = None
    form_data["departure_travel_mode"] = None
    form_data["departure_date"] = None
    form_data["departure_time"] = None
    form_data["arrival_train_number"] = None
    form_data["departure_train_number"] = None
    form_data["arrival_flight_number"] = None
    form_data["departure_flight_number"] = None
    form_data["arrival_airline_name"] = None
    form_data["departure_airline_name"] = None

# Checkout date with restriction and default time logic
checkout_date = st.date_input("Checkout Date", value=datetime.date(2025, 1, 26))

if checkout_date not in [datetime.date(2025, 1, 26), datetime.date(2025, 1, 27)]:
    st.error("Please select a valid checkout date (26th or 27th January 2025).")

# Default checkout time for 27th January 2025
if checkout_date == datetime.date(2025, 1, 27):
    checkout_time = datetime.time(10, 0)
    st.markdown(
        "Default Checkout time :"
        "<span style='font-weight: bold; border-radius: 4px;'>10:00 AM</span> "
        "on 27th January 2025.",
        unsafe_allow_html=True,
    )
else:
    checkout_time = st.time_input("Checkout Time", value=datetime.time(10, 0))

form_data["checkout_date"] = checkout_date
form_data["checkout_time"] = checkout_time

# Button to save the form data to PostgreSQL
if st.button("Submit"):
    # Validate data before submission
    if not contact_present:
        st.error("At least one contact number must be provided.")
    elif checkout_date not in [datetime.date(2025, 1, 26), datetime.date(2025, 1, 27)]:
        st.error("Invalid checkout date. Please select 26th or 27th January 2025.")
    elif arrival_travel_mode != "Own Vechile" and not form_data["arrival_location"]:
        st.error("Please provide the arrival location.")
    elif arrival_travel_mode == "train" and not form_data["arrival_train_number"]:
        st.error("Please enter the train number for arrival as 'train' is selected as the arrival mode.")
    elif departure_travel_mode == "train" and not form_data["departure_train_number"]:
        st.error("Please enter the train number for departure as 'train' is selected as the departure mode.")
    elif arrival_travel_mode == "air" and (not form_data["arrival_flight_number"] or not form_data["arrival_airline_name"]):
        st.error("Please enter both the flight number and airline name for arrival as 'air' is selected as the arrival mode.")
    elif departure_travel_mode == "air" and (not form_data["departure_flight_number"] or not form_data["departure_airline_name"]):
        st.error("Please enter both the flight number and airline name for departure as 'air' is selected as the departure mode.")
    elif not aadhaar_valid:
        st.error("Please ensure all guests have valid 12-digit Aadhaar numbers.")
    else:
        # Convert the form data to a DataFrame
        guests_data = pd.DataFrame(form_data["guests"])

        # Add the other fields to the dataframe
        guests_data['arrival_date'] = form_data["arrival_date"]
        guests_data['arrival_time'] = form_data["arrival_time"]
        guests_data['checkout_date'] = form_data["checkout_date"]
        guests_data['checkout_time'] = form_data["checkout_time"]
        guests_data['departure_date'] = form_data["departure_date"]
        guests_data['departure_time'] = form_data["departure_time"]
        guests_data['arrival_travel_mode'] = form_data["arrival_travel_mode"]
        guests_data['arrival_location'] = form_data["arrival_location"]
        guests_data['departure_travel_mode'] = form_data["departure_travel_mode"]
        guests_data['arrival_train_number'] = form_data["arrival_train_number"]
        guests_data['departure_train_number'] = form_data["departure_train_number"]
        guests_data['arrival_flight_number'] = form_data["arrival_flight_number"]
        guests_data['departure_flight_number'] = form_data["departure_flight_number"]
        guests_data['arrival_airline_name'] = form_data["arrival_airline_name"]
        guests_data['departure_airline_name'] = form_data["departure_airline_name"]

        # Save the data to PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()

        for index, row in guests_data.iterrows():
            cursor.execute("""
                INSERT INTO guest_data (name, age, aadhaar, contact, arrival_date, arrival_time, arrival_location, 
                                        checkout_date, checkout_time, departure_date, departure_time, 
                                        arrival_travel_mode, departure_travel_mode, 
                                        arrival_train_number, arrival_flight_number, departure_train_number, 
                                        departure_flight_number, arrival_airline_name, departure_airline_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (row['name'], row['age'], row['aadhaar'], row['contact'], row['arrival_date'], row['arrival_time'],
                  row['arrival_location'], row['checkout_date'], row['checkout_time'], row['departure_date'], 
                  row['departure_time'], row['arrival_travel_mode'], row['departure_travel_mode'], 
                  row['arrival_train_number'], row['arrival_flight_number'], row['departure_train_number'], 
                  row['departure_flight_number'], row['arrival_airline_name'], row['departure_airline_name']))
        conn.commit()
        cursor.close()
        conn.close()

        st.success("Form submitted successfully 🎉. Your Presence is awaited!")

 # Big right tick
        st.markdown(
            """
            <div style="text-align: center; margin-top: 20px;">
                <span style="font-size: 100px; color: green;">✅</span>
            </div>
            """,
            unsafe_allow_html=True
        )

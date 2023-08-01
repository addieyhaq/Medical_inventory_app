import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Create a connection to the SQLite database
conn = sqlite3.connect('patient_data.db')
c = conn.cursor()

# Function to get data for a specific date and shift
def get_data_for_date_shift(selected_date, selected_shift):
    # Convert selected_shift to datetime objects
    shift_start = datetime.strptime(selected_shift[0], "%H:%M:%S")
    shift_end = datetime.strptime(selected_shift[1], "%H:%M:%S")

    # Format the selected_date to match the format in the database (YYYY-MM-DD)
    formatted_date = selected_date.strftime('%Y-%m-%d')

    # Create datetime objects for the start and end of the selected_date with the selected_shift timings
    start_datetime = datetime.strptime(f"{formatted_date} {selected_shift[0]}", "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime(f"{formatted_date} {selected_shift[1]}", "%Y-%m-%d %H:%M:%S")

    # For C shift, split the comparison into two parts
    if shift_start > shift_end:
        c.execute('''SELECT * FROM patient_data 
                     WHERE (datetime(date_time) >= ? AND time(date_time) >= ?) 
                     OR (datetime(date_time) >= ? AND time(date_time) < ?)''',
                  (start_datetime, shift_start, end_datetime, shift_end))
    else:
        c.execute('''SELECT * FROM patient_data 
                     WHERE datetime(date_time) >= ? AND datetime(date_time) < ?''',
                  (start_datetime, end_datetime))
        
    return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])



# Function to get data based on search term
def get_data_for_search(search_term):
    if search_term:
        c.execute('''SELECT * FROM patient_data 
                     WHERE card_number LIKE ? OR name LIKE ? OR shop LIKE ?''',
                  (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        return pd.DataFrame(c.fetchall(), columns=[desc[0] for desc in c.description])
    else:
        return pd.DataFrame()  # Return an empty DataFrame if search_term is empty


# Centered layout
st.set_page_config(layout="centered",
                   page_title ="Med-Techno labs",
)

# Professional fonts
st.markdown('<style>body{font-family: Arial, sans-serif;}</style>', unsafe_allow_html=True)

# Color scheme light blue and white
st.markdown('<style>body{background-color: lightblue;}</style>', unsafe_allow_html=True)
st.markdown('<style>body{color: white;}</style>', unsafe_allow_html=True)

# Panel Title
st.title("Shift Data Panel")

# First Column - Calendar Widget
st.header("Select a date:")
selected_date = st.date_input("", datetime.today())

# Second Column - Shift Selection
st.header("Select a shift:")
shift_options = {
    "A shift (08:00-16:59)": ("08:00:00", "16:59:00"),
    "B shift (17:00-22:59)": ("17:00:00", "22:59:00"),
    "C shift (23:00-07:59)": ("23:00:00", "07:59:00")
}
selected_shift = st.radio("", list(shift_options.keys()))

# Get selected shift start and end time
selected_shift = shift_options[selected_shift]

# Third Column - Search Widget
st.header("Search:")
search_term = st.text_input("Search by Card Number, Patient Name, or Shop:")

# Get data for selected date and shift
data_for_date_shift = get_data_for_date_shift(selected_date, selected_shift)

# Filter data based on search term
if search_term:
    search_term = search_term.lower()  # Convert search term to lowercase for case-insensitive matching
    filtered_data_for_date_shift = data_for_date_shift[
        (data_for_date_shift['card_number'].str.lower().str.contains(search_term)) |
        (data_for_date_shift['name'].str.lower().str.contains(search_term)) |
        (data_for_date_shift['shop'].str.lower().str.contains(search_term))
    ]
else:
    filtered_data_for_date_shift = data_for_date_shift

# Get data based on search term for the entire database
data_for_search = get_data_for_search(search_term)

# Display the filtered data for selected date and shift
st.subheader("Data for Selected Date and Shift:")
st.write(f"Selected Date: {selected_date} | Selected Shift: {selected_shift[0]} to {selected_shift[1]}")
st.dataframe(filtered_data_for_date_shift)

# Display the data for the search term from the entire database
st.subheader("Data for Search Term:")
st.dataframe(data_for_search)

# Close the connection to the SQLite database
conn.close()

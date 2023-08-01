import streamlit as st
import pandas as pd
import sqlite3
from pandas.io.formats.style import Styler

# Function to create a connection with SQLite database
def create_conn():
    try:
        conn = sqlite3.connect('patient_data.db')
        return conn
    except Error as e:
        print(e)

# Function to fetch data from the medicine record table and create a DataFrame
def fetch_medicine_records(start_date, end_date):
    """Fetch data from the medicine_record table within specified period"""
    conn = create_conn()
    try:
        with conn:
            start_date = start_date.strftime('%Y-%m-%d')
            end_date = end_date.strftime('%Y-%m-%d')
            c = conn.cursor()
            c.execute("SELECT medicine_name, SUM(dispersed_quantity) AS total_dispersed_quantity "
                    "FROM medicine_record "
                    "WHERE date_time BETWEEN ? AND ? "
                    "GROUP BY medicine_name", (start_date, end_date))
            records = c.fetchall()
            
            df_medicine_records = pd.DataFrame(records, columns=['medicine_name', 'total_dispersed_quantity'])
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

    return df_medicine_records

# Centered layout
st.set_page_config(layout="centered", page_title="Med-Techno labs")

start_date = st.date_input("Select the start date:")
end_date = st.date_input("Select the end date:")
df_medicine_records = fetch_medicine_records(start_date, end_date)

st.title("Medicine Records")
st.write(f"Showing records from {start_date} to {end_date}")

# Customizing DataFrame display
st.table(df_medicine_records.assign(hack='').set_index('hack'))
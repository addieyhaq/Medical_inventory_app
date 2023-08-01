import streamlit as st
import pandas as pd
import sqlite3
import base64
import io
from openpyxl import Workbook

import streamlit as st

# Set the page title
st.set_page_config(page_title="Med-Techno labs"
)

# Connect to SQLite database
conn = sqlite3.connect('patient_data.db')

# Query to fetch necessary data from the inventory table
query = '''
SELECT drug_name, 
    strength, 
    dosage_form, 
    total_quantity, 
    Issued_Medicine, 
    dispersed_medicine 
FROM inventory
'''

# Execute the query and load the data into a pandas DataFrame
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Create a new column for the full medicine name
df['medicine_name'] = df['drug_name'] + ' ' + df['strength'] + ' ' + df['dosage_form']

# Rearrange the columns into the specific order
df = df[['medicine_name', 'total_quantity', 'Issued_Medicine', 'dispersed_medicine']]

st.title("Homepage")

# Display the DataFrame
st.write(df)

# Function to create an excel file from the DataFrame
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl', mode='xlsx') as writer: 
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data

# Function to create a download link for the excel file
def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    val = to_excel(df)
    b64 = base64.b64encode(val) 
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Medtechnolabs.xlsx">Download Excel file</a>'

# Display a download link on the Streamlit app
st.markdown(get_table_download_link(df), unsafe_allow_html=True)
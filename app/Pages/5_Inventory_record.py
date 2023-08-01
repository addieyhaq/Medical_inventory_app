import streamlit as st
import sqlite3
import pandas as pd

# Create a connection to the SQLite database for inventory
inventory_conn = sqlite3.connect('patient_data.db')

# Function to check if the "medicine_issue" column exists in the 'inventory' table
def check_medicine_issue_column():
    with inventory_conn:
        inventory_c = inventory_conn.cursor()
        inventory_c.execute('''PRAGMA table_info(inventory)''')
        columns = inventory_c.fetchall()
        column_names = [column[1] for column in columns]
        return "medicine_issue" in column_names

# Function to add the "medicine_issue" column to the 'inventory' table
def add_medicine_issue_column():
    if not check_medicine_issue_column():
        with inventory_conn:
            inventory_c = inventory_conn.cursor()
            inventory_c.execute('''ALTER TABLE inventory ADD COLUMN medicine_issue INTEGER''')

# Function to fetch data from the inventory table
def fetch_inventory_data():
    with inventory_conn:
        inventory_c = inventory_conn.cursor()
        inventory_c.execute('''SELECT drug_name, strength, dosage_form, total_quantity, Issued_Medicine FROM inventory''')
        inventory_data = inventory_c.fetchall()
    return inventory_data

# Function to update total_quantity and issued_medicine in the inventory database
def update_inventory_data(drug_name, strength, dosage_form, total_quantity, issued_medicine, medicine_issue):
    with inventory_conn:
        inventory_c = inventory_conn.cursor()
        inventory_c.execute('''UPDATE inventory SET total_quantity=?, Issued_Medicine=?, medicine_issue=?
                                WHERE drug_name=? AND strength=? AND dosage_form=?''',
                             (total_quantity, issued_medicine, medicine_issue, drug_name, strength, dosage_form))
        inventory_conn.commit()

# Function to combine drug_name, strength, and dosage_form to form a single "Medicine Name" column
def combine_medicine_name(row):
    return f"{row['drug_name']} {row['strength']} {row['dosage_form']}"

# Centered layout
st.set_page_config(layout="centered", page_title="Med-Techno labs")

# Professional fonts
st.markdown('<style>body{font-family: Arial, sans-serif;}</style>', unsafe_allow_html=True)

# Color scheme light blue and white
st.markdown('<style>body{background-color: lightblue;}</style>', unsafe_allow_html=True)
st.markdown('<style>body{color: white;}</style>', unsafe_allow_html=True)

# Panel Title
st.title("Record Keeping Panel")

# Add the "medicine_issue" column to the 'inventory' table (if it doesn't already exist)
add_medicine_issue_column()

# Fetch data from the inventory table
inventory_data = fetch_inventory_data()

# Convert the data to a Pandas DataFrame
df_inventory = pd.DataFrame(inventory_data, columns=["drug_name", "strength", "dosage_form", "Total Quantity", "Issued Medicine"])

# Combine drug_name, strength, and dosage_form to form a single "Medicine Name" column
df_inventory["Medicine Name"] = df_inventory.apply(combine_medicine_name, axis=1)

# Create an empty column "Medicine Issue" in the DataFrame
df_inventory["Medicine Issue"] = ""

# Select only the required columns for display
display_columns = ["Medicine Name", "Total Quantity", "Issued Medicine", "Medicine Issue"]
edited_df = df_inventory[display_columns]

# Data editor widget to display and edit the DataFrame
edited_df = st.data_editor(edited_df, width=900, height=500)

if st.button("Save Changes"):
    with st.spinner("Updating data..."):
        for i, row in edited_df.iterrows():
            drug_name, strength, dosage_form = df_inventory.loc[i, "drug_name"], df_inventory.loc[i, "strength"], df_inventory.loc[i, "dosage_form"]
            total_quantity_str, issued_medicine_str = row["Total Quantity"], row["Issued Medicine"]
            medicine_issue_str = row["Medicine Issue"]
            
            # Convert the strings to integers (handling possible None values)
            total_quantity = int(total_quantity_str) if total_quantity_str else 0
            issued_medicine = int(issued_medicine_str) if issued_medicine_str else 0
            
            # Convert the "Medicine Issue" to integer, or set to 0 if it cannot be converted
            try:
                medicine_issue = int(medicine_issue_str)
            except (ValueError, TypeError):
                medicine_issue = 0

            # Get the value from the data frame
            df_medicine_issue_str = df_inventory.loc[i, "Medicine Issue"]

            # Check if the string is not empty, convert to integer or else set as 0
            df_medicine_issue = int(df_medicine_issue_str) if df_medicine_issue_str else 0
            
            # Calculate the difference between edited medicine_issue and original value
            edited_medicine_issue = medicine_issue - df_medicine_issue
            
            # Update Total Quantity with the difference
            total_quantity -= edited_medicine_issue
            
            # Update Issued Medicine with the difference
            issued_medicine += edited_medicine_issue
            
            # Update the inventory data in the database
            update_inventory_data(drug_name, strength, dosage_form, total_quantity, issued_medicine, medicine_issue)
    
    st.success("Data updated successfully!")

inventory_conn.close()


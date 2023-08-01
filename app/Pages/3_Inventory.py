import streamlit as st
import sqlite3
from datetime import datetime

# Create a connection to the SQLite database for inventory
inventory_conn = sqlite3.connect('patient_data.db')
inventory_c = inventory_conn.cursor()

# Create the inventory table if it doesn't exist
inventory_c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    drug_name TEXT,
                    strength TEXT,
                    total_quantity INTEGER,
                    dosage_form TEXT,
                    batch_or_consignment_no TEXT,
                    dispersed_medicine INTEGER,
                    Issued_Medicine INTEGER,
                    not_applied_to_case INTEGER,
                    date TEXT
                )''')
inventory_conn.commit()

# Function to check if a similar drug exists in the inventory
def check_existing_entry(drug_name, strength, dosage_form):
    inventory_c.execute('''SELECT * FROM inventory WHERE drug_name=? AND strength=? AND dosage_form=?''',
                         (drug_name, strength, dosage_form))
    existing_data = inventory_c.fetchone()
    return existing_data

# Function to add data to the inventory table


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
st.title("Inventory Panel")

# ... (The rest of the code remains the same)
def add_inventory_data(data):
    existing_data = check_existing_entry(data["Drug Name"], data["Strength"], data["Dosage Form"])

    if existing_data:
        # Update the existing entry with the new total quantity
        total_quantity = data["Total Quantity"] + existing_data[3]
        inventory_c.execute('''UPDATE inventory SET total_quantity=?, 
                                dosage_form=?, batch_or_consignment_no=?, 
                                not_applied_to_case=?, date=? WHERE id=?''',
                             (total_quantity, data["Dosage Form"],
                              data["Batch/Consignment No."], data["Not Applied to Case"], data["Date"],
                              existing_data[0]))
        st.success("Data added to inventory successfully!")
    else:
        # Create a new entry in the database
        inventory_c.execute('''INSERT INTO inventory (
                                drug_name,
                                strength,
                                total_quantity,
                                dosage_form,
                                batch_or_consignment_no,
                                not_applied_to_case,
                                date
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (data["Drug Name"],
                             data["Strength"],
                             data["Total Quantity"],
                             data["Dosage Form"],
                             data["Batch/Consignment No."],
                             data["Not Applied to Case"],
                             data["Date"]))
        st.success("Data added to inventory successfully!")

    inventory_conn.commit()

# Inventory Form
st.header("Inventory Form")

# Form Input Fields
medicine_name = st.text_input("Name of the Drug")
drug_name = medicine_name.lower()

# Strength field with radio options for unit selection
strength_units = ["Mg", "%", "Nil"]
selected_strength_unit = st.radio("Select the unit for Strength:", strength_units)
strength = st.text_input(f"Strength ({selected_strength_unit})", key="strength_input")

# Calculate Total Quantity in Tablets
total_quantity = st.number_input("Total Quantity (Tablets/bottles/vials/Piece)", min_value=0, step=1)

dosage_form_options = ["Oral", "IV", "IM", "Topical", "Accessory"]
dosage_form = st.selectbox("Dosage Form", dosage_form_options)

# Batch No. / Consignment No. and Not Applied to Case Checkbox
batch_or_consignment_no = st.text_input("Batch No. / Consignment No.")
not_applied_to_case = st.checkbox("Not Applied to Case")

# Date Widget to Select Date for the Inventory Entry
date = st.date_input("Date for the Inventory Entry", datetime.today())

# Add Button to Add Data into the Inventory Table
if st.button("Add"):
    if drug_name and strength and total_quantity and dosage_form and date:
        inventory_data = {
            "Drug Name": drug_name,
            "Strength": f"{strength} {selected_strength_unit}",  # Combine the strength and unit
            "Total Quantity": total_quantity,
            "Dosage Form": dosage_form,
            "Batch/Consignment No.": batch_or_consignment_no,
            "Not Applied to Case": not_applied_to_case,
            "Date": date.strftime('%Y-%m-%d')
        }
        add_inventory_data(inventory_data)
        # Clear form after successful submission
        drug_name = ""
        strength = ""
        total_quantity = 0
        batch_or_consignment_no = ""

# Close the connection to the SQLite database for inventory
inventory_conn.close()


def add_inventory_data(data):
    existing_data = check_existing_entry(data["Drug Name"], data["Strength"], data["Dosage Form"])

    if existing_data:
        # Update the existing entry with the new total quantity
        total_quantity = data["Total Quantity"] + existing_data[3]
        inventory_c.execute('''UPDATE inventory SET total_quantity=?, 
                                dosage_form=?, batch_or_consignment_no=?, 
                                not_applied_to_case=?, date=? WHERE id=?''',
                             (total_quantity, data["Dosage Form"],
                              data["Batch/Consignment No."], data["Not Applied to Case"], data["Date"],
                              existing_data[0]))
        st.success("Data added to inventory successfully!")
    else:
        # Create a new entry in the database
        inventory_c.execute('''INSERT INTO inventory (
                                drug_name,
                                strength,
                                total_quantity,
                                dosage_form,
                                batch_or_consignment_no,
                                not_applied_to_case,
                                date
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (data["Drug Name"],
                             data["Strength"],
                             data["Total Quantity"],
                             data["Dosage Form"],
                             data["Batch/Consignment No."],
                             data["Not Applied to Case"],
                             data["Date"]))
        st.success("Data added to inventory successfully!")

    inventory_conn.commit()


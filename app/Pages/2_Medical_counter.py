
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime


# Create a connection to the SQLite database
conn = sqlite3.connect('patient_data.db')
c = conn.cursor()

# Create the patient_data table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS patient_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                card_number TEXT,
                shop TEXT,
                opd_slip TEXT,
                treatment TEXT,
                emergency_complaint TEXT,
                dressing_name TEXT,
                doctor_name TEXT,
                medicine_info TEXT,
                date_time TEXT
            )''')

            
            

# Create the medicine_record table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS medicine_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT,
                shop TEXT,
                medicine_name TEXT,
                dispersed_quantity INTEGER,
                date_time TEXT
            )''')

conn.commit()

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
st.title("Medical Panel")

# ... (The rest of the code remains the same)

# Enter name
enter_name = st.text_input("Please enter the name")
enter_name = enter_name.lower()  # Convert the entered name to lowercase



# Enter name
enter_card_number = st.text_input("Please enter the Card Number")
enter_card_number = enter_card_number.lower()  # Convert the entered name to lowercase


# Enter shop
shops = ["S shop", "N Shop", "R Shop", "Q Shop", "SSAMC", "SPM", "M shop", "Admin", "KRl Security", "Z shop", "WTP",
         "FGS", "Marketing", "Bank", "Medical", "Finance", "Procurement", "Transport", "MR", "T Shop",
         "Worker Canteen", "Executive Mess", "Visitor", "CMD"]
enter_shop = st.selectbox("Please select the shop", shops)

# Opd slip present or not
enter_opd_slip = st.radio("Opd slip present or not", ["Yes", "No"])

treatments = {
    "emergency": "Enter your emergency complaint",
    "medicine": "Select medicines from the inventory list",
    "opd": "Select a doctor from the list and choose medicines with quantity",
    "dressing": "Ask the user for additional information related to dressing treatment",
    "multiple": "Execute all functions: emergency, dressing, opd, and medicines with quantity"
}
# ... (The rest of the code remains the same)

# Execute the query to fetch inventory from SQLite
df = pd.read_sql_query("SELECT drug_name, strength, dosage_form, CAST(Issued_Medicine AS INTEGER) AS Issued_Medicine FROM inventory", conn)


# ... (Rest of the code remains the same)


# Filter out records where total_quantity is zero
df = df[df['Issued_Medicine'] > 0]

# Combine columns to create a single column for multi select
df['display_name'] = df['drug_name'] + '  ' + df['strength'] + '  ' + df['dosage_form']

# Store the display_name values in a list
inventory = df['display_name'].tolist()

#integration into inventory list
inventory_list = inventory

doctor_list = ["Dr Salman", "Dr M Ehteram", "Dr Saleemullah"]

selected_treatment = st.selectbox("Select the treatment:", list(treatments.keys()))

complaint = ""
medicine_info = ""
doctor_name = ""
dressing_name = ""

if selected_treatment == "emergency" or selected_treatment == "multiple":
    complaint = st.text_input("Enter your emergency complaint:")
    # Process the complaint for the emergency treatment

if selected_treatment == "dressing" or selected_treatment == "multiple":
    dressing_name = st.selectbox("Please select a name from the list:", ["Noman", "Ehtesham", "Asaduddin","Gultaf", "Shakeel","Asad Ali Rao","Mubasher", "Nasir"])
    # Process the name for the dressing treatment

if selected_treatment == "opd" or selected_treatment == "multiple":
    doctor_name = st.selectbox("Please select a doctor from the list:", doctor_list)
    # Process the doctor name for the opd treatment

# Dictionary to store selected medicines and their quantities
selected_medicines_dict = {}

if selected_treatment == "medicine" or selected_treatment == "opd" or selected_treatment == "multiple" or selected_treatment == "emergency":
    # Display the medicine inventory DataFrame only if the selected treatment is "medicine" or "opd"
    if selected_treatment == "medicine" or selected_treatment == "opd":
        medicine_inventory_df = pd.DataFrame(inventory_list, columns=["Medicine"])

    selected_medicines = st.multiselect("Select medicines:", inventory_list)
    # Process the selected medicines for the medicine treatment

    # Clear the dictionary before updating the selected medicines
    selected_medicines_dict.clear()

    for medicine in selected_medicines:
        quantity = st.number_input(f"Enter quantity for {medicine}:", min_value=0, step=1)

        # Append the medicine and quantity to the dictionary
        selected_medicines_dict[medicine] = quantity

# ... (Rest of the code remains the same)

data = {
    "Name": enter_name,
    "Card": enter_card_number,
    "Shop": enter_shop,
    "Opd Slip": enter_opd_slip,
    "Treatment": selected_treatment,
    "Emergency Complaint": complaint,
    "Date and Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# Append medicine information to the data dictionary
if selected_treatment == "medicine" or selected_treatment == "opd" or selected_treatment == "multiple" or selected_treatment == "emergency":
    data["Medicine Info"] = "\n".join([f"{medicine}: {quantity}" for medicine, quantity in selected_medicines_dict.items()])

# ... (Rest of the code remains the same)
if selected_treatment == "dressing" or selected_treatment == "multiple":
    data["Dressing Name"] = dressing_name

if selected_treatment == "opd" or selected_treatment == "multiple":
    data["Doctor Name"] = doctor_name

# ... (The rest of the code remains the same)

def update_medicine_inventory(medicine_index, drug_info, issued_medicine, quantity):
    with conn:
        c = conn.cursor()

        # Retrieve the current dispersed_medicine and Issued_Medicine values from the database
        c.execute('''SELECT dispersed_medicine, Issued_Medicine FROM inventory 
                     WHERE drug_name = ? AND strength = ? AND dosage_form = ?''',
                  (df.at[medicine_index, 'drug_name'],
                   df.at[medicine_index, 'strength'],
                   df.at[medicine_index, 'dosage_form']))

        current_values = c.fetchone()
        current_dispersed_medicine, current_issued_medicine = current_values[0], current_values[1]

        # Check if current_dispersed_medicine is None and set it to 0
        if current_dispersed_medicine is None:
            current_dispersed_medicine = 0

        # Calculate the new dispersed_medicine and Issued_Medicine values
        new_dispersed_medicine = current_dispersed_medicine + quantity
        new_issued_medicine = current_issued_medicine - quantity

        # Update the inventory table with the new dispersed_medicine and Issued_Medicine values
        c.execute('''UPDATE inventory 
                     SET dispersed_medicine = ?, Issued_Medicine = ? 
                     WHERE drug_name = ? AND strength = ? AND dosage_form = ?''',
                  (new_dispersed_medicine,
                   new_issued_medicine,
                   df.at[medicine_index, 'drug_name'],
                   df.at[medicine_index, 'strength'],
                   df.at[medicine_index, 'dosage_form']))

        conn.commit()


        # Update the medicine_record table with dispersed quantity
        update_medicine_records(enter_card_number, enter_shop, drug_info, quantity)

        # Update total quantity in dataframe
        df.at[medicine_index, 'Issued_Medicine'] -= quantity



def update_medicine_records(card_number, shop, medicine_name, dispersed_quantity):
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with conn:
        c = conn.cursor()
        c.execute('''INSERT INTO medicine_record (card_number, shop, medicine_name, dispersed_quantity, date_time)
                     VALUES (?, ?, ?, ?, ?)''',
                  (card_number, shop, medicine_name, dispersed_quantity, date_time))
        conn.commit()


def add_data_to_database(data):
    # Set flag to True by default
    sufficient_stock = True

    # First update medicine_inventory's total quantity and update medicine_record table
    for medicine, quantity in selected_medicines_dict.items():
        # Get index of medicine in our dataframe
        medicine_index = df[df['display_name'] == medicine].index[0]

        # Check if there is enough quantity to dispense
        if df.at[medicine_index, 'Issued_Medicine'] < quantity:
            st.warning(f"Not enough quantity for {medicine}. Only {df.at[medicine_index, 'Issued_Medicine']} left.")
            # Set the flag to False if there is not enough stock
            sufficient_stock = False
            continue

        # Update inventory with the new Issued_Medicine and dispersed_medicine
        update_medicine_inventory(medicine_index, medicine, df.at[medicine_index, 'Issued_Medicine'], quantity)

    # ... (Rest of the code remains the same)

    # Only update the patient data if there is sufficient stock
    if sufficient_stock:
        c.execute('''INSERT INTO patient_data (
                        name,
                        card_number,
                        shop,
                        opd_slip,
                        treatment,
                        emergency_complaint,
                        dressing_name,
                        doctor_name,
                        medicine_info,
                        date_time
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (data["Name"],
                     data["Card"],
                     data["Shop"],
                     data["Opd Slip"],
                     data["Treatment"],
                     data["Emergency Complaint"],
                     data.get("Dressing Name"),
                     data.get("Doctor Name"),
                     data.get("Medicine Info"),
                     data["Date and Time"]))
        conn.commit()
    else:
        st.warning("Data has not been saved due to insufficient inventory.")


# ... (The rest of the code remains the same)


    # Only update the patient data if there is sufficient stock
    if sufficient_stock:
        c.execute('''INSERT INTO patient_data (
                        name,
                        card_number,
                        shop,
                        opd_slip,
                        treatment,
                        emergency_complaint,
                        dressing_name,
                        doctor_name,
                        medicine_info,
                        date_time
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (data["Name"],
                     data["Card"],
                     data["Shop"],
                     data["Opd Slip"],
                     data["Treatment"],
                     data["Emergency Complaint"],
                     data.get("Dressing Name"),
                     data.get("Doctor Name"),
                     data.get("Medicine Info"),
                     data["Date and Time"]))
        conn.commit()
    else:
        st.warning("Data has not been saved due to insufficient inventory.")


# Create the main DataFrame
df_main = pd.DataFrame([data])

# Display the main DataFrame
st.write(df_main)

# Add button layout
col1 = st.columns(1)[0]

if col1.button("ADD"):
    if enter_name and enter_card_number:
        add_data_to_database(data)
        st.success("Data added successfully!")
        enter_name = ""
        enter_card_number = ""
    else:
        st.warning("Name or Card Number missing!")

# Retrieve the last 5 entries from the database
c.execute("SELECT * FROM patient_data ORDER BY id DESC LIMIT 5")
previous_entries = pd.read_sql_query("SELECT * FROM patient_data ORDER BY id DESC LIMIT 5", conn)

# Display previous 5 entries
st.subheader("Last 5 Entries")
st.write(previous_entries)

# Close the connection to the SQLite database
conn.close()


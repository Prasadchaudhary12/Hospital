import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------
# File paths
# --------------------------
PATIENT_FILE = "patients.csv"
DOCTOR_FILE = "doctors.csv"
APPOINTMENT_FILE = "appointments.csv"
BILL_FILE = "bills.csv"

# --------------------------
# Load data
# --------------------------
def load_file(file, cols):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame(columns=cols)

patients = load_file(PATIENT_FILE, ["Patient_ID", "Name", "Age", "Gender", "Contact"])
doctors = load_file(DOCTOR_FILE, ["Doctor_ID", "Name", "Specialization"])
appointments = load_file(APPOINTMENT_FILE, ["Appointment_ID", "Patient", "Doctor", "Date"])
bills = load_file(BILL_FILE, ["Bill_ID", "Patient", "Amount", "Date"])

# --------------------------
# Save function
# --------------------------
def save(df, file):
    df.to_csv(file, index=False)

# --------------------------
# UI Navigation
# --------------------------
st.set_page_config(page_title="Hospital Management System", layout="wide")
menu = st.sidebar.selectbox("Menu", [
    "Dashboard",
    "Register Patient",
    "Add Doctor",
    "Book Appointment",
    "Billing",
    "Records"
])

st.title("🏥 Hospital Management System")

# --------------------------
# Dashboard
# --------------------------
if menu == "Dashboard":
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Patients", len(patients))
    col2.metric("Doctors", len(doctors))
    col3.metric("Appointments", len(appointments))
    col4.metric("Total Revenue", f"₹ {bills['Amount'].sum() if not bills.empty else 0}")

    st.subheader("📊 Appointments Trend")
    if not appointments.empty:
        appointments["Date"] = pd.to_datetime(appointments["Date"])
        trend = appointments.groupby("Date").size()
        st.line_chart(trend)

# --------------------------
# Register Patient
# --------------------------
elif menu == "Register Patient":
    st.header("👤 Patient Registration")

    with st.form("patient_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", 0, 120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        contact = st.text_input("Contact")

        if st.form_submit_button("Register"):
            pid = f"P{len(patients)+1}"

            new_patient = pd.DataFrame([{
                "Patient_ID": pid,
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Contact": contact
            }])

            patients_df = pd.concat([patients, new_patient], ignore_index=True)
            save(patients_df, PATIENT_FILE)

            st.success(f"✅ Patient Registered with ID: {pid}")

# --------------------------
# Add Doctor
# --------------------------
elif menu == "Add Doctor":
    st.header("👨‍⚕️ Add Doctor")

    with st.form("doctor_form"):
        name = st.text_input("Doctor Name")
        specialization = st.text_input("Specialization")

        if st.form_submit_button("Add Doctor"):
            did = f"D{len(doctors)+1}"

            new_doc = pd.DataFrame([{
                "Doctor_ID": did,
                "Name": name,
                "Specialization": specialization
            }])

            doctor_df = pd.concat([doctors, new_doc], ignore_index=True)
            save(doctor_df, DOCTOR_FILE)

            st.success(f"✅ Doctor Added with ID: {did}")

# --------------------------
# Book Appointment
# --------------------------
elif menu == "Book Appointment":
    st.header("📅 Appointment Booking")

    if patients.empty or doctors.empty:
        st.warning("Please add patients and doctors first")
    else:
        with st.form("appointment_form"):
            patient = st.selectbox("Select Patient", patients["Name"])
            doctor = st.selectbox("Select Doctor", doctors["Name"])
            date = st.date_input("Appointment Date")

            if st.form_submit_button("Book"):
                aid = f"A{len(appointments)+1}"

                new_appt = pd.DataFrame([{
                    "Appointment_ID": aid,
                    "Patient": patient,
                    "Doctor": doctor,
                    "Date": date
                }])

                appt_df = pd.concat([appointments, new_appt], ignore_index=True)
                save(appt_df, APPOINTMENT_FILE)

                st.success(f"✅ Appointment booked! ID: {aid}")

# --------------------------
# Billing
# --------------------------
elif menu == "Billing":
    st.header("💳 Billing")

    if patients.empty:
        st.warning("No patients available")
    else:
        with st.form("billing_form"):
            patient = st.selectbox("Select Patient", patients["Name"])
            amount = st.number_input("Amount", min_value=0.0)

            if st.form_submit_button("Generate Bill"):
                bid = f"B{len(bills)+1}"

                new_bill = pd.DataFrame([{
                    "Bill_ID": bid,
                    "Patient": patient,
                    "Amount": amount,
                    "Date": datetime.today().strftime('%Y-%m-%d')
                }])

                bill_df = pd.concat([bills, new_bill], ignore_index=True)
                save(bill_df, BILL_FILE)

                st.success(f"✅ Bill Generated! ID: {bid}")

# --------------------------
# Records
# --------------------------
elif menu == "Records":
    st.header("📁 Records")

    tab1, tab2, tab3, tab4 = st.tabs(["Patients", "Doctors", "Appointments", "Billing"])

    with tab1:
        st.dataframe(patients)

    with tab2:
        st.dataframe(doctors)

    with tab3:
        st.dataframe(appointments)

    with tab4:
        st.dataframe(bills)

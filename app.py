import streamlit as st
import mysql.connector
import pandas as pd


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="S4siyam@1010",   # apna password yahan
        database="clinic_rdbms_exam"
    )


st.title("🏥 Clinic Patient Management System")


menu = ["Add Patient", "View Patients", "Search Patient"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Patient":
    st.subheader("➕ Add New Patient")

    with st.form("patient_form"):
        patient_id = st.number_input("Patient ID", min_value=1)
        name = st.text_input("Patient Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=0, max_value=120)
        phone = st.text_input("Phone")
        address = st.text_area("Address")
        reg_date = st.date_input("Registration Date")

        submit = st.form_submit_button("Save Patient")

        if submit:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM patients WHERE patient_id = %s", (patient_id,))
            if cursor.fetchone()[0] > 0:
                st.warning(f"Patient ID {patient_id} already exists. Please choose a unique Patient ID.")
            else:
                query = """
                INSERT INTO patients 
                (patient_id, patient_name, gender, age, phone, address, registration_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                values = (patient_id, name, gender, age, phone, address, reg_date)

                try:
                    cursor.execute(query, values)
                    conn.commit()
                    st.success("✅ Patient record inserted successfully!")
                except mysql.connector.IntegrityError as err:
                    conn.rollback()
                    st.error(f"Database error: {err}")
                finally:
                    conn.close()


elif choice == "View Patients":
    st.subheader("📋 All Patients")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    df = pd.DataFrame(data, columns=columns)

    st.dataframe(df)

    conn.close()


elif choice == "Search Patient":
    st.subheader("🔍 Search Patient")

    search = st.text_input("Enter Name or Phone")

    if st.button("Search"):

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM patients
        WHERE patient_name LIKE %s OR phone LIKE %s
        """

        value = f"%{search}%"

        cursor.execute(query, (value, value))
        data = cursor.fetchall()

        if data:
            columns = [col[0] for col in cursor.description]
            df = pd.DataFrame(data, columns=columns)
            st.dataframe(df)
        else:
            st.warning("No patient found")

        conn.close()
import streamlit as st
import psycopg2
import pandas as pd

st.title("Getting Lost Survey")

# Database connection
@st.cache(allow_output_mutation=True)
def connect_to_db():
    return psycopg2.connect(
        dbname="glprui_jloddr",
        user="glprui_jloddr",
        password="612ef773",
        host="db.qgiscloud.com",
        port="5432",
        sslmode="prefer"
    )

# Function to submit data
def submit_data(age, gender, transport, multi_transport, time_of_day, day_of_week, description, start_point, lost_point, end_point):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO public.gettinglost_tracking (Age, Gender, Transport, TimeOfDay, DayOfWeek, Description) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING ID;
            """,
            (age, gender, transport, time_of_day, day_of_week, description)
        )

        record_id = cursor.fetchone()[0]

        points = {'start': start_point, 'lost': lost_point, 'end': end_point}
        for pointType, point in points.items():
            if point:
                cursor.execute(
                    """
                    INSERT INTO public.gettinglost_geom (ID, PointType, geom) 
                    VALUES (%s, %s, ST_SetSRID(ST_Point(%s, %s), 4326));
                    """,
                    (record_id, pointType, point[1], point[0])
                )

        conn.commit()
        st.success("Data recorded successfully!")
    except Exception as e:
        conn.rollback()
        st.error(f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Form inputs
age = st.selectbox("Age", ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"])
gender = st.radio("Gender", ["M", "F", "O", "PNTS"])
transport = st.radio("Mode of Transport", ["Walk", "Car", "Bike", "Train", "Other", "Multi"])

multi_transport = []
if transport == "Multi":
    multi_transport = st.multiselect("If Multi, Select Modes Used", ["Walk", "Car", "Bike", "Train", "Other"])

time_of_day = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
day_of_week = st.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
description = st.text_area("Why did you get lost?")

start_point = st.map()
lost_point = st.map()
end_point = st.map()

if st.button("Save"):
    submit_data(age, gender, transport, multi_transport, time_of_day, day_of_week, description, start_point, lost_point, end_point)

st.markdown("---")
st.markdown("For a more detailed survey, click the link or scan the QR code:")
st.markdown("[https://arcg.is/1GK5jP0](https://arcg.is/1GK5jP0)")
st.image("static/Getting Lost Survey.png", width=200)

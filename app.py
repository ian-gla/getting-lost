import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw, Geocoder, MiniMap
import psycopg2
import pandas as pd

st.set_page_config(layout="wide")

# Database connection
@st.cache_resource
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
def submit_data(age, gender, transport, multi_transport, time_of_day, day_of_week, description, points):
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

# Initialize session state for points
if 'points' not in st.session_state:
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
if 'step' not in st.session_state:
    st.session_state['step'] = 1

# Sidebar for marker management
st.sidebar.title("Step 1: Add Markers on the Map")

# Selector for point type
point_type = st.sidebar.radio("Select Point Type to Add", ["start", "lost", "end"])

# Buttons to clear points
if st.sidebar.button("Clear All Markers"):
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
    st.rerun()

if st.sidebar.button("Clear Selected Marker"):
    st.session_state['points'][point_type] = None
    st.rerun()

# Create a placeholder for the map
map_placeholder = st.empty()

def create_map():
    # Initialize map
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=10, control_scale=True)

    # Add existing points to the map
    for pointType, coords in st.session_state['points'].items():
        if coords:
            folium.Marker(
                location=coords,
                popup=pointType,
                icon=folium.Icon(color="red" if pointType == "start" else "blue" if pointType == "end" else "orange")
            ).add_to(m)

    # Add click functionality without creating popups
    draw = Draw(
        export=False,
        draw_options={
            "circle": False,
            "polyline": False,
            "polygon": False,
            "rectangle": False,
            "circlemarker": False,
            "marker": True,
        },
        edit_options={"edit": False}
    )
    draw.add_to(m)
    Geocoder(add_marker=True).add_to(m)
    MiniMap().add_to(m)

    return m

# Display map
with map_placeholder.container():
    output = st_folium(create_map(), width="100%", height=600, key="map")

# Check for map click data
if output and 'last_clicked' in output and output['last_clicked'] is not None:
    lat = output['last_clicked']['lat']
    lon = output['last_clicked']['lng']
    st.session_state['points'][point_type] = (lat, lon)
    st.rerun()

# Display current points
st.write("Current Points:", st.session_state['points'])

# Step 2: Survey questions
if st.session_state['step'] == 1:
    if st.sidebar.button("Done Adding Markers"):
        st.session_state['step'] = 2
        st.rerun()

if st.session_state['step'] == 2:
    st.sidebar.title("Step 2: Fill Out the Survey")

    age = st.sidebar.selectbox("Age", ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"])
    gender = st.sidebar.radio("Gender", ["M", "F", "O", "PNTS"])
    transport = st.sidebar.radio("Mode of Transport", ["Walk", "Car", "Bike", "Train", "Other", "Multi"])

    multi_transport = []
    if transport == "Multi":
        multi_transport = st.sidebar.multiselect("If Multi, Select Modes Used", ["Walk", "Car", "Bike", "Train", "Other"])

    time_of_day = st.sidebar.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
    day_of_week = st.sidebar.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    description = st.sidebar.text_area("Why did you get lost?")

    if st.sidebar.button("Save"):
        submit_data(age, gender, transport, multi_transport, time_of_day, day_of_week, description, st.session_state['points'])

    st.sidebar.markdown("---")
    st.sidebar.markdown("For a more detailed survey, click the link or scan the QR code:")
    st.sidebar.markdown("[https://arcg.is/1GK5jP0](https://arcg.is/1GK5jP0)")
    st.sidebar.image("static/Getting Lost Survey.png", width=200)

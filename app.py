import streamlit as st
import psycopg2
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide")

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

# Sidebar form inputs
st.sidebar.title("Getting Lost Survey")

age = st.sidebar.selectbox("Age", ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"])
gender = st.sidebar.radio("Gender", ["M", "F", "O", "PNTS"])
transport = st.sidebar.radio("Mode of Transport", ["Walk", "Car", "Bike", "Train", "Other", "Multi"])

multi_transport = []
if transport == "Multi":
    multi_transport = st.sidebar.multiselect("If Multi, Select Modes Used", ["Walk", "Car", "Bike", "Train", "Other"])

time_of_day = st.sidebar.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
day_of_week = st.sidebar.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
description = st.sidebar.text_area("Why did you get lost?")

# Map interaction
st.sidebar.title("Select Points on Map")
point_type = st.sidebar.radio("Select Point Type", ["start", "lost", "end"])

if 'points' not in st.session_state:
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}

def map_click(lat, lon):
    st.session_state['points'][point_type] = (lat, lon)

st.sidebar.write("Click on the map to select points.")

# Map display
map_data = pd.DataFrame([
    {'lat': st.session_state['points']['start'][0], 'lon': st.session_state['points']['start'][1]} if st.session_state['points']['start'] else {'lat': None, 'lon': None},
    {'lat': st.session_state['points']['lost'][0], 'lon': st.session_state['points']['lost'][1]} if st.session_state['points']['lost'] else {'lat': None, 'lon': None},
    {'lat': st.session_state['points']['end'][0], 'lon': st.session_state['points']['end'][1]} if st.session_state['points']['end'] else {'lat': None, 'lon': None}
])

map_data.dropna(inplace=True)

layer = pdk.Layer(
    'ScatterplotLayer',
    data=map_data,
    get_position='[lon, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=200,
)

view_state = pdk.ViewState(
    latitude=map_data['lat'].mean() if not map_data.empty else 0,
    longitude=map_data['lon'].mean() if not map_data.empty else 0,
    zoom=10,
    pitch=0,
)

r = pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{pointType} point at {lat}, {lon}"}
)

st.pydeck_chart(r)

if st.button("Save"):
    submit_data(age, gender, transport, multi_transport, time_of_day, day_of_week, description, st.session_state['points'])

st.markdown("---")
st.markdown("For a more detailed survey, click the link or scan the QR code:")
st.markdown("[https://arcg.is/1GK5jP0](https://arcg.is/1GK5jP0)")
st.image("static/Getting Lost Survey.png", width=200)

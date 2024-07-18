import streamlit as st
import folium
from folium import LayerControl
from folium.plugins import Geocoder, MiniMap
from streamlit_folium import st_folium
import psycopg2

st.set_page_config(layout="wide")

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

def submit_data(consent, age, gender, other_transport, time_of_day, day_of_week, familiarity, route_guidance, group, navigation_ease, personal_context, lost_factors, open_ended_explanation, points):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO public.gettinglost_tracking (
                Consent, Age, Gender, OtherTransport, TimeOfDay, DayOfWeek, Familiarity, RouteGuidance, Group, NavigationEase, PersonalContext, LostFactors, OpenEndedExplanation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING ID;
            """,
            (consent, age, gender, other_transport, time_of_day, day_of_week, familiarity, route_guidance, group, navigation_ease, personal_context, lost_factors, open_ended_explanation)
        )

        record_id = cursor.fetchone()[0]

        for pointType, point in points.items():
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

def create_map(points, center=None, zoom=10):
    if center is None:
        center = [51.5074, -0.1278]
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, tiles=None)
    Geocoder().add_to(m)
    MiniMap().add_to(m)
    basemap_satellite_layer1 = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="ESRI Satellite",
        overlay=False,
        control=True
    )
    basemap_satellite_layer1.add_to(m)
    OpenStreetMap_HOT = folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        attr="Humanitarian OpenStreetMap Team",
        name="OpenStreetMap_HOT",
        overlay=False,
        control=True  
    )
    OpenStreetMap_HOT.add_to(m)
    LayerControl().add_to(m)
    for point_type, coords in points.items():
        if coords:
            folium.Marker(
                location=coords,
                popup=point_type,
                icon=folium.Icon(color="red" if point_type == "start" else "blue" if point_type == "end" else "orange")
            ).add_to(m)
    return m

# Initialize session state for points if not already done
if 'points' not in st.session_state:
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
if 'survey' not in st.session_state:
    st.session_state['survey'] = False
if 'point_type' not in st.session_state:
    st.session_state['point_type'] = 'start'
if 'map_center' not in st.session_state:
    st.session_state['map_center'] = [51.5074, -0.1278]
if 'map_zoom' not in st.session_state:
    st.session_state['map_zoom'] = 10

# Custom CSS for colored buttons
st.markdown(
    """
    <style>
    .start-button { background-color: red; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    .lost-button { background-color: orange; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    .end-button { background-color: blue; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    .reset-button { background-color: gray; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.image("static/UoG_keyline.png")
st.title("Step 1 - Add Your :red[Start], :orange[Lost] and :blue[End] Markers on the Map")

# Custom buttons for selecting point type
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(":red[Start]", key="start-button", help="Place a marker on the corresponding map location",  use_container_width=True):
        st.session_state['point_type'] = 'start'
        st.markdown('<div class="start-button">Start Point</div>', unsafe_allow_html=True)

with col2:
    if st.button(":orange[Lost]", key="lost-button", help="Place a marker on the corresponding map location", use_container_width=True):
        st.session_state['point_type'] = 'lost'
        st.markdown('<div class="lost-button">Lost Point</div>', unsafe_allow_html=True)

with col3:
    if st.button(":blue[End]", key="end-button", help="Place a marker on the corresponding map location",  use_container_width=True):
        st.session_state['point_type'] = 'end'
        st.markdown('<div class="end-button">End Point</div>', unsafe_allow_html=True)

# Reset button
if st.button(":red-background[:x: **Clear Markers**]", key="reset-button", use_container_width=True):
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
    st.rerun()

map_placeholder = st.empty()

with map_placeholder.container():
    folium_map = create_map(st.session_state['points'], center=st.session_state['map_center'], zoom=st.session_state['map_zoom'])
    map_output = st_folium(folium_map, width="100%", height=800)

new_coords = None
if map_output and 'last_clicked' in map_output and map_output['last_clicked'] is not None:
    new_coords = (map_output['last_clicked']['lat'], map_output['last_clicked']['lng'])
    # Update the map center to the current view, ensuring it's a list
    st.session_state['map_center'] = [map_output['center']['lat'], map_output['center']['lng']]
    st.session_state['map_zoom'] = map_output['zoom']

if new_coords:
    st.session_state['points'][st.session_state['point_type']] = new_coords
    map_placeholder.empty()
    with map_placeholder.container():
        folium_map = create_map(st.session_state['points'], center=st.session_state['map_center'], zoom=st.session_state['map_zoom'])
        st_folium(folium_map, width="100%", height=800)

if all(st.session_state['points'].values()) and not st.session_state['survey']:
    if st.sidebar.button("**Proceed to Survey** :question:", use_container_width=True, key="sidebar"):
        st.session_state['survey'] = True
    if st.button("**Proceed to Survey** :question:", use_container_width=True, key="main"):
        st.session_state['survey'] = True
else:
    st.sidebar.title("Step 2 - Survey Questions")
    st.sidebar.warning("Please add your start, lost, and end points before proceeding to the survey questions.")

if st.session_state['survey']:
    st.sidebar.title("Step 2 - Survey Questions")
    consent = st.sidebar.checkbox("I consent to participate in this survey.")
    age = st.sidebar.selectbox("Age", ["18-25","25-35","35-45","45-55","55-65","65+"])
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
    other_transport = st.sidebar.multiselect("Did you use any other mode of transport during this journey?", ["Walk", "Car", "Bike", "Train", "Other"])
    time_of_day = st.sidebar.selectbox("Time of Day (2-hour window)", ["00:00-02:00", "02:00-04:00", "04:00-06:00", "06:00-08:00", "08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00", "22:00-24:00"])
    day_of_week = st.sidebar.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    familiarity = st.sidebar.radio("Familiarity (1-5, with 1 being not familiar with the area and 5 being very familiar with the area)", [1, 2, 3, 4, 5],horizontal=True)
    route_guidance = st.sidebar.selectbox("Main method of route guidance", ["GPS/sat nav (e.g. Google maps, Citymapper, etc)", "Paper map", "Someone else’s directions (in group)", "Someone else’s directions (not in group)", "Street signs", "I was just wandering"])
    group = st.sidebar.radio("Walking in group?", ["Yes", "No"])
    navigation_ease = st.sidebar.radio("How easy do you typically find navigating whilst walking in cities (independent of this event)? [1-5]", [1, 2, 3, 4, 5],horizontal=True)
    personal_context = st.sidebar.text_area("Please describe the context in which you got lost in your own words")
    lost_factors = st.sidebar.multiselect("Ranking important factors for getting lost", ["environment", "street layout", "number of people", "busy streets", "complex roadsigns"], help="Please select in yoor order of significance")
    open_ended_explanation = st.sidebar.text_area("Open-ended explanation of why you got lost")

    if st.sidebar.button("Save"):
        submit_data(consent, age, gender, other_transport, time_of_day, day_of_week, familiarity, route_guidance, group, navigation_ease, personal_context, lost_factors, open_ended_explanation, st.session_state['points'])
        st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
        st.session_state['survey'] = False
        st.rerun()

# st.sidebar.write("Current Points:")
# st.sidebar.json(st.session_state['points'])

    st.sidebar.markdown("---")
    st.sidebar.markdown("For a more detailed survey, click the link or scan the QR code:")
    st.sidebar.markdown("[https://arcg.is/1GK5jP0](https://arcg.is/1GK5jP0)")
    st.sidebar.image("static/Getting Lost Survey.png", width=200)

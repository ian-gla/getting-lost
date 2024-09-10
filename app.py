import streamlit as st
import folium
from folium import LayerControl
from folium.plugins import Geocoder, MiniMap
from streamlit_folium import st_folium
import psycopg2


st.set_page_config(layout='wide')


@st.cache_resource
def connect_to_db():
    return psycopg2.connect(
        dbname='glprui_jloddr',
        user='glprui_jloddr',
        password='612ef773',
        host='db.qgiscloud.com',
        port='5432',
        sslmode='prefer',
    )


def submit_data(
    age,
    gender,
    transport,
    multi_transport,
    time_of_day,
    day_of_week,
    description,
    points,
):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO public.gettinglost_tracking
            (Age, Gender, Transport, TimeOfDay, DayOfWeek, Description)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING ID;
            """,
            (age, gender, transport, time_of_day, day_of_week, description),
        )

        record_id = cursor.fetchone()[0]

        for pointType, point in points.items():
            cursor.execute(
                """
                INSERT INTO public.gettinglost_geom (ID, PointType, geom)
                VALUES (%s, %s, ST_SetSRID(ST_Point(%s, %s), 4326));
                """,
                (record_id, pointType, point[1], point[0]),
            )

        conn.commit()
        st.success('Data recorded successfully!')
    except Exception as e:
        conn.rollback()
        st.error(f'Error: {str(e)}')
    finally:
        cursor.close()
        conn.close()


def create_map(points, center=None, zoom=10):
    if center is None:
        center = [51.5074, -0.1278]
    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, Tiles=None)
    Geocoder().add_to(m)
    MiniMap().add_to(m)
    basemap_satellite_layer1 = folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services'
        '/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='ESRI Satellite',
        overlay=False,
        control=True,
    )
    basemap_satellite_layer1.add_to(m)
    OpenStreetMap_HOT = folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        attr='Humanitarian OpenStreetMap Team',
        name='OpenStreetMap_HOT',
        overlay=False,
        control=True,
    )
    OpenStreetMap_HOT.add_to(m)
    LayerControl().add_to(m)
    for point_type, coords in points.items():
        if coords:
            folium.Marker(
                location=coords,
                popup=point_type,
                icon=folium.Icon(
                    color='red'
                    if point_type == 'start'
                    else 'blue'
                    if point_type == 'end'
                    else 'orange'
                ),
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
    .start-button { background-color: red; color: white; border: none; padding:
    10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    .lost-button { background-color: orange; color: white; border:
    none; padding:
    10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    .end-button { background-color: blue; color: white; border: none; padding:
    10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    .reset-button { background-color: gray; color: white; border: none; padding:
    10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.image('static/UoG_keyline.png')
st.title('Step 1 - Add Your :red[Start], :orange[Lost] and :blue[End] Markers on the Map')

# Custom buttons for selecting point type
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        ':red[Start]',
        key='start-button',
        help='Place a marker on the corresponding map location',
        use_container_width=True,
    ):
        st.session_state['point_type'] = 'start'
        st.markdown('<div class="start-button">Start Point</div>', unsafe_allow_html=True)

with col2:
    if st.button(
        ':orange[Lost]',
        key='lost-button',
        help='Place a marker on the corresponding map location',
        use_container_width=True,
    ):
        st.session_state['point_type'] = 'lost'
        st.markdown('<div class="lost-button">Lost Point</div>', unsafe_allow_html=True)

with col3:
    if st.button(
        ':blue[End]',
        key='end-button',
        help='Place a marker on the corresponding map location',
        use_container_width=True,
    ):
        st.session_state['point_type'] = 'end'
        st.markdown('<div class="end-button">End Point</div>', unsafe_allow_html=True)


# st.write(f"Selected Point Type: {st.session_state['point_type'].capitalize()}")
# Reset button
if st.button(
    ':red-background[:x: **Clear Markers**]',
    key='reset-button',
    use_container_width=True,
):
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
    st.rerun()

map_placeholder = st.empty()

with map_placeholder.container():
    folium_map = create_map(
        st.session_state['points'],
        center=st.session_state['map_center'],
        zoom=st.session_state['map_zoom'],
    )
    map_output = st_folium(folium_map, width='100%', height=800)

new_coords = None
if map_output and 'last_clicked' in map_output and map_output['last_clicked'] is not None:
    new_coords = (map_output['last_clicked']['lat'], map_output['last_clicked']['lng'])
    # Update the map center to the current view, ensuring it's a list
    st.session_state['map_center'] = [
        map_output['center']['lat'],
        map_output['center']['lng'],
    ]
    st.session_state['map_zoom'] = map_output['zoom']

if new_coords:
    st.session_state['points'][st.session_state['point_type']] = new_coords
    map_placeholder.empty()
    with map_placeholder.container():
        folium_map = create_map(
            st.session_state['points'],
            center=st.session_state['map_center'],
            zoom=st.session_state['map_zoom'],
        )
        st_folium(folium_map, width='100%', height=800)

if all(st.session_state['points'].values()) and not st.session_state['survey']:
    if st.sidebar.button(
        '**Proceed to Survey** :question:', use_container_width=True, key='sidebar'
    ):
        st.session_state['survey'] = True
    if st.button('**Proceed to Survey** :question:', use_container_width=True, key='main'):
        st.session_state['survey'] = True
else:
    st.sidebar.title('Step 2 - Survey Questions')
    st.sidebar.warning(
        'Please add your start, lost, and end points before proceeding to the survey questions.'
    )


if st.session_state['survey']:
    st.sidebar.title('Step 2 - Survey Questions')
    age = st.sidebar.selectbox('Age', ['18-25', '25-35', '35-45', '45-55', '55-65', '65+'])
    gender = st.sidebar.radio('Gender', ['Male', 'Female', 'Other', 'Prefer not to say'])
    transport = st.sidebar.radio(
        'Mode of Transport', ['Walk', 'Car', 'Bike', 'Train', 'Other', 'Multi']
    )
    multi_transport = (
        st.sidebar.multiselect(
            'If Multi, select modes used', ['Walk', 'Car', 'Bike', 'Train', 'Other']
        )
        if transport == 'Multi'
        else []
    )
    time_of_day = st.sidebar.selectbox('Time of Day', ['Morning', 'Afternoon', 'Evening', 'Night'])
    day_of_week = st.sidebar.selectbox(
        'Day of the Week',
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    )
    description = st.sidebar.text_area('Why did you get lost?')

    if st.sidebar.button('Save'):
        submit_data(
            age,
            gender,
            transport,
            multi_transport,
            time_of_day,
            day_of_week,
            description,
            st.session_state['points'],
        )
        st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
        st.session_state['survey'] = False
        st.rerun()

    # st.sidebar.write("Current Points:")
    # st.sidebar.json(st.session_state['points'])

    st.sidebar.markdown('---')
    st.sidebar.markdown('For a more detailed survey, click the link or scan the QR code:')
    st.sidebar.markdown('[https://arcg.is/1GK5jP0](https://arcg.is/1GK5jP0)')
    st.sidebar.image('static/Getting Lost Survey.png', width=200)

import streamlit as st
import folium
from folium.plugins import Geocoder, MiniMap
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import psycopg2
from geopy import distance


st.set_page_config(layout='wide')


@st.cache_resource
def connect_to_db():
    return psycopg2.connect(
        dbname=st.secrets['dbname'],
        user=st.secrets['user'],
        password=st.secrets['password'],
        host=st.secrets['host'],
        port=st.secrets['port'],
        sslmode=st.secrets['sslmode'],
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


def create_map(points, center=None, zoom=14):
    if not center:
        loc = get_geolocation()
        if loc:
            center = [loc['coords']['latitude'], loc['coords']['longitude']]
        else:
            center = [55.87245110807691, -4.290001402160369]

    m = folium.Map(location=center, zoom_start=zoom, control_scale=True, Tiles=None)
    Geocoder().add_to(m)
    MiniMap().add_to(m)
    OpenStreetMap_HOT = folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        attr='Humanitarian OpenStreetMap Team',
        name='OpenStreetMap_HOT',
        overlay=False,
        control=True,
    )
    OpenStreetMap_HOT.add_to(m)
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
                tooltip='Where you began'
                if point_type == 'start'
                else 'Where you next knew where your where'
                if point_type == 'end'
                else 'Where you got lost',
                draggable=True,
            ).add_to(m)
    return m


# Main code - loop?
# Initialize session state for points if not already done
if 'points' not in st.session_state:
    st.session_state['points'] = {'start': None, 'lost': None, 'end': None}
if 'survey' not in st.session_state:
    st.session_state['survey'] = False
if 'point_type' not in st.session_state:
    st.session_state['point_type'] = 'start'
if 'map_center' not in st.session_state:
    st.session_state['map_center'] = None
if 'map_zoom' not in st.session_state:
    st.session_state['map_zoom'] = 14
if 'pts_valid' not in st.session_state:
    st.session_state['pts_valid'] = False

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
st.title(
    'Step 1 - Add markers that show your :red[last known position], '
    'where :orange[you got lost] and '
    'where :blue[you next knew where you were] on the Map'
)
st.markdown("""
            Please mark on the map roughly where you were coming from and going to
            and where you got lost.  You can drag the flags to the position you want,
            if necessary zoom in and move them again.
            Then check as many of the reasons on the right for getting lost as apply.
            Finally, please click the submit button to send us your information.
            """)
# Custom buttons for selecting point type
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        ':red[Last known position]',
        key='start-button',
        help='Place a marker on the corresponding map location',
        use_container_width=True,
    ):
        st.session_state['point_type'] = 'start'
        st.markdown(
            '<div class="start-button">Last known position Point</div>', unsafe_allow_html=True
        )

with col2:
    if st.button(
        ':orange[Where you got lost]',
        key='lost-button',
        help='Place a marker on the corresponding map location',
        use_container_width=True,
    ):
        st.session_state['point_type'] = 'lost'
        st.markdown('<div class="lost-button">Where you got lost</div>', unsafe_allow_html=True)

with col3:
    if st.button(
        ':blue[Where you next knew where you where]',
        key='end-button',
        help='Place a marker on the corresponding map location',
        use_container_width=True,
    ):
        st.session_state['point_type'] = 'end'
        st.markdown(
            '<div class="end-button">Where you next knew where you were</div>',
            unsafe_allow_html=True,
        )


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
    map_output = st_folium(folium_map, width='100%', height=500)
    print(f"{folium_map=}")
    print(f"{map_output=}")

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
    # why are we remaking the map here? - see https://github.com/GDSGlasgow/getting-lost/issues/17
    map_placeholder.empty()
    with map_placeholder.container():
        folium_map = create_map(
            st.session_state['points'],
            center=st.session_state['map_center'],
            zoom=st.session_state['map_zoom'],
        )
        st_folium(folium_map, width='100%', height=500)

# check if there are 3 points on the map - if there are set `survey` true
if all(st.session_state['points'].values()) and not st.session_state['pts_valid']:
    for pointType, point in st.session_state['points'].items():
        print(f"{pointType=}")
        if 'start' == pointType:
            start = point
        if 'end' == pointType:
            end = point
        if 'lost' == pointType:
            lost = point
    d1 = distance.distance(start, lost).m
    d2 = distance.distance(end, lost).m
    print(f"{d1=} {d2=}")
    if d1 < 1000 and d2 < 1000:
        st.session_state['pts_valid'] = True
    else:
        print("Too far apart")


elif all(st.session_state['points'].values()) and not st.session_state['survey']:
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

# 3 markers are placed on the map in a valid configuration
if st.session_state['survey']:
    # TODO remove clear markers button, lock locations?
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

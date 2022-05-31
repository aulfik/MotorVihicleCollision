import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.figure_factory as ff

DATA_URL = (
"https://data.cityofnewyork.us/resource/h9gi-nx95.csv"
)

st.title("Motor Vihicle Collision in New York City 2021")
st.markdown("This application is a Strimlit dashboard that can be used"
"to analyze motor vehicle collisions in NYC 🗽💥🚗")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[["crash_date", "crash_time"]])
    data.dropna(subset=['latitude', 'longitude'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(1000000)
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of person injured in vehicle collisions", 0, 19, 2)
st.map(data.query("number_of_persons_injured >= @injured_people")[["latitude", "longitude"]].dropna(how="any"), zoom=8)


st.header("How many collusions occur during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) %24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=['longitude', 'latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) %24))
filtered = data[
    (data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour < (hour +1))
]
hist= np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = ff.create_distplot(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Top 5 dengerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians', 'Cyclist', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("number_of_pedestrians_injured >= 1")[["on_street_name", "number_of_pedestrians_injured"]].sort_values(by=['number_of_pedestrians_injured'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclist':
    st.write(original_data.query("number_of_cyclist_injured >= 1")[["on_street_name", "number_of_cyclist_injured"]].sort_values(by=['number_of_cyclist_injured'], ascending=False).dropna(how='any')[:5])

else :
    st.write(original_data.query("number_of_motorist_injured >= 1")[["on_street_name", "number_of_motorist_injured"]].sort_values(by=['number_of_motorist_injured'], ascending=False).dropna(how='any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)

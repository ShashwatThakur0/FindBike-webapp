from helpers import *
import streamlit as st

# URL to fetch bike share data 
station_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status"
latlon_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information"


st.title('Red deer Bike share station status')
st.markdown (' This dashboard tracks bike availability at each bike share station in Toronto.')

# fetch data for initial visualization 
data_df = query_station_status(station_url) # get station status 
latlon_df = get_station_latlon(latlon_url)
data = join_latlon(data_df, latlon_df)

col1, col2, col3 = st.columns(3)
with col1:
  st.metric(label = 'Bike Available Now', value = sum(data['num_bikes_available']))
  st.metric(label = 'EBikes Available Now', value = sum(data['ebike']) )
with col2:
  st.metric(label = 'Stations with Available Bikes', value = len(data[data['num_bikes_available'] > 0]))
  st.metric(label = 'stations with Availabel E-Bikes', value = 
  len(data[data['ebike'] > 0]))
with col3:
  st.metric(label = 'Stations with Empty Docks', value = len(data[data['num_docks_available'] > 0 ]))

with st.sidebar:
    st.selectbox(
       "Are you looking to rent or return a bike?",
       ('Rent', 'Return')
    )


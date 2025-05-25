import streamlit as st  # Import Streamlit for creating web apps
import requests  # Import requests for making HTTP requests
import pandas as pd  # Import pandas for data manipulation
import datetime as dt  # Import datetime for handling date and time
import urllib  # Import urllib for URL handling
import json  # Import json for handling JSON data
import time  # Import time for time-related functions
from helpers import *  # Import custom helper functions
import folium  # Import folium for creating interactive maps
from streamlit_folium import folium_static  # Import folium_static to render Folium maps in Streamlit
import os  # Import os for file path operations
from folium.plugins import MarkerCluster, HeatMap, Fullscreen, MeasureControl, LocateControl  # Import additional folium plugins

# URL to fetch bike share data 
station_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status"
latlon_url = "https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information"

# Load custom CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS
load_css()

# Display logo and app header
logo_path = os.path.join(os.path.dirname(__file__), "static", "assets", "logo.svg")
with open(logo_path, "r") as f:
    logo_svg = f.read()

# App header with logo and title
header_col1, header_col2 = st.columns([1, 3])
with header_col1:
    st.markdown(f"{logo_svg}", unsafe_allow_html=True)
with header_col2:
    st.markdown('<h1 class="main-title">Toronto Bike Share Finder</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Find available bikes and docks in real-time across Toronto</p>', unsafe_allow_html=True)

# Add a horizontal divider
st.markdown("<hr style='margin: 1rem 0; border: 0; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

# Fetch data for initial visualization
data_df = query_station_status(station_url)  # Get station status data
latlon_df = get_station_latlon(latlon_url)  # Get station latitude and longitude data
data = join_latlon(data_df, latlon_df)  # Join the status data with the location data

# Display metrics in styled cards
st.markdown('<h2 style="color: #1e88e5; margin-bottom: 1rem;">System Status</h2>', unsafe_allow_html=True)

# Create metrics with improved styling
metrics_container = st.container()
with metrics_container:
    # Add custom CSS for the metrics container
    st.markdown("""
    <style>
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e88e5;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #757575;
        margin-bottom: 0.5rem;
    }
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a 2x3 grid for metrics
    col1, col2, col3 = st.columns(3)
    
    # Total bikes available
    with col1:
        total_bikes = sum(data['num_bikes_available'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🚲</div>
            <div class="metric-value">{total_bikes}</div>
            <div class="metric-label">Bikes Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    # E-bikes available
    with col2:
        total_ebikes = sum(data["ebike"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{total_ebikes}</div>
            <div class="metric-label">E-Bikes Available</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Mechanical bikes available
    with col3:
        total_mechanical = sum(data["mechanical"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🔧</div>
            <div class="metric-value">{total_mechanical}</div>
            <div class="metric-label">Mechanical Bikes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row of metrics
    col4, col5, col6 = st.columns(3)
    
    # Stations with available bikes
    with col4:
        stations_with_bikes = len(data[data['num_bikes_available'] > 0])
        total_stations = len(data)
        percentage = round((stations_with_bikes / total_stations) * 100)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📍</div>
            <div class="metric-value">{stations_with_bikes}</div>
            <div class="metric-label">Stations with Bikes ({percentage}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stations with e-bikes
    with col5:
        stations_with_ebikes = len(data[data['ebike'] > 0])
        percentage_ebike = round((stations_with_ebikes / total_stations) * 100)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">{stations_with_ebikes}</div>
            <div class="metric-label">Stations with E-Bikes ({percentage_ebike}%)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stations with empty docks
    with col6:
        stations_with_docks = len(data[data['num_docks_available'] > 0])
        percentage_docks = round((stations_with_docks / total_stations) * 100)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🔒</div>
            <div class="metric-value">{stations_with_docks}</div>
            <div class="metric-label">Stations with Empty Docks ({percentage_docks}%)</div>
        </div>
        """, unsafe_allow_html=True)

# Add a horizontal divider
st.markdown("<hr style='margin: 1rem 0; border: 0; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)

# Track metrics for delta calculation
deltas = [
    sum(data['num_bikes_available']),
    sum(data["ebike"]),
    len(data[data['num_bikes_available'] > 0]),
    len(data[data['ebike'] > 0]),
    len(data[data['num_docks_available'] > 0])
]

# Initialize variables for user input and state
iamhere = 0
iamhere_return = 0
findmeabike = False
findmeadock = False
input_bike_modes = []

# Enhanced sidebar with better UI
with st.sidebar:
    # Add sidebar header with styling
    st.markdown('<div style="text-align: center; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    st.markdown(f"{logo_svg}", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<h3 style="color: #1e88e5; margin-bottom: 1rem;">Find Your Ride</h3>', unsafe_allow_html=True)
    
    # Add styled container for the form
    st.markdown("""
    <style>
    .sidebar-form {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .form-header {
        font-weight: 600;
        color: #1e88e5;
        margin-bottom: 0.5rem;
    }
    .form-description {
        font-size: 0.9rem;
        color: #757575;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main selection for rent/return
    st.markdown('<div class="sidebar-form">', unsafe_allow_html=True)
    bike_method = st.selectbox(
        "What would you like to do?", 
        ("Rent a bike", "Return a bike"),
        format_func=lambda x: "🚲 " + x if x == "Rent a bike" else "🔒 " + x
    )
    
    # Description based on selection
    if bike_method == "Rent a bike":
        st.markdown('<p class="form-description">Find available bikes near your location</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="form-description">Find available docks to return your bike</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Rent a bike form
    if bike_method == "Rent a bike":
        st.markdown('<div class="sidebar-form">', unsafe_allow_html=True)
        st.markdown('<p class="form-header">Bike Preferences</p>', unsafe_allow_html=True)
        
        # Improved multi-select with icons
        input_bike_modes = st.multiselect(
            "What type of bike are you looking for?", 
            ["ebike", "mechanical"],
            format_func=lambda x: "⚡ E-Bike" if x == "ebike" else "🔧 Mechanical Bike"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Location form
        st.markdown('<div class="sidebar-form">', unsafe_allow_html=True)
        st.markdown('<p class="form-header">📍 Your Location</p>', unsafe_allow_html=True)
        input_street = st.text_input("Street Address", placeholder="e.g. 100 Queen Street West")
        
        # Use columns for city and country to save space
        loc_col1, loc_col2 = st.columns(2)
        with loc_col1:
            input_city = st.text_input("City", "Toronto")
        with loc_col2:
            input_country = st.text_input("Country", "Canada")
            
        # Transportation option with better UI
        drive = st.checkbox("🚗 I'm driving there", help="Check this if you plan to drive to the station")
        
        # Primary button with better styling
        findmeabike = st.button(
            "🔍 Find me a bike!", 
            type="primary",
            use_container_width=True
        )
        
        # Error handling with better styling
        if findmeabike:
            if input_street != "":
                iamhere = geocode(input_street + " " + input_city + " " + input_country)
                if iamhere == '':
                    st.error("📍 We couldn't find that address. Please check and try again.")
            else:
                st.warning("📍 Please enter your street address so we can find bikes near you.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Return a bike form
    elif bike_method == "Return a bike":
        # Location form for return
        st.markdown('<div class="sidebar-form">', unsafe_allow_html=True)
        st.markdown('<p class="form-header">📍 Your Location</p>', unsafe_allow_html=True)
        input_street_return = st.text_input("Street Address", placeholder="e.g. 100 Queen Street West")
        
        # Use columns for city and country to save space
        loc_col1, loc_col2 = st.columns(2)
        with loc_col1:
            input_city_return = st.text_input("City", "Toronto")
        with loc_col2:
            input_country_return = st.text_input("Country", "Canada")
        
        # Primary button with better styling
        findmeadock = st.button(
            "🔍 Find me a dock!", 
            type="primary",
            use_container_width=True
        )
        
        # Error handling with better styling
        if findmeadock:
            if input_street_return != "":
                iamhere_return = geocode(input_street_return + " " + input_city_return + " " + input_country_return)
                if iamhere_return == '':
                    st.error("📍 We couldn't find that address. Please check and try again.")
            else:
                st.warning("📍 Please enter your street address so we can find docks near you.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add help information at the bottom of sidebar
    st.markdown('<div style="margin-top: 2rem; padding: 1rem; background-color: #f5f7fa; border-radius: 8px; font-size: 0.9rem;">', unsafe_allow_html=True)
    st.markdown('<p style="color: #1e88e5; font-weight: 600; margin-bottom: 0.5rem;">💡 Tips</p>', unsafe_allow_html=True)
    st.markdown('<ul style="color: #757575; margin: 0; padding-left: 1.2rem;">', unsafe_allow_html=True)
    st.markdown('<li>Enter a complete street address for best results</li>', unsafe_allow_html=True)
    st.markdown('<li>The map will show the nearest station with available bikes/docks</li>', unsafe_allow_html=True)
    st.markdown('<li>Travel time estimates are based on walking speed</li>', unsafe_allow_html=True)
    st.markdown('</ul>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced map visualization section
st.markdown('<h2 style="color: #1e88e5; margin-bottom: 1rem;">Bike Station Map</h2>', unsafe_allow_html=True)

# Function to create a better styled popup
def create_popup_html(row):
    # Determine status classes based on availability
    bike_status_class = "status-available" if row['num_bikes_available'] > 3 else "status-limited" if row['num_bikes_available'] > 0 else "status-unavailable"
    ebike_status_class = "status-available" if row['ebike'] > 0 else "status-unavailable"
    mechanical_status_class = "status-available" if row['mechanical'] > 0 else "status-unavailable"
    dock_status_class = "status-available" if row['num_docks_available'] > 0 else "status-unavailable"
    
    # Create styled HTML for popup
    html = f"""
    <div style="font-family: 'Inter', sans-serif; min-width: 200px; max-width: 300px;">
        <h3 style="margin: 0 0 10px 0; color: #1e88e5; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px;">
            Station {row['station_id']}
        </h3>
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 500;">Total Bikes:</span>
                <span class="{bike_status_class}">{row['num_bikes_available']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 500;">E-Bikes:</span>
                <span class="{ebike_status_class}">{row['ebike']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: 500;">Mechanical Bikes:</span>
                <span class="{mechanical_status_class}">{row['mechanical']}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="font-weight: 500;">Empty Docks:</span>
                <span class="{dock_status_class}">{row['num_docks_available']}</span>
            </div>
        </div>
    </div>
    """
    return html

# Function to create a better map
def create_enhanced_map(center, data, zoom_level=13):
    # Create a map with a modern style
    m = folium.Map(
        location=center,
        zoom_start=zoom_level,
        tiles='cartodbpositron',
        control_scale=True
    )
    
    # Add a fullscreen control
    folium.plugins.Fullscreen().add_to(m)
    
    # Add a locate control to help users find their position
    folium.plugins.LocateControl(auto_start=False, fly_to=True).add_to(m)
    
    # Create a marker cluster for better performance with many markers
    marker_cluster = MarkerCluster(
        name="Bike Stations",
        overlay=True,
        control=False,
        icon_create_function=None
    )
    
    # Add markers for each station
    for _, row in data.iterrows():
        # Determine marker color and icon based on availability
        if row['num_bikes_available'] > 3:
            marker_color = "green"
            icon_color = "white"
            prefix = "fa"
            icon = "bicycle"
        elif row['num_bikes_available'] > 0:
            marker_color = "orange"
            icon_color = "white"
            prefix = "fa"
            icon = "bicycle"
        else:
            marker_color = "red"
            icon_color = "white"
            prefix = "fa"
            icon = "times-circle"
        
        # Create a custom icon
        icon = folium.Icon(
            color=marker_color,
            icon_color=icon_color,
            icon=icon,
            prefix=prefix
        )
        
        # Create popup with styled HTML
        popup_html = create_popup_html(row)
        popup = folium.Popup(folium.Html(popup_html, script=True), max_width=300)
        
        # Add marker to cluster
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=popup,
            icon=icon,
            tooltip=f"Station {row['station_id']} - {row['num_bikes_available']} bikes available"
        ).add_to(marker_cluster)
    
    # Add the marker cluster to the map
    marker_cluster.add_to(m)
    
    # Add a heatmap layer for bike availability
    heat_data = [[row['lat'], row['lon'], row['num_bikes_available']] for _, row in data.iterrows() if row['num_bikes_available'] > 0]
    if heat_data:  # Only add heatmap if there's data
        folium.plugins.HeatMap(
            heat_data,
            radius=15,
            blur=10,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'},
            name="Bike Availability Heatmap",
            show=False  # Hidden by default
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Display map based on user selection
map_container = st.container()
with map_container:
    # Add custom CSS for the map container
    st.markdown("""
    <style>
    .map-container {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    
    # Initial map setup based on user selection
    if (bike_method == "Return a bike" and findmeadock == False) or (bike_method == "Rent a bike" and findmeabike == False):
        # Toronto city center coordinates
        center = [43.65306613746548, -79.38815311015]
        
        # Create and display the enhanced map
        m = create_enhanced_map(center, data)
        folium_static(m, width=800, height=500)
        
        # Add map legend and explanation
        legend_col1, legend_col2, legend_col3 = st.columns(3)
        with legend_col1:
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background-color: #43a047; width: 15px; height: 15px; border-radius: 50%; margin-right: 8px;"></div>
                <span style="font-size: 0.9rem;">Many bikes available (4+)</span>
            </div>
            """, unsafe_allow_html=True)
        with legend_col2:
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background-color: #ff9800; width: 15px; height: 15px; border-radius: 50%; margin-right: 8px;"></div>
                <span style="font-size: 0.9rem;">Limited bikes (1-3)</span>
            </div>
            """, unsafe_allow_html=True)
        with legend_col3:
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="background-color: #e53935; width: 15px; height: 15px; border-radius: 50%; margin-right: 8px;"></div>
                <span style="font-size: 0.9rem;">No bikes available</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced results section with better styling
results_container = st.container()

# Function to create a better route map
def create_route_map(user_location, station_location, station_id, mode="rent"):
    # Center the map on the user's location
    center = user_location
    
    # Create a map with a modern style and higher zoom level for detailed view
    m = folium.Map(
        location=center,
        zoom_start=15,
        tiles='cartodbpositron',
        control_scale=True
    )
    
    # Add a fullscreen control
    folium.plugins.Fullscreen().add_to(m)
    
    # Add a locate control to help users find their position
    folium.plugins.LocateControl(auto_start=False, fly_to=True).add_to(m)
    
    # Add user marker with custom styling
    folium.Marker(
        location=user_location,
        popup=folium.Popup("<b>Your Location</b>", max_width=200),
        tooltip="You are here",
        icon=folium.Icon(color="blue", icon="user", prefix="fa")
    ).add_to(m)
    
    # Add station marker with custom styling
    if mode == "rent":
        station_popup = f"<b>Bike Station {station_id}</b><br>Rent your bike here"
        tooltip_text = "Rent bikes here"
    else:  # mode == "return"
        station_popup = f"<b>Bike Station {station_id}</b><br>Return your bike here"
        tooltip_text = "Return bikes here"
    
    folium.Marker(
        location=(station_location[0], station_location[1]),
        popup=folium.Popup(station_popup, max_width=200),
        tooltip=tooltip_text,
        icon=folium.Icon(color="green", icon="bicycle", prefix="fa")
    ).add_to(m)
    
    # Get route coordinates and duration
    coordinates, duration = run_osrm([station_id, station_location[0], station_location[1]], user_location)
    
    # Add route line with better styling
    route = folium.PolyLine(
        locations=coordinates,
        color="#1e88e5",  # Primary blue color
        weight=5,
        opacity=0.8,
        tooltip=f"Travel time: {duration} minutes",
        dash_array="10, 10"  # Create a dashed line for better visibility
    )
    route.add_to(m)
    
    # Add distance markers along the route
    folium.plugins.MeasureControl(position='topright', primary_length_unit='meters').add_to(m)
    
    # Fit the map to show both markers and the route
    bounds = [user_location, (station_location[0], station_location[1])]
    m.fit_bounds(bounds, padding=(30, 30))
    
    return m, duration

# Function to display station details card
def display_station_details(station_id, data, duration, mode="rent"):
    # Create a container for this station details to isolate any errors
    station_container = st.container()
    
    with station_container:
        # Get station data - convert station_id to integer for proper comparison
        try:
            # Handle different types of station_id (int, string, pandas Series)
            if hasattr(station_id, 'item'):
                station_id = station_id.item()
            station_id = int(station_id)
            
            # Find the station in the data
            station_data = data[data['station_id'] == station_id]
            
            # Check if we found the station
            if len(station_data) == 0:
                # Use a placeholder instead of error to avoid persistent messages
                st.info("Loading station details...")
                return
            
            # Get the first row of matching data
            station_data = station_data.iloc[0]
        except (ValueError, TypeError, IndexError) as e:
            # Use a placeholder instead of error to avoid persistent messages
            st.info("Loading station details...")
            return
    
    # Add CSS only once to avoid duplication
    if not hasattr(st.session_state, 'station_card_css_added'):
        st.markdown("""
        <style>
        .station-card {
            background-color: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }
        .station-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 0.5rem;
        }
        .station-icon {
            font-size: 2rem;
            margin-right: 1rem;
            color: #1e88e5;
        }
        .station-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #1e88e5;
            margin: 0;
        }
        .station-subtitle {
            font-size: 1rem;
            color: #757575;
            margin: 0;
        }
        .station-detail {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        .detail-label {
            font-weight: 500;
            color: #333333;
        }
        .detail-value {
            font-weight: 600;
        }
        .travel-time {
            background-color: #f5f7fa;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: center;
        }
        .time-value {
            font-size: 2rem;
            font-weight: 700;
            color: #43a047;
            margin: 0.5rem 0;
        }
        .time-label {
            font-size: 1rem;
            color: #757575;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.station_card_css_added = True
    
    # Station card with details
    if mode == "rent":
        icon = "🚲"
        title = f"Bike Station {station_id}"
        subtitle = "Bikes available for rent"
    else:  # mode == "return"
        icon = "🔒"
        title = f"Bike Station {station_id}"
        subtitle = "Docks available for return"
    
    # Get values with error handling
    try:
        num_bikes = station_data['num_bikes_available']
        ebikes = station_data['ebike']
        mechanical = station_data['mechanical']
        docks = station_data['num_docks_available']
    except KeyError as e:
        st.error(f"Missing data field: {e}. Please check the data source.")
        # Set default values
        num_bikes = 0
        ebikes = 0
        mechanical = 0
        docks = 0
    
    # Create the HTML for the station card
    station_html = f"""
    <div class="station-card">
        <div class="station-header">
            <div class="station-icon">{icon}</div>
            <div>
                <h3 class="station-title">{title}</h3>
                <p class="station-subtitle">{subtitle}</p>
            </div>
        </div>
        
        <div class="station-detail">
            <span class="detail-label">Total Bikes Available:</span>
            <span class="detail-value">{num_bikes}</span>
        </div>
        <div class="station-detail">
            <span class="detail-label">E-Bikes Available:</span>
            <span class="detail-value">{ebikes}</span>
        </div>
        <div class="station-detail">
            <span class="detail-label">Mechanical Bikes Available:</span>
            <span class="detail-value">{mechanical}</span>
        </div>
        <div class="station-detail">
            <span class="detail-label">Empty Docks:</span>
            <span class="detail-value">{docks}</span>
        </div>
        
        <div class="travel-time">
            <div class="time-label">Estimated Travel Time</div>
            <div class="time-value">{duration} min</div>
            <div class="time-label">Walking distance</div>
        </div>
    </div>
    """
    
    # Display the station card
    st.markdown(station_html, unsafe_allow_html=True)

# Logic for finding a bike - enhanced version
with results_container:
    if findmeabike:
        if input_street != "":
            if iamhere != "":
                # Display a loading spinner while processing
                with st.spinner("Finding the best bike station for you..."):
                    # Get bike availability
                    chosen_station = get_bike_availability(iamhere, data, input_bike_modes)
                    
                    # Make sure we have a valid station ID (convert from pandas Series if needed)
                    station_id = chosen_station[0]
                    if hasattr(station_id, 'item'):
                        station_id = station_id.item()
                    
                    # Display results header
                    st.markdown('<h2 style="color: #1e88e5; margin-bottom: 1rem;">Your Recommended Bike Station</h2>', unsafe_allow_html=True)
                    
                    # Create two columns for results display
                    result_col1, result_col2 = st.columns([2, 1])
                    
                    with result_col1:
                        # Create and display the route map
                        route_map, duration = create_route_map(
                            iamhere, 
                            (chosen_station[1], chosen_station[2]), 
                            station_id, 
                            mode="rent"
                        )
                        folium_static(route_map, width=600, height=400)
                    
                    with result_col2:
                        # Display station details
                        display_station_details(station_id, data, duration, mode="rent")

# Logic for finding a dock - enhanced version
with results_container:
    if findmeadock:
        if input_street_return != "":
            if iamhere_return != "":
                # Display a loading spinner while processing
                with st.spinner("Finding the best dock for your bike return..."):
                    # Get dock availability
                    chosen_station = get_dock_availability(iamhere_return, data)
                    
                    # Make sure we have a valid station ID (convert from pandas Series if needed)
                    station_id = chosen_station[0]
                    if hasattr(station_id, 'item'):
                        station_id = station_id.item()
                    
                    # Display results header
                    st.markdown('<h2 style="color: #1e88e5; margin-bottom: 1rem;">Your Recommended Return Station</h2>', unsafe_allow_html=True)
                    
                    # Create two columns for results display
                    result_col1, result_col2 = st.columns([2, 1])
                    
                    with result_col1:
                        # Create and display the route map
                        route_map, duration = create_route_map(
                            iamhere_return, 
                            (chosen_station[1], chosen_station[2]), 
                            station_id, 
                            mode="return"
                        )
                        folium_static(route_map, width=600, height=400)
                    
                    with result_col2:
                        # Display station details
                        display_station_details(station_id, data, duration, mode="return")
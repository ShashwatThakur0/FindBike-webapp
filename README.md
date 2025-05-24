# FindBike-webapp

## Overview
FindBike-webapp is a Streamlit-based web application that helps users locate and navigate to Toronto Bike Share stations. The app provides real-time information about bike and dock availability across the city, allowing users to easily find bikes to rent or docks to return bikes.

## Features
- **Real-time Bike Availability**: Track the number of available bikes (both mechanical and e-bikes) at each station
- **Interactive Map**: Visualize all bike stations with color-coded markers indicating availability
- **Location-based Search**: Find the nearest bike or dock based on your current location
- **Route Planning**: Get directions and estimated travel time to the nearest bike station or dock
- **Filtering Options**: Search specifically for mechanical bikes or e-bikes based on preference

## Technology Stack
- **Frontend**: Streamlit for the web interface
- **Data Visualization**: Folium for interactive maps
- **Geolocation Services**: Geopy for geocoding and distance calculations
- **Routing**: OSRM (Open Source Routing Machine) for route planning and travel time estimation
- **Data Processing**: Pandas for data manipulation and analysis

## Data Sources
- Toronto Bike Share System API for real-time station status and information

## Installation

### Prerequisites
- Python 3.8
- Conda (for environment management)

### Setup

1. Clone the repository
2. Create and activate the conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate bikeshare_streamlit
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage
1. Select whether you want to rent or return a bike using the sidebar.
2. For renting:
   - Choose the type of bike you're looking for (mechanical, e-bike, or both).
   - Enter your current location.
   - Click "Find me a bike!" to locate the nearest available bike.
3. For returning:
   - Enter your current location.
   - Click "Find me a dock!" to locate the nearest available dock.
4. The app will display an interactive map with your location, the recommended station, and the route between them.

## Project Structure
- `app.py`: Main application file containing the Streamlit interface and core functionality
- `helpers.py`: Helper functions for data processing, geocoding, and routing
- `environment.yml`: Conda environment configuration file

## Contributing
Contributions to improve FindBike-webapp are welcome. Please feel free to submit a pull request or open an issue to discuss potential changes or enhancements.
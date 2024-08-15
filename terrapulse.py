import streamlit as st
import google.generativeai as genai
import googlemaps
from datetime import datetime
from PIL import Image as PILImage
import folium
from streamlit_folium import folium_static
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import plotly.graph_objs as go
import re

# Load environment variables
load_dotenv()

# Initialize APIs
MAP_API_KEY = os.getenv('MAP_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Configure the page
st.set_page_config(
    page_title="TerraPulse", 
    page_icon="🌍", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Custom CSS for typography, headings, and styling
st.markdown(
    """
    <style>
    body {
        background-color: #f5f7fa;
        font-family: 'Poppins', sans-serif;
    }
    h1, h2, h3 {
        color: #008080;
        font-weight: 700;
    }
    h1 {
        font-size: 3em;
        text-align: center;
        margin-bottom: 20px;
    }
    h2 {
        font-size: 2.2em;
        margin-top: 20px;
    }
    h3 {
        font-size: 1.8em;
    }
    .stApp {
        padding: 20px;
        border-radius: 10px;
        background-color: #f5f7fa;
    }
    .stButton>button {
        background-color: #008080;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 18px;
        border-radius: 10px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #006666;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 12px;
        font-size: 18px;
    }
    .stSidebar > div {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 10px;
    }
    .chat-message {
        font-size: 18px;
        font-weight: bold;
        color: #008080;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar with option menu
selected_option = option_menu(
    menu_title="🌎 TerraPulse",  
    options=["Home", "Waste-wise", "EcoRoute: Sustainable Travel Planner"],  
    icons=["house", "recycle", "globe"],  
    menu_icon="cast",  
    default_index=0,  
    orientation="horizontal",
    styles={
        "container": {"padding": "5!important", "background-color": "#e0f7fa"},
        "icon": {"color": "#006666", "font-size": "25px"}, 
        "nav-link": {"font-size": "20px", "text-align": "center", "margin":"0px", "--hover-color": "#e0f7fa"},
        "nav-link-selected": {"background-color": "#008080"},
    }
)

# Home page
if selected_option == "Home":
    st.title("🌍 Welcome to TerraPulse")
    st.markdown(
        """
        **TerraPulse** is your go-to application for a sustainable future. 🌱  
        Whether you're looking to classify waste for proper disposal or planning an eco-friendly route for your next trip, TerraPulse has got you covered.

        **Features:**
        - **♻️ Waste-wise:** Upload images of trash items, and TerraPulse will classify them into recyclables, compostables, hazardous materials, and general waste.  
        - **🌍 EcoRoute:** Plan your travel with the environment in mind. Get the most sustainable routes, transportation suggestions, and carbon footprint estimates.

        **Let's work together for a cleaner and greener planet!** 🌍💚
        """
    )

# Load Gemini Pro Vision model
@st.cache_resource
def load_model():
    if not GOOGLE_API_KEY:
        st.error("Google API Key not found in .env file.")
        st.stop()
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')

# Analyze image function
def analyze_image(image, prompt):
    model = load_model()
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        return None
    
def parse_modes_and_footprints(response_text):
    # Regular expression to match the rows of the table
    row_pattern = re.compile(r'\| (.+?) \| ([\d.]+) \|')
    
    # Find all rows in the table
    matches = row_pattern.findall(response_text)
    
    modes = []
    carbon_footprints = []
    
    for match in matches:
        mode = match[0].strip()
        footprint = float(match[1].strip())
        modes.append(mode)
        carbon_footprints.append(footprint)
    
    if not modes or not carbon_footprints:
        raise ValueError("No valid data found in the response text")
    
    return modes, carbon_footprints


# Waste-wise section
if selected_option == "Waste-wise":
    st.title("♻️ Waste-wise")

    st.subheader("📤 Upload Image")
    uploaded_files = st.file_uploader("Choose trash images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    prompt = "Analyze the image of trash items. Classify the waste into categories such as recyclables, compostables, hazardous materials, and general waste. Based on the classification, guide the user on which specific color dustbin (e.g., recycling, compost, hazardous, or landfill) to dispose of the items."

    if uploaded_files:
        analyze_button = st.button("🔍 Analyze Image")
        for uploaded_file in uploaded_files:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🖼️ Uploaded Image")
                image = PILImage.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)

            with col2:
                st.subheader("🧠 Image Analysis")
                if analyze_button:
                    with st.spinner("Analyzing the image..."):
                        analysis = analyze_image(image, prompt)
                        if analysis:
                            st.markdown(analysis)
                else:
                    st.info("Click 'Analyze Image' to start the analysis.")

# EcoRoute section
if selected_option == "EcoRoute: Sustainable Travel Planner":
    st.title("🌍 EcoRoute: Sustainable Travel Planner")

    gmaps = googlemaps.Client(key=MAP_API_KEY)
    model = load_model()

    # User inputs
    start_location = st.text_input("Enter your start location")
    destination_location = st.text_input("Enter your destination location")
    no_of_people = st.selectbox(
        "Choose the number of people",
        ["1", "2", "3-6", "6-10", "10+"]
    )

    def calculate_trees(carbon_footprint):
        """Calculate the number of trees required to offset the carbon footprint."""
        carbon_per_tree = 0.02177  # Metric tons of CO₂ absorbed per year by one tree
        return carbon_footprint / carbon_per_tree

    if st.button("Find Eco-Friendly Route"):
        if start_location and destination_location:
            # Geocoding the start and end locations
            geocode_start = gmaps.geocode(start_location)
            geocode_end = gmaps.geocode(destination_location)
            
            if geocode_start and geocode_end:
                start_coords = geocode_start[0]['geometry']['location']
                end_coords = geocode_end[0]['geometry']['location']

                # Prompt Google Gemini API to suggest an eco-friendly mode of transport
                prompt = f"""You are an eco-friendly mode of transport suggestor. Your job is to provide me with the best routes in bullet points in a comprehensive manner. Suggest the most eco-friendly mode of transport between {start_location} and {destination_location}. Here is the number of people traveling: {no_of_people}. Consider all the above parameters to provide the result in the below format:

Distance: [distance]

Mode 1: Train
- Time: 2h 30m
- Feasibility: High
- Route: Detailed route description
- Carbon footprint (unit): 30.0

Mode 2: Bus
- Time: 3h 00m
- Feasibility: Medium
- Route: Detailed route description
- Carbon footprint (unit): 50.0

Mode 3: Car
- Time: 1h 15m
- Feasibility: High
- Route: Detailed route description
- Carbon footprint (unit): 120.0

Use this exact format. carbon footprint output should only be a single number in float format, nothing else. Generate a table of the different modes of transport vs their carbon footprint.
Similarly, using your own knowledge, provide eco-friendly routes and the most eco-friendly option along with the estimated carbon footprint.
"""

                response = model.generate_content([prompt])
                eco_friendly_modes = response.text.strip()

                st.write(f"**Suggested Eco-Friendly Modes:**\n{eco_friendly_modes}")

                try:
                    modes, carbon_footprints = parse_modes_and_footprints(eco_friendly_modes)

                    # Plotting the pie chart using Plotly
                    if modes and carbon_footprints:
                        fig = go.Figure(data=[go.Pie(labels=modes, values=carbon_footprints)])
                        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20)
                        fig.update_layout(title="Carbon Footprint Distribution by Mode of Transport", margin=dict(l=0, r=0, t=40, b=0))

                        # Adjust layout to ensure map and pie chart do not overlap
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            # Displaying the map
                            st.subheader("EcoRoute Map View")
                            # Create a map centered at the midpoint
                            midpoint = [(start_coords['lat'] + end_coords['lat']) / 2, (start_coords['lng'] + end_coords['lng']) / 2]
                            m = folium.Map(location=midpoint, zoom_start=8)

                            folium.Marker([start_coords['lat'], start_coords['lng']], popup=start_location, icon=folium.Icon(color='green')).add_to(m)
                            folium.Marker([end_coords['lat'], end_coords['lng']], popup=destination_location, icon=folium.Icon(color='red')).add_to(m)

                            # Draw a line between the start and end locations
                            folium.PolyLine(locations=[(start_coords['lat'], start_coords['lng']), (end_coords['lat'], end_coords['lng'])], color='blue').add_to(m)

                            folium_static(m)

                        with col2:
                            st.plotly_chart(fig, use_container_width=True)
                    
                except ValueError as e:
                    st.error(f"Error parsing the response: {str(e)}")
            
            else:
                st.error("Could not geocode one or both locations. Please check the input.")
        else:
            st.error("Please enter both the start and destination locations.")

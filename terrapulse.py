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

# Waste-wise section
if selected_option == "Waste-wise":
    st.title("♻️ Waste-wise")

    st.subheader("📤 Upload Image")
    uploaded_files = st.file_uploader("Choose trash images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    st.subheader("⚙️ Analysis")
    prompt = "Analyze the image of trash items. Classify the waste into categories such as recyclables, compostables, hazardous materials, and general waste. Based on the classification, guide the user on which specific color dustbin (e.g., recycling, compost, hazardous, or landfill) to dispose of the items."

    analyze_button = st.button("🔍 Analyze Image")

    if uploaded_files:
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
    no_of_people = st.multiselect(
        "Choose the number of people",
        ["1", "2", "3-6", "6-10", "10+"]
    )

    if st.button("Find Eco-Friendly Route"):
        if start_location and destination_location:
            # Geocoding the start and end locations
            geocode_start = gmaps.geocode(start_location)
            geocode_end = gmaps.geocode(destination_location)
            
            if geocode_start and geocode_end:
                start_coords = geocode_start[0]['geometry']['location']
                end_coords = geocode_end[0]['geometry']['location']

                # Prompt Google Gemini API to suggest an eco-friendly mode of transport
                prompt = f"""You are an eco-friendly mode of transport suggestor, your job is to provide me with the best routes in bulletins in a comprehensive manner. Suggest the most eco-friendly mode of transport between {start_location} and {destination_location}, here is the number of people traveling {no_of_people}. Consider all the above parameters to provide the result in the below format:
                Distance: [distance]
                
                Mode 1 (Ex: Train)
                Time: [time taken to travel from start to end location], use your own knowledge
                Feasibility: [Provide How feasible it is]
                Route: [Provide detailed route]

                Similarly using your own knowledge provide eco-friendly routes and the most eco-friendly along with the estimated carbon footprint.
                """
                response = model.generate_content([prompt])
                eco_friendly_mode = response.text.strip().lower()

                # Valid modes of transportation
                valid_modes = ["driving", "walking", "bicycling", "transit"]

                # Check if the suggested mode is valid; default to 'walking' if invalid
                if eco_friendly_mode not in valid_modes:
                    st.warning(f"Suggested mode '{eco_friendly_mode}' is not valid. Defaulting to 'walking'.")
                    eco_friendly_mode = "walking"

                st.write(f"Suggested eco-friendly mode: {eco_friendly_mode.capitalize()}")

                # Get directions based on the suggested eco-friendly mode
                directions = gmaps.directions(
                    (start_coords['lat'], start_coords['lng']),
                    (end_coords['lat'], end_coords['lng']),
                    mode=eco_friendly_mode,
                    departure_time=datetime.now()
                )

                if directions:
                    # Extract route information
                    route = directions[0]
                    st.write("**Route Summary:**")
                    st.write(route['summary'])

                    # Calculate carbon footprint using Google Gemini (Placeholder logic)
                    prompt2 = f"""You are a carbon footprint calculator. I need to determine the carbon emissions for different modes of transportation over a given distance between {start_location} and {destination_location} Please provide the estimated carbon footprint in kilograms of CO2 for the following transportation modes:

1. **Driving**: Calculate the carbon footprint for driving a vehicle over a distance of [Distance] kilometers. Use an average emission factor for a gasoline car (e.g., 0.2 kg CO2 per km).

2. **Public Transit**: Calculate the carbon footprint for traveling by public transit (e.g., bus or train) over a distance of [Distance] kilometers. Use an average emission factor for public transit (e.g., 0.05 kg CO2 per km).

3. **Bicycling**: Calculate the carbon footprint for traveling by bicycle over a distance of [Distance] kilometers. For simplicity, you can consider the footprint as negligible or use an average factor if necessary (e.g., 0.01 kg CO2 per km).

4. **Walking**: Calculate the carbon footprint for walking over a distance of [Distance] kilometers. The footprint is typically negligible, but include it if needed (e.g., 0.01 kg CO2 per km for infrastructure and production).

For each mode of transportation, provide:
- The total carbon footprint in kilograms of CO2.
- A brief explanation of how you derived the emission factors and calculations.

Please ensure the results are presented in a clear and concise manner.
"""
                    response = model.generate_content([prompt2])
                    carbon_footprint = response.text.strip()
                    st.write(f"Estimated Carbon Footprint: {carbon_footprint}")

                    # Visualize the route on a map using Folium
                    m = folium.Map(location=[start_coords['lat'], start_coords['lng']], zoom_start=13)

                    # Add start and end markers
                    folium.Marker(
                        [start_coords['lat'], start_coords['lng']],
                        popup=start_location,
                        icon=folium.Icon(color="green")
                    ).add_to(m)

                    folium.Marker(
                        [end_coords['lat'], end_coords['lng']],
                        popup=destination_location,
                        icon=folium.Icon(color="pink")
                    ).add_to(m)

                    # Plot the route on the map
                    for step in route['legs'][0]['steps']:
                        start_lat = step['start_location']['lat']
                        start_lng = step['start_location']['lng']
                        end_lat = step['end_location']['lat']
                        end_lng = step['end_location']['lng']
                        folium.PolyLine([(start_lat, start_lng), (end_lat, end_lng)], color="blue").add_to(m)

                    # Display the map in Streamlit
                    folium_static(m)

                    # Embed Google Map using Maps Embed API
                    embed_url = f"https://www.google.com/maps/embed/v1/directions?key={MAP_API_KEY}&origin={start_coords['lat']},{start_coords['lng']}&destination={end_coords['lat']},{end_coords['lng']}&mode={eco_friendly_mode}"
                    st.markdown(f'<iframe width="600" height="450" frameborder="0" style="border:0" src="{embed_url}" allowfullscreen></iframe>', unsafe_allow_html=True)

                else:
                    st.error("No routes found. Please check the locations and try again.")
            else:
                st.error("Invalid locations entered. Please check your input and try again.")
        else:
            st.error("Please enter both start and destination locations.")

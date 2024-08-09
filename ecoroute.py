import streamlit as st
import googlemaps
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import folium
from streamlit_folium import folium_static
from streamlit_folium import st_folium
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Load environment variables
load_dotenv()

# Initialize APIs
MAP_API_KEY = os.getenv('MAP_API_KEY')  
os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY")

st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #e0efe6;  /* Light green background to give an eco-friendly feel */
    }
    .stApp {
        background-color: #f8f8f8;  /* Soft white for app background */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);  /* Softer shadow for a subtle 3D effect */
    }
    h1 {
        color: #2f4f4f;  /* Dark Slate Gray for the title */
        text-align: center;
        font-weight: 700;  /* Bolder font for the title */
    }
    .stTextInput, .stButton {
        font-size: 16px;
        color: #2e8b57;  /* Sea Green color for input and button text */
    }
    .stButton > button {
        background-color: #2e8b57;  /* Sea Green button background */
        color: #fff;  /* White text on buttons */
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3cb371;  /* Medium Sea Green for button hover */
    }
    </style>
""", unsafe_allow_html=True)


st.title("🌍 EcoRoute: Sustainable Travel Planner")


gmaps = googlemaps.Client(key=MAP_API_KEY)
@st.cache_resource
def load_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API Key not found in .env file.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

model = load_model()

# User inputs
start_location = st.text_input("Enter your start location")
destination_location = st.text_input("Enter your destination location")

if st.button("Find Eco-Friendly Route"):
    if start_location and destination_location:
        # Geocoding the start and end locations
        geocode_start = gmaps.geocode(start_location)
        geocode_end = gmaps.geocode(destination_location)
        
        if geocode_start and geocode_end:
            start_coords = geocode_start[0]['geometry']['location']
            end_coords = geocode_end[0]['geometry']['location']
            st.write("Eco friendly route")
            prompt = f"You are a eco friendly mode of transport suggestor, your job is to provide me with the best routes in bulletins in comprehensive manner.Suggest the most eco-friendly mode of transport between {start_location} and {destination_location}."
            response = model.generate_content([prompt])
            eco_friendly_mode = response.text.strip()
            st.write(f"Suggested eco-friendly mode: {eco_friendly_mode.capitalize()}")
            
            # Get directions based on the suggested eco-friendly mode
            directions = gmaps.directions(
                (start_coords['lat'], start_coords['lng']),
                (end_coords['lat'], end_coords['lng']),
                mode=eco_friendly_mode if eco_friendly_mode in ["driving", "walking", "bicycling", "transit"] else "walking",  # Default to walking if the mode is not recognized
                departure_time=datetime.now()
            )
            
            if directions:
                # Extract route information
                route = directions[0]
                st.write("**Route Summary:**")
                st.write(route['summary'])
                
                # Calculate carbon footprint using Google Gemini (Placeholder logic)
                st.write("Carbon footprint")
                prompt2 = f"You are a carbon footprint calculator, you will Calculate the carbon footprint for a {route['legs'][0]['distance']['text']} {eco_friendly_mode} trip and provide me the best answer"
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
            else:
                st.error("No routes found. Please try again.")
        else:
            st.error("Invalid locations. Please check your input.")
    else:
        st.error("Please enter both start and destination locations.")

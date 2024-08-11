import streamlit as st
import google.generativeai as genai
from PIL import Image as PILImage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="TerraPulse", 
    page_icon="🌎", 
    layout="wide", 
    initial_sidebar_state="expanded", 
)

# Custom CSS for typography, headings, and styling
st.markdown(
    """
    <style>
    body {
        background-color: #f0f4f8;
        font-family: 'Roboto', sans-serif;
    }
    h1, h2, h3 {
        color: #005bb5;
        font-weight: 700;
    }
    h1 {
        font-size: 2.5em;
    }
    h2 {
        font-size: 2em;
    }
    h3 {
        font-size: 1.5em;
    }
    .stApp {
        padding: 15px;
        border-radius: 5px;
        background-color: #f0f4f8;
    }
    .stButton>button {
        background-color: #0073e6;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #005bb5;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 10px;
        font-size: 18px;
    }
    .stTextInput>div {
        display: flex;
        justify-content: center;
        margin-top: 80px;
    }
    .stSidebar > div {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 5px;
    }
    .sidebar-emoji {
        text-align: center;
    }
    .sidebar-emoji img {
        width: 2in;
        height: 2in;
    }
    .chat-message {
        font-size: 18px;
        font-weight: bold;
        color: #0073e6;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# GIF
st.sidebar.markdown(
    '<div class="sidebar-emoji"><img src="https://media.tenor.com/PBuEkZA9cVwAAAAj/sceptical-trashcan.gif" width="256" height="256" alt="MEDUSA GIF"></div>',
    unsafe_allow_html=True
)

# Sidebar instructions
st.sidebar.title("🛠️ How to Use TerraPulse")
st.sidebar.markdown(
    """
    **1. Upload an Image** 📸  
    Click the "Upload Image" button to select one or more images of trash items.

    **2. Analyze Image** 🔍  
    After uploading, click the "Analyze Image" button to begin analysis.

    **3. Get Classification** 🗑️  
    The app will classify the waste into categories and suggest the correct dustbin for disposal.
    
    **4. Review Results** ✅  
    The analysis results will appear next to the uploaded image.
    """
)

# Function to load the Gemini Pro Vision model
@st.cache_resource
def load_model():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API Key not found in .env file.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

# Function to analyze image
def analyze_image(image, prompt):
    model = load_model()
    response = model.generate_content([prompt, image])
    return response.text

# Function to handle Medical Imaging Diagnostics section
def Wastewise():
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
                        try:
                            analysis = analyze_image(image, prompt)
                            st.markdown(analysis)

                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                else:
                    st.info("Click 'Analyze Image' to start the analysis.")

Wastewise()

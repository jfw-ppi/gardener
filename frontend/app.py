import os
import streamlit as st
import requests
import datetime
import matplotlib.pyplot as plt
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


# Set up base URL and port for backend API
base_url = os.getenv("BACKEND_URL", "http://backend-service")
port = os.getenv("BACKEND_PORT", "8000")

# Full API URL
api_url = f"{base_url}:{port}"

# Initialize Llama 3b client
client = HuggingFaceEndpoint(
    endpoint_url="https://chat-default.llm.mylab.th-luebeck.dev/",
    timeout=30,
    streaming=True
)

# Define the refined prompt template with a fun, personalized touch
prompt_template = PromptTemplate.from_template("""
system
You are a friendly and quirky gardening gnome with a deep knowledge of botany. Your task is to analyze the growing conditions for a given plant at a specific location based on the provided weather data, plant requirements, and a calculated suitability score. Please provide your analysis in a fun and engaging way, adding a bit of personality to your responses.

user
Location: {location} (Latitude: {latitude}, Longitude: {longitude})
Date: {current_date}

Plant: {plant_name}
- Optimal Temperature Range: {topmn}-{topmx} °C
- Absolute Temperature Range: {tmin}-{tmax} °C
- Optimal Precipitation Range: {ropmn}-{ropmx} mm
- Absolute Precipitation Range: {rmin}-{rmax} mm

Weather Data for the Past 30 Days:
- Average Temperatures: {temperature_data}
- Precipitation: {precipitation_data}

Suitability Score: {suitability_score}
Suitability Score Legend: 
- 0-20: 🌧️ Very Poor - Conditions are not suitable for this plant.
- 21-40: 😟 Poor - The plant might struggle to grow.
- 41-60: 🤔 Moderate - Conditions are marginally acceptable.
- 61-80: 🙂 Good - Conditions are favorable for this plant.
- 81-100: 🌞 Excellent - Ideal growing conditions.

Warnings: {warnings}

### Response Instructions:
1. Greet the user in a fun way.
2. Provide an overview of the location and plant.
3. Analyze the temperature and precipitation data in a creative, storytelling manner.
4. Discuss the implications of the location’s latitude and longitude with some quirky comments.
5. Provide practical gardening advice in a friendly tone.
6. Conclude with a motivational message, encouraging the user to enjoy gardening.

Make sure to keep the response light-hearted and enjoyable!
""")

# Set a fun title with emojis
st.title("🌱 Gardening Helper 🧑‍🌾")

# Fetch all plant names from the backend API
plants_url = f"{api_url}/plants/"
plants_response = requests.get(plants_url)

if plants_response.status_code == 200:
    plants_data = plants_response.json()
    plant_names = [plant['ScientificName'] for plant in plants_data]
else:
    st.error("🚨 Failed to fetch plant names from the backend. Please try again later.")
    plant_names = []

# Location input with an example
location = st.text_input("🏡 Enter your location (city or address):", placeholder="e.g., Hamburg, Germany")

# Use a searchable dropdown for plant names with an added emoji
plant_name = st.selectbox("🌿 Select a plant (optional):", options=plant_names)

# Disable the button if the location is not provided
if st.button("🌟 Calculate Suitability 🌟", disabled=not location):
    if location and plant_name:
        # Fetch plant details using the selected scientific name
        plant_details_url = f"{api_url}/plants/scientific_name/{plant_name}"
        plant_details_response = requests.get(plant_details_url)

        if plant_details_response.status_code == 200:
            plant_details = plant_details_response.json()[0]  # We expect one plant per scientific name

            # Fetch geocode data
            geocode_response = requests.get(f"https://geocode.xyz/{location}?json=1")
            geocode_data = geocode_response.json()

            if 'latt' in geocode_data and 'longt' in geocode_data:
                latitude = geocode_data['latt']
                longitude = geocode_data['longt']

                # Fetch plant suitability data from backend API
                suitability_url = f"{api_url}/plants/suitability/single/{plant_name}?location={location}"
                suitability_response = requests.get(suitability_url)

                if suitability_response.status_code == 200:
                    suitability_data = suitability_response.json()

                    # Display the suitability score with an emoji
                    suitability_score = suitability_data['suitability_details']['suitability_score']
                    st.subheader(f"🌟 Suitability Score for {plant_name} at {location}: {suitability_score} 🌟")

                    # Visualization of weather data with custom styles
                    weather_data = suitability_data['weather_data']
                    st.subheader("📊 Weather Data (Past 30 Days):")

                    fig, ax = plt.subplots()
                    ax.plot(weather_data['temperature_2m_mean'], label='Temperature (°C)', color='orange', marker='o')
                    ax.bar(range(len(weather_data['precipitation_sum'])), weather_data['precipitation_sum'], alpha=0.5,
                           label='Precipitation (mm)', color='blue')
                    plt.legend()
                    st.pyplot(fig)

                    # Inform the user about the weather data interval
                    st.info("The weather data is collected and averaged over the past 30 days to provide an accurate analysis of current growing conditions.")

                    # Display a fun legend for the suitability score
                    st.subheader("📈 Suitability Score Legend")
                    st.write("""
                        - **0-20:** 🌧️ Very Poor - Conditions are not suitable for this plant.
                        - **21-40:** 😟 Poor - The plant might struggle to grow.
                        - **41-60:** 🤔 Moderate - Conditions are marginally acceptable.
                        - **61-80:** 🙂 Good - Conditions are favorable for this plant.
                        - **81-100:** 🌞 Excellent - Ideal growing conditions.
                    """)

                    # Prepare the prompt for Llama3 with a fun twist
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    prompt = prompt_template.format(
                        location=location,
                        latitude=latitude,
                        longitude=longitude,
                        plant_name=plant_name,
                        topmn=plant_details['TOPMN'],
                        topmx=plant_details['TOPMX'],
                        tmin=plant_details['TMIN'],
                        tmax=plant_details['TMAX'],
                        ropmn=plant_details['ROPMN'],
                        ropmx=plant_details['ROPMX'],
                        rmin=plant_details['RMIN'],
                        rmax=plant_details['RMAX'],
                        temperature_data=weather_data['temperature_2m_mean'],
                        precipitation_data=weather_data['precipitation_sum'],
                        suitability_score=suitability_score,
                        warnings="; ".join(suitability_data['suitability_details']['warnings']),
                        current_date=current_date
                    )

                    # Generate the response using Llama3
                    response = client.generate([prompt], temperature=0.25, max_new_tokens=512, repetition_penalty=1.2)
                    generated_text = response.generations[0][0].text.strip()

                    # Post-process the LLM output to clean up any artifacts
                    clean_text = generated_text.split("###")[0]  # Remove everything after '###'
                    clean_text = clean_text.replace("</s>", "").strip()  # Remove '</s>' if it appears

                    st.write("📜 Analysis Report:")
                    st.write(clean_text)
                else:
                    st.error("🚨 Failed to fetch suitability data. Please try again.")
            else:
                st.error("🚨 Could not fetch coordinates for the location. Please try again.")
        else:
            st.error("🚨 Failed to fetch plant details. Please try again.")

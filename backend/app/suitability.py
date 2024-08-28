import requests
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from .models import Plant

import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all types of logs


# Helper functions for calculating suitability scores

def calculate_daily_suitability(temperature, precipitation, plant):
    # Temperature suitability score
    if plant.TMIN <= temperature <= plant.TMAX:
        temp_score = 100
    elif temperature < plant.TMIN:
        temp_score = max(0, 100 - (plant.TMIN - temperature) * 10)  # Reduce score as it deviates
    else:
        temp_score = max(0, 100 - (temperature - plant.TMAX) * 10)

    # Precipitation suitability score
    if plant.RMIN <= precipitation <= plant.RMAX:
        precip_score = 100
    elif precipitation < plant.RMIN:
        precip_score = max(0, 100 - (plant.RMIN - precipitation) * 10)
    else:
        precip_score = max(0, 100 - (precipitation - plant.RMAX) * 10)

    # Average the scores
    return (temp_score + precip_score) / 2


def calculate_suitability_score(weather_data, plant):
    suitability_scores = []

    for temperature, precipitation in zip(weather_data['temperature_2m_mean'], weather_data['precipitation_sum']):
        daily_score = calculate_daily_suitability(temperature, precipitation, plant)
        suitability_scores.append(daily_score)

    # Average score over the 30-day period
    final_suitability_score = sum(suitability_scores) / len(suitability_scores)

    return final_suitability_score


async def get_plant_data_by_scientific_name(scientific_name, session: AsyncSession):
    query = select(Plant).where(Plant.ScientificName.ilike(scientific_name))
    result = await session.execute(query)
    plant = result.scalars().first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant


async def get_weather_and_suitability(location, scientific_name, session: AsyncSession):
    # If location is a tuple of latitude and longitude, use them directly
    if isinstance(location, tuple):
        latitude, longitude = location
    else:
        # Otherwise, geocode the location
        geocode_url = f"https://geocode.xyz/{location}?json=1"
        geocode_response = requests.get(geocode_url)
        geocode_data = geocode_response.json()
        latitude = float(geocode_data['latt'])
        longitude = float(geocode_data['longt'])

    # Step 2: Fetch plant data from the database
    plant = await get_plant_data_by_scientific_name(scientific_name, session)

    # Step 3: Fetch historical weather data
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=30)

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum"
    logger.debug(f"Weather API URL: {weather_url}")

    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        logger.error(f"Failed to retrieve weather data: {weather_response.text}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve weather data: {weather_response.text}")

    weather_data = weather_response.json()
    if 'daily' not in weather_data:
        logger.error("No daily weather data found in the API response.")
        raise HTTPException(status_code=500, detail="No daily weather data found in the API response.")

    daily_weather = weather_data.get("daily", {})
    temperature_2m_mean = [t for t in daily_weather.get('temperature_2m_mean', []) if t is not None]
    precipitation_sum = [p for p in daily_weather.get('precipitation_sum', []) if p is not None]

    if not temperature_2m_mean or not precipitation_sum:
        logger.error(f"Temperature or precipitation data missing or invalid: {daily_weather}")
        raise HTTPException(status_code=500, detail="Temperature or precipitation data missing or invalid.")

    try:
        final_suitability_score = calculate_suitability_score(
            {"temperature_2m_mean": temperature_2m_mean, "precipitation_sum": precipitation_sum},
            plant
        )
    except ValueError as e:
        logger.error(f"Failed to calculate suitability score: {e}")
        final_suitability_score = None

    if final_suitability_score is None:
        logger.warning("Suitability score could not be calculated due to insufficient data.")
        raise HTTPException(status_code=500,
                            detail="Suitability score could not be calculated due to insufficient data.")

    response_data = {
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "plant_name": plant.ScientificName,
        "suitability_details": {
            "suitability_score": final_suitability_score,
            "warnings": [],
            "interval_used": 30
        },
        "weather_data": {
            "temperature_2m_mean": temperature_2m_mean,
            "precipitation_sum": precipitation_sum
        }
    }

    return response_data

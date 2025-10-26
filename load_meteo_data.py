# load_meteo_data.py
import streamlit as st
import pandas as pd
import requests

METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

@st.cache_data
def fetch_meteo_data(latitude, longitude, start_date, end_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["rain", "temperature_2m", "wind_speed_10m", "snowfall"],
        "timezone": "auto",
    }
    r = requests.get(METEO_URL, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        st.error(f"Error fetching data from the weather API ({r.status_code}).")
        return None

@st.cache_data
def load_meteo_data(lat, lon, start_date, end_date):
    data = fetch_meteo_data(lat, lon, start_date, end_date)
    if not data or "hourly" not in data:
        return pd.DataFrame()

    hourly = data["hourly"]
    df_meteo = pd.DataFrame(hourly)
    df_meteo["time"] = pd.to_datetime(df_meteo["time"], errors="coerce", format="mixed")
    df_meteo["date"] = pd.to_datetime(df_meteo["time"], errors="coerce", format="mixed").dt.date
    df_meteo["hour"] = pd.to_datetime(df_meteo["time"], errors="coerce", format="mixed").dt.time

    # Optioneel: logje
    print(f"Loaded meteo for lat={lat}, lon={lon}, {start_date}→{end_date}")
    return df_meteo
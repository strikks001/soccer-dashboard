import streamlit as st
import pandas as pd
import requests
import unicodedata2

METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

def clean_city(city_name: str) -> str:
    # get the first part if there are multiple cities separated by /
    city = city_name.strip().split("/")[-1]

    # remove accents
    city = (
        unicodedata2.normalize("NFKD", city)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )

    # correct known discrepancies
    if city.lower() == "santiago de chile":
        city = "Santiago"
    elif city.lower() == "washington dc":
        city = "Washington"
    elif city.lower() == "udevalla":
        city = "Uddevalla"
    elif "sseldorf" in city.lower():
        city = "Dusseldorf"
    elif "norrk" in city.lower():
        city = "Norrkoping"

    return city

# Function to fetch latitude and longitude for a given city
@st.cache_data
def fetch_latlon(city_name):
    params = {"name": clean_city(city_name), "count": 1}
    r = requests.get(GEO_URL, params=params)

    if r.status_code == 200:
        data = r.json()
        if "results" in data and len(data["results"]) > 0:
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            return (lat, lon)
        else:
            st.error(f"City not found: {city_name}")
            return None
    else:
        st.error("Error fetching data from the geocoding API.")
        return None

# Function to fetch meteorological data
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
        data = r.json()
        return data
    else:
        st.error("Error fetching data from the weather API.")
        return None

# Convert meteo data into dataframe
data = fetch_meteo_data(52.52, 13.41, "2023-01-01", "2023-01-31")

# Pak de hourly data
df_meteo = pd.DataFrame(data["hourly"])
st.write(df_meteo.head())

# Retrieve unique cities from the DataFrame
cities = df["City"].unique()

# Fetch lat/lon for each unique city
city_map = {city: fetch_latlon(city) for city in cities if pd.notnull(city)}

# Map lat/lon back to the DataFrame
df["Latlon"] = df["City"].map(city_map)

# Split Datetime into Date and Time columns
df["Datetime"] = pd.to_datetime(df["Datetime"], dayfirst=True, errors="coerce")
df["Date"] =df["Datetime"].dt.date
df["Time"] =  df["Datetime"].dt.time

# Add meteo data for each match

st.title("🎈 Soccer Dashboard")
st.write(
    df.head(50),
   fetch_meteo_data(52.52, 13.41, "2023-01-01", "2023-01-31")
)

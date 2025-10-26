import streamlit as st
import pandas as pd
import requests
import unicodedata2

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url, encoding="utf-8")
    return df

# Function to clean city names
def clean_city(city_name: str) -> str:
    # get the first part if there are multiple cities separated by /
    city = city_name.strip().split("/")[-1]

    # remove accents
    city = (
        unicodedata2.normalize("NFKD", city)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )
    
    city = city.replace('rn">', '')

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
    elif city.lower() == "germany fr":
        city = "Germany"
    elif city.lower() == "ir iran":
        city = "Iran"

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

# Main function to load and process matches data
@st.cache_data
def load_matches_data():
    df = load_data("data/WorldCupMatches.csv")

     # Retrieve unique cities from the DataFrame
    cities = df["City"].unique()
    
    for col in ["Home Team Name", "Away Team Name"]:
        df[col] = df[col].str.replace('rn">', '', regex=False)
        df[col] = df[col].str.replace('IR Iran', 'Iran', regex=False)

    # Fetch lat/lon for each unique city
    city_map = {city: fetch_latlon(city) for city in cities if pd.notnull(city)}

    # Map lat/lon back to the DataFrame
    df["Latlon"] = df["City"].map(city_map)

    # Split Datetime into Date and Time columns
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce", format='mixed')
    df["Date"] = pd.to_datetime(df["Datetime"], errors="coerce").dt.date
    df["Start Time"] =  pd.to_datetime(df["Datetime"], errors="coerce", format="mixed").dt.time
    df["End Time"] =  (df["Datetime"] + pd.Timedelta(hours=2)).dt.time

    return df


@st.cache_data
def load_winner_data():
    df = load_data("data/WorldCups.csv")
    
    # clean city names with clean_city function
    df[["Winner", "Country", "Runners-Up", "Third", "Fourth"]] = df[["Winner", "Country", "Runners-Up", "Third", "Fourth"]].apply(lambda col: col.map(clean_city))
    return df
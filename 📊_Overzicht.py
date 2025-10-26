import streamlit as st
import plotly.express as px
import pandas as pd

from load_meteo_data import load_meteo_data
from load_matches_data import load_matches_data, load_winner_data

df_matches = load_matches_data()

st.title("📊 Overzicht")
st.write("Dit dashboard biedt een overzicht van de historische data van het WK voetbal, inclusief wedstrijden, teams en locaties. In de vergelijkingssectie kunt u dieper ingaan op specifieke analyses en vergelijkingen. Het onderzoek kijkt naar de weerdata in relatie tot de wedstrijden van het WK.")

st.dataframe(df_matches.sort_values(by="Year", ascending=False).head(15))

st.caption("De WK data komt uit de Kaggle dataset 'FIFA World Cup' (https://www.kaggle.com/datasets/abecklas/fifa-world-cup). De meteorologische data is opgehaald via de Open-Meteo API (https://open-meteo.com/en/docs).")

st.divider()

# Key metrics
total_matches = len(df_matches)
unique_cities = df_matches["City"].nunique()
unique_teams = pd.concat([
    df_matches['Home Team Name'],
    df_matches['Away Team Name']
]).nunique()
total_goals = df_matches['Home Team Goals'].sum() + df_matches['Away Team Goals'].sum()

# Display key metrics in columns
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Wedstrijden", f"{total_matches}")
with c2:
    st.metric("Unieke gaststeden", f"{unique_cities}")
with c3:
    st.metric("Unieke teams", f"{unique_teams}")
with c4:
    st.metric("Totaal aantal goals", f"{total_goals}")
    
st.divider()

# WK Winners section
st.subheader("🏆 Laatste WK winnaars")
df_winners = load_winner_data()

df_winners["WinsToDate"] = df_winners.groupby("Winner").cumcount() + 1

fig = px.scatter(
    df_winners,
    x="Year",
    y="Country",
    color="Winner",
    size="WinsToDate",
    size_max=30,
    opacity=0.5,
    hover_data=["Year", "Country", "WinsToDate"],
    title="WK Winnaars Over Tijd en Aantal Overwinningen",
    labels={"Country": "Gastland", "Year": "Jaar", "Winner": "Winnaar", "WinsToDate": "Aantal Overwinningen", "x" : "Jaar", "y": "Gastland"},
    color_discrete_sequence=px.colors.qualitative.G10
)
st.plotly_chart(fig, use_container_width=True)
# st.dataframe(df_winners.sort_values(by="Year", ascending=False).head(10))
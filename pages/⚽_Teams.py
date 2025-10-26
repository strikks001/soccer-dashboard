import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
from load_matches_data import load_matches_data

st.title("⚽ 1. Teams")

df_matches = load_matches_data()

st.subheader("1.1 Aantal teams per jaar")

# Display available teams per year
teams_per_year = (
    df_matches.groupby('Year')[['Home Team Name', 'Away Team Name']]
    .agg(lambda x: list(set(x.explode())))  # 👉 lijst van unieke teams
    .apply(lambda row: list(set(row['Home Team Name'] + row['Away Team Name'])), axis=1)
    .reset_index(name='Teams')
)

# Calculate number of teams per year
teams_per_year['Team Count'] = teams_per_year['Teams'].apply(len)

# Plot number of teams per year
fig = px.bar(
    x=teams_per_year['Year'],
    y=teams_per_year['Team Count'],
    labels={'x': 'Jaar', 'y': 'Aantal Teams'},
    title='Aantal teams per jaar',
    text=teams_per_year['Team Count']
)

st.plotly_chart(fig)

st.subheader("1.2 Cumulatieve deelnames van teams")

# show per selection cumulative participations of teams over the years
team_part_per_year = pd.concat([
    df_matches[['Year', 'Home Team Name']].rename(columns={'Home Team Name': 'Team'}),
    df_matches[['Year', 'Away Team Name']].rename(columns={'Away Team Name': 'Team'})
])
team_part_per_year = team_part_per_year.drop_duplicates().sort_values(['Team', 'Year']).dropna()
team_part_per_year['Cum'] = team_part_per_year.groupby('Team').cumcount() + 1

teams = sorted(team_part_per_year['Team'].unique())
selected = st.multiselect("Kies één of meer teams:", teams, default=["Brazil", "Germany", "Italy"])
df_sel = team_part_per_year[team_part_per_year['Team'].isin(selected)]

fig = px.line(
    df_sel, 
    x='Year', 
    y='Cum', 
    color='Team', 
    markers=True,
    title='Cumulatieve deelnames per gekozen teams',
    labels={'Cum': 'Cumulatieve deelnames', 'Year': 'Jaar'}
)
st.plotly_chart(fig, use_container_width=True)
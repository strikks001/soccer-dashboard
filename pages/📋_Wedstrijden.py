import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
from load_matches_data import load_matches_data

st.title("📋 2. Wedstrijden")

df_matches = load_matches_data()

st.subheader("2.1 Wedstrijden per jaar")

# Display total matches per year
matches_per_year = df_matches['Year'].value_counts().sort_index()
fig_year = px.bar(
    x=matches_per_year.index,
    y=matches_per_year.values,
    labels={'x': 'Jaar', 'y': 'Aantal Wedstrijden'},
    title='Aantal wedstrijden per jaar',
    text=matches_per_year.values,
    color_discrete_sequence=['#EF553B']
)
st.plotly_chart(fig_year)

# Display matches per city
st.subheader("2.2 Wedstrijden per stad")
matches_per_city = df_matches['City'].value_counts().sort_values(ascending=False)
top_n = st.slider("Aantal steden tonen (Top-N)", 5, len(matches_per_city.index), 5)

# Tel het aantal wedstrijden per stad
matches_per_city = matches_per_city.head(top_n)

# Plot (horizontale bar = beter leesbaar bij lange namen)
fig_city = px.bar(
    x=matches_per_city.values,
    y=matches_per_city.index,
    orientation="h",
    labels={"x": "Aantal wedstrijden", "y": "Stad"},
    title=f"Top {top_n} steden met de meeste wedstrijden",
    text=matches_per_city.values,
    color_discrete_sequence=['#636EFA']
)
fig_city.update_layout(
    yaxis=dict(autorange="reversed"),
    height=500 + top_n * 10
)

st.plotly_chart(fig_city, use_container_width=True)
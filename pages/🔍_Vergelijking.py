# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from load_matches_data import load_matches_data
from load_meteo_data import load_meteo_data

# Filter on the 2014 World Cup
df_all = load_matches_data()

# Add interactive selectbox of years
years = sorted(df_all["Year"].unique().tolist())
years = [y for y in years if y >= 1940]  # filter alle jaren vóór 1940 eruit
default_year = 2014 if 2014 in years else years[0]

year = st.sidebar.select_slider("Kies jaar", options=years, value=default_year)

st.title("🔍 Vergelijking van het jaar " + str(year))

df = df_all[df_all["Year"] == year].copy()

st.divider()

# Bepaal eerste en laatste speelmoment (incl. middernacht-cases)
start_dt = pd.to_datetime(df["Date"].astype(str) + " " + df["Start Time"].astype(str))
end_dt   = pd.to_datetime(df["Date"].astype(str) + " " + df["End Time"].astype(str))
end_dt[end_dt <= start_dt] += pd.Timedelta(days=1)

period_start = start_dt.min().date()
period_end   = end_dt.max().date()
n_matches    = len(df)

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Startdatum", str(period_start))
with col_b:
    st.metric("Einddatum", str(period_end))
with col_c:
    st.metric("Aantal wedstrijden", n_matches)
    
    
st.divider()

# Turn into a tuple list of (lat, lon)
df[["lat", "lon"]] = pd.DataFrame(df["Latlon"].tolist(), index=df.index)

# Show winner of the match in df
df["Winner"] = np.where(
    df["Home Team Goals"] > df["Away Team Goals"],
    df["Home Team Name"],
    np.where(
        df["Home Team Goals"] < df["Away Team Goals"],
        df["Away Team Name"],
        "Draw"
    )
)

# Add amount of goals
df["Total Goals"] = df["Home Team Goals"] + df["Away Team Goals"]

# Add goal difference
df["GoalDiff"] = df["Home Team Goals"] - df["Away Team Goals"]

# Function to get meteo stats for each match
with st.spinner("⏳ Weerdata wordt opgehaald..."):
    def _stats(r):
        start = pd.to_datetime(f"{r['Date']} {r['Start Time']}")
        end   = pd.to_datetime(f"{r['Date']} {r['End Time']}")
        
        if end <= start:
            end += pd.Timedelta(days=1)

        m = load_meteo_data(r.lat, r.lon, start.date().isoformat(), end.date().isoformat())
        s = m[(m["time"] >= start) & (m["time"] < end)]
        return [s["temperature_2m"].mean(), s["rain"].sum(), s["wind_speed_10m"].mean()] if not s.empty else [np.nan]*3

    # Apply the function to get meteo stats
    df[["temp_mean_c","rain_total_mm","wind_mean_ms"]] = df.apply(_stats, axis=1, result_type="expand")

df_plot = df.copy()
df_plot["WinnerType"] = np.select(
    [df_plot["Winner"] == df_plot["Home Team Name"],
     df_plot["Winner"] == df_plot["Away Team Name"],
     df_plot["Winner"] == "Draw"],
    ["Home", "Away", "Draw"],
    default="Draw"
)

# --- Toggle: gelijkspelen meenemen of niet ---
show_draws = st.checkbox("Gelijkspelen meenemen", value=True)

df_view = df_plot.copy()
if not show_draws:
    df_view = df_view[df_view["WinnerType"] != "Draw"]

# dynamische volgorde voor assen/legendes
order = [x for x in ["Home", "Away", "Draw"] if x in df_view["WinnerType"].unique()]

# Als er niets overblijft, netjes stoppen
if df_view.empty:
    st.info("Geen wedstrijden over met de huidige filter (Draw uitgeschakeld).")
    st.stop()

order = ["Home", "Away", "Draw"]

# check for correlation
st.subheader("4.1 Correlatie matrix")
corr_cols = ["Home Team Goals", "Away Team Goals", "Total Goals", "GoalDiff", "temp_mean_c", "rain_total_mm", "wind_mean_ms"]
corr = df_view[corr_cols].corr()
fig_corr = px.imshow(
    corr,
    text_auto=True,
    title="Correlatie matrix van wedstrijd- en weerdata",
    labels={ "color": "Correlatiecoëfficiënt"},
    x=corr_cols,
    y=corr_cols,
    color_continuous_scale='RdBu',
    zmin=-1,
    zmax=1
)
st.plotly_chart(fig_corr)

corr = df_view.corr(numeric_only=True)
r_temp_goals = corr.loc["temp_mean_c", "Total Goals"].round(2)
r_rain_goals = corr.loc["rain_total_mm", "Total Goals"].round(2)
r_wind_goals = corr.loc["wind_mean_ms", "Total Goals"].round(2)

st.markdown(f"""
**Inzichten voor {year}:**
- Correlatie temperatuur ↔ totaal aantal goals: **{r_temp_goals}**
- Correlatie regen ↔ totaal aantal goals: **{r_rain_goals}**
- Correlatie wind ↔ totaal aantal goals: **{r_wind_goals}**
""")

# Kleine samenvatting per uitslag
st.subheader("4.2 Samenvatting per uitslag (gemiddelde)")
st.dataframe(
    df_view.groupby("WinnerType", as_index=False)[["temp_mean_c","rain_total_mm","wind_mean_ms"]].mean().round(2)
)

fig = make_subplots(
    rows=1, cols=3,
    subplot_titles=("Temperatuur (°C)", "Regen (mm)", "Wind (m/s)"),
    shared_yaxes=False
)

# Temperatuur-boxplot
fig.add_trace(
    go.Box(
        y=df_view["temp_mean_c"],
        x=df_view["WinnerType"],
        name="Temperatuur",
        boxpoints="outliers"
    ),
    row=1, col=1
)

# Regen-boxplot
fig.add_trace(
    go.Box(
        y=df_view["rain_total_mm"],
        x=df_view["WinnerType"],
        name="Regen",
        boxpoints="outliers"
    ),
    row=1, col=2
)

# Wind-boxplot
fig.add_trace(
    go.Box(
        y=df_view["wind_mean_ms"],
        x=df_view["WinnerType"],
        name="Wind",
        boxpoints="outliers"
    ),
    row=1, col=3
)

# Layout aanpassen
fig.update_layout(
    title="Weer vs Uitslag",
    showlegend=False,
    height=500,
    width=1200,
)

# In Streamlit tonen
st.plotly_chart(fig, use_container_width=True)

# Influence of weather on total goals
st.subheader("4.3 Invloed van weer op totaal aantal goals")

factor = st.selectbox(
    "Kies welke weerfactor de kleur van de bubbels bepaalt:",
    options=["wind_mean_ms", "rain_total_mm", "temp_mean_c"],
    format_func=lambda x: {
        "wind_mean_ms": "Gem. Windsnelheid (m/s)",
        "rain_total_mm": "Totale Regenval (mm)",
        "temp_mean_c": "Gem. Temperatuur (°C)"
    }[x],
)

fig_bubble = px.scatter(
    df_view,
    x="temp_mean_c",
    y="Total Goals",
    size="rain_total_mm",
    color=factor,
    hover_data=["City", "Home Team Name", "Away Team Name", "Date"],
    labels={
        "temp_mean_c": "Gem. Temperatuur (°C)",
        "Total Goals": "Totaal aantal Goals",
        factor: factor.replace("_", " ").title(),
        "rain_total_mm": "Totale Regenval (mm)"
    },
    color_continuous_scale="Viridis",
    title=f"Invloed van temperatuur, regen en wind op doelpunten ({year})"
)

st.plotly_chart(fig_bubble, use_container_width=True)



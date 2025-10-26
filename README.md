# ⚽ Soccer Dashboard – Wereldkampioenschappen Analyse

Een interactieve **Streamlit webapp** om historische **WK-wedstrijden** en **weersomstandigheden** te analyseren.  
De applicatie combineert matchdata met meteorologische gegevens om te onderzoeken of factoren zoals temperatuur, regen en wind invloed hebben op het aantal gemaakte doelpunten.

---

## 📊 Functionaliteiten

### 📋 Overzicht (hoofdpagina)

- Toon alle gespeelde WK-wedstrijden sinds 1940.
- Bekijk datum, stadion, locatie, teams en eindstanden.
- Gebruik een **filter per jaar** via de sidebar.

### ⚽ Wedstrijden

- Detailanalyse per jaar of per stad.
- Bekijk statistieken van specifieke wedstrijden.
- Weergave van:
  - Totale doelpunten
  - Doelpuntverschil
  - Winnende ploeg (Home / Away / Draw)

### 🔍 Vergelijking

- Correlatie-analyse tussen weer en wedstrijdresultaten.
- Grafieken met temperatuur, regen en wind ten opzichte van uitslagen.
- Bubble-plot om te zien of weersomstandigheden invloed hebben op het **totaal aantal doelpunten**.
- Mogelijkheid om ‘Draw’-wedstrijden aan/uit te zetten.

---

## 🧠 Technische details

**Framework:** [Streamlit](https://streamlit.io/)  
**Data-analyse:** `pandas`, `numpy`  
**Visualisatie:** `plotly.express`, `plotly.graph_objects`, `matplotlib`  
**Data-bronnen:**

- `load_matches_data.py` – laadt WK-wedstrijddataset (CSV / Kaggle).
- `load_meteo_data.py` – haalt weerdata op voor een specifieke locatie en datum.

---

## 📁 Projectstructuur

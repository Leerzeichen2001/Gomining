import streamlit as st
import requests
import pandas as pd

API_URL = "https://api.gomining.com/api/nft-game/round/get-state"

def fetch_round_state():
    headers = {
        "Authorization": f"Bearer {st.secrets['ACCESS_TOKEN']}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://app.gomining.com",
        "Referer": "https://app.gomining.com/",
        "x-device-type": "desktop",
        "Accept": "application/json"
    }
    
    # Versuch mit POST ohne Body
    response = requests.get(API_URL, headers=headers)
    
    # Falls das nicht funktioniert, kannst du später auf GET wechseln:
    # response = requests.get(API_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API Fehler: {response.status_code}")
        return None

st.title("⛏️ BTC Mining Wars Wahrscheinlichkeiten & Statistik")

data = fetch_round_state()

if data and "data" in data:
    clans = data["data"]["array"]
    me = data["data"]["me"]

    # DataFrame erstellen
    df = pd.DataFrame([{
        "Clan": c["clanName"],
        "Score": c["score"],
        "Chance %": c["chance"] * 100,
        "Boost": c["activeBoostScore"]
    } for c in clans])

    # Dein Clan anzeigen
    st.subheader("Dein Clan")
    st.write(f"**Name:** {me['clanName']}")
    st.write(f"**Score:** {me['score']:.2f}")
    st.write(f"**Gewinnchance:** {me['chance']*100:.4f} %")

    # Score Bar-Chart
    st.subheader("Score pro Clan")
    df_sorted = df.sort_values(by="Score", ascending=False)
    st.bar_chart(df_sorted.set_index("Clan")["Score"])

    # Boost Bar-Chart
    st.subheader("Boost pro Clan")
    st.bar_chart(df_sorted.set_index("Clan")["Boost"])

    # Gewinnchance Bar-Chart
    st.subheader("Gewinnchance pro Clan (%)")
    st.bar_chart(df_sorted.set_index("Clan")["Chance %"])

    # Rechner: benötigter Score für Wunsch-Chance
    st.subheader("Optimaler Score-Rechner")
    desired_chance = st.slider("Gewünschte Gewinnchance (%)", min_value=0.1, max_value=50.0, value=5.0)
    total_score = df["Score"].sum() + me["score"]
    needed_score = (desired_chance / 100) * total_score
    st.write(f"Du bräuchtest ca. **{needed_score:.2f} Punkte**, um {desired_chance:.1f}% Gewinnchance zu haben (bei aktuellem Gesamtscore {total_score:.2f}).")

else:
    st.warning("Keine Daten empfangen oder API-Problem.")

import streamlit as st
import requests
import pandas as pd
import base64
import json
import time

API_URL = "https://api.gomining.com/api/nft-game/round/get-state"

# Funktion zum JWT-Token Ablauf prüfen
def decode_jwt_exp(token):
    try:
        payload_encoded = token.split('.')[1]
        padding = '=' * (-len(payload_encoded) % 4)
        decoded = base64.urlsafe_b64decode(payload_encoded + padding)
        payload = json.loads(decoded)
        return payload.get("exp", 0)
    except Exception:
        return 0

def check_token(token):
    exp = decode_jwt_exp(token)
    now = int(time.time())
    remaining = exp - now
    if remaining <= 0:
        st.error("⚠ Dein Access Token ist abgelaufen. Bitte hole einen neuen Token aus der Web-App und aktualisiere dein Secret.")
    else:
        min_left = remaining // 60
        sec_left = remaining % 60
        st.info(f"✅ Dein Access Token ist noch {min_left} min {sec_left} sek gültig.")

# Funktion zum Abrufen des API-States
def fetch_round_state():
    headers = {
        "Authorization": f"Bearer {st.secrets['ACCESS_TOKEN']}",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://app.gomining.com",
        "Referer": "https://app.gomining.com/",
        "x-device-type": "desktop",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    body = {
        "type": "clans",
        "pagination": {
            "limit": 10,
            "skip": 0,
            "count": 0
        },
        "leagueId": 5
    }

    response = requests.post(API_URL, headers=headers, json=body)

    if response.status_code == 200:
        st.success("Daten erfolgreich abgerufen!")
        return response.json()
    else:
        st.error(f"API Fehler: {response.status_code}")
        st.json(response.text)
        return None

# Streamlit App Aufbau
st.title("⛏️ BTC Mining Wars Wahrscheinlichkeiten & Statistik")

# Check Access Token Gültigkeit
check_token(st.secrets["ACCESS_TOKEN"])

# API Call
data = fetch_round_state()

if data and "data" in data:
    clans = data["data"]["array"]
    me = data["data"]["me"]

    df = pd.DataFrame([{
        "Clan": c["clanName"],
        "Score": c["score"],
        "Chance %": c["chance"] * 100,
        "Boost": c["activeBoostScore"]
    } for c in clans])

    st.subheader("Dein Clan")
    st.write(f"**Name:** {me['clanName']}")
    st.write(f"**Score:** {me['score']:.2f}")
    st.write(f"**Gewinnchance:** {me['chance']*100:.4f} %")

    st.subheader("Score pro Clan")
    df_sorted = df.sort_values(by="Score", ascending=False)
    st.bar_chart(df_sorted.set_index("Clan")["Score"])

    st.subheader("Boost pro Clan")
    st.bar_chart(df_sorted.set_index("Clan")["Boost"])

    st.subheader("Gewinnchance pro Clan (%)")
    st.bar_chart(df_sorted.set_index("Clan")["Chance %"])

    st.subheader("Optimaler Score-Rechner")
    desired_chance = st.slider("Gewünschte Gewinnchance (%)", min_value=0.1, max_value=50.0, value=5.0)
    total_score = df["Score"].sum() + me["score"]
    needed_score = (desired_chance / 100) * total_score
    st.write(f"Du bräuchtest ca. **{needed_score:.2f} Punkte**, um {desired_chance:.1f}% Gewinnchance zu haben (bei aktuellem Gesamtscore {total_score:.2f}).")
else:
    st.warning("Keine gültigen Daten empfangen. Bitte prüfe Access Token oder API.")

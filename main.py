import streamlit as st
import requests
import pandas as pd
import base64
import json
import time
import math

# API URL
API_URL = "https://api.gomining.com/api/nft-game/round/get-state"

# JWT-Token Ablaufprüfung
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
        st.error("⚠ Dein Access Token ist abgelaufen. Bitte hole einen neuen Token und aktualisiere dein Secret.")
    else:
        min_left = remaining // 60
        sec_left = remaining % 60
        st.info(f"✅ Access Token gültig: {min_left} min {sec_left} sek")

# API-Daten abrufen
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
        "pagination": {"limit": 10, "skip": 0, "count": 0},
        "leagueId": 5
    }
    response = requests.post(API_URL, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API Fehler: {response.status_code}")
        st.json(response.text)
        return None

# Echo Boost Zyklen berechnen
def calc_echo_cycles(diff):
    # Summe = 100k * N * (N+1)/2 >= diff
    # Lösen der quadratischen Gleichung: N^2 + N - (2*diff/100000) >= 0
    a = 1
    b = 1
    c = -2 * diff / 100000
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return None
    n = (-b + math.sqrt(discriminant)) / (2 * a)
    return math.ceil(n)

# Booster Definition
BOOSTERS = [
    {"name": "🔄 Echo Boost X1", "type": "echo", "interval": 120},  # alle 2 min
    {"name": "🚀 Blitz", "value": 400000, "type": "instant"},      # sofort 400k
    {"name": "⚡ Rakete", "value": 1800, "type": "rakete"}         # 1800 Punkte pro Sekunde
]

# Streamlit App Start
st.title("⛏️ BTC Mining Wars Booster-Rechner")

check_token(st.secrets["ACCESS_TOKEN"])
data = fetch_round_state()

if data and "data" in data:
    clans = data["data"]["array"]
    me = data["data"]["me"]
    df = pd.DataFrame([{"Clan": c["clanName"], "Score": c["score"]} for c in clans])
    df_sorted = df.sort_values(by="Score", ascending=False)
    top_scores = df_sorted["Score"].values[:3]
    ranks = ["🥇 Platz 1", "🥈 Platz 2", "🥉 Platz 3"]

    for idx, target in enumerate(top_scores):
        diff = max(0, target - me["score"])
        if diff == 0:
            st.success(f"Du bist bereits vor {ranks[idx]}!")
            continue

        st.markdown(f"### {ranks[idx]} Ziel-Score: {target:.2f}")
        st.markdown(f"Benötigte Punkte: **{diff:.2f}**")

        cols = st.columns(3)

        # Echo Boost
        with cols[0]:
            st.markdown("**🔄 Echo Boost X1**")
            n_cycles = calc_echo_cycles(diff)
            if n_cycles:
                total_time = n_cycles * 120
                min_needed = total_time // 60
                sec_needed = total_time % 60
                st.write(f"Zyklen: {n_cycles}")
                st.write(f"Dauer: {min_needed} min {sec_needed} sek")
            else:
                st.write("Nicht erreichbar")

        # Blitz
        with cols[1]:
            st.markdown("**🚀 Blitz**")
            blitz_count = math.ceil(diff / 400000)
            st.write(f"Benötigt: {blitz_count}x")

        # Rakete
        with cols[2]:
            st.markdown("**⚡ Rakete**")
            sec_needed = math.ceil(diff / 1800)
            min_needed = sec_needed // 60
            sec_remaining = sec_needed % 60
            st.write(f"Laufzeit: {min_needed} min {sec_remaining} sek")
else:
    st.warning("Keine gültigen Daten empfangen. Bitte prüfe Access Token oder API.")

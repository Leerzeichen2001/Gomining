import streamlit as st
import requests
import pandas as pd
import base64
import json
import time
import math

API_URL = "https://api.gomining.com/api/nft-game/round/get-state"

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

BOOSTERS = [
    {"name": "Boost X1", "value": 1800, "type": "instant"},
    {"name": "Boost X10", "value": 18000, "type": "instant"},
    {"name": "Boost X100", "value": 180000, "type": "instant"},
    {"name": "Instant Boost", "value": 400000, "type": "instant"},
    {"name": "Echo Boost X1", "value": 100000, "type": "echo", "interval": 120},
    {"name": "Echo Boost X10", "value": 1000000, "type": "echo", "interval": 120},
    {"name": "Echo Boost X100", "value": 10000000, "type": "echo", "interval": 120}
]

# App Start
st.title("⛏️ BTC Mining Wars Wahrscheinlichkeiten & Booster-Rechner")

check_token(st.secrets["ACCESS_TOKEN"])

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

    df_sorted = df.sort_values(by="Score", ascending=False)

    st.subheader("📈 Booster-Vorschau (Top 3 Ziele)")

    top_scores = df_sorted["Score"].values[:3]
    ranks = ["🥇", "🥈", "🥉"]

    for idx, target in enumerate(top_scores):
        diff = max(0, target - me["score"])
        st.markdown(f"### {ranks[idx]} Ziel-Score: {target:.2f} Punkte")

        booster_cols = st.columns(3)
        for i, booster in enumerate(BOOSTERS):
            col = booster_cols[i % 3]
            with col:
                st.markdown(
                    f"""
                    <div style='border:1px solid #ddd; padding:10px; border-radius:10px; background-color:#f9f9f9'>
                    <b>{booster['name']}</b><br>
                    """,
                    unsafe_allow_html=True
                )
                if booster["type"] == "instant":
                    count = math.ceil(diff / booster["value"])
                    st.markdown(
                        f"<span style='color:green'>Benötigt: {count}x</span></div>",
                        unsafe_allow_html=True
                    )
                elif booster["type"] == "echo":
                    count = math.ceil(diff / booster["value"])
                    time_needed = count * booster["interval"]
                    min_needed = time_needed // 60
                    sec_needed = time_needed % 60
                    st.markdown(
                        f"<span style='color:blue'>Benötigt: {count}x<br>Dauer: {min_needed} min {sec_needed} sek</span></div>",
                        unsafe_allow_html=True
                    )

else:
    st.warning("Keine gültigen Daten empfangen. Bitte prüfe Access Token oder API.")

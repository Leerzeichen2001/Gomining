import streamlit as st
import requests
import pandas as pd
import base64
import json
import time
import math
import matplotlib.pyplot as plt

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
        st.error("⚠ Dein Access Token ist abgelaufen. Bitte hole einen neuen Token und aktualisiere dein Secret.")
    else:
        min_left = remaining // 60
        sec_left = remaining % 60
        st.info(f"✅ Access Token gültig: {min_left} min {sec_left} sek")

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

def calc_echo_cycles(diff):
    a = 1
    b = 1
    c = -2 * diff / 100000
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return None
    n = (-b + math.sqrt(discriminant)) / (2 * a)
    return math.ceil(n)

# --- Start Auto-Refresh ---
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

auto_refresh = st.checkbox("🔄 Automatisch alle 1 Sekunde aktualisieren", value=True)

if auto_refresh:
    if time.time() - st.session_state["last_refresh"] >= 1:
        st.session_state["last_refresh"] = time.time()
        st.experimental_rerun()

# --- Haupt-App ---
st.title("⛏️ BTC Mining Wars Booster-Rechner (mit Graphen)")

check_token(st.secrets["ACCESS_TOKEN"])
data = fetch_round_state()

if data and "data" in data:
    clans = data["data"]["array"]
    me = data["data"]["me"]
    df = pd.DataFrame([{"Clan": c["clanName"], "Score": c["score"]} for c in clans])
    df_sorted = df.sort_values(by="Score", ascending=False)
    top_scores = df_sorted.head(3)

    # Dein Score vs. Top 3 Diagramm
    plt.figure(figsize=(8, 5))
    plt.bar(
        [f"{row['Clan']} (Top {i+1})" for i, row in top_scores.iterrows()] + ["Du"],
        list(top_scores["Score"]) + [me["score"]],
        color=["green", "orange", "blue", "red"]
    )
    plt.ylabel("Punkte")
    plt.title("Dein Score vs. Top 3")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(plt.gcf())
    plt.clf()

    # Booster Bedarf Diagramme mit logarithmischer Skala
    for i, row in top_scores.iterrows():
        target = row["Score"]
        diff = max(0, target - me["score"])
        st.markdown(f"### {row['Clan']} Ziel: {target:.2f} Punkte (Diff: {diff:.2f})")

        if diff == 0:
            st.success("✅ Du bist bereits auf oder vor diesem Platz!")
            continue

        # Booster-Berechnung
        echo_cycles = calc_echo_cycles(diff)
        blitz_count = math.ceil(diff / 400000)
        rakete_sec = math.ceil(diff / 1800)

        booster_names = ["🔄 Echo Zyklen", "🚀 Blitz Booster", "⚡ Rakete Sekunden"]
        booster_values = [echo_cycles or 0, blitz_count, rakete_sec]

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(booster_names, booster_values, color=["blue", "green", "purple"])
        ax2.set_ylabel("Benötigte Menge (log-Skala)")
        ax2.set_yscale('log')
        ax2.set_title(f"Booster-Bedarf für {row['Clan']}")

        # Zahlen auf Balken
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2, height, f'{int(height)}', ha='center', va='bottom')

        st.pyplot(fig2)
        plt.clf()

else:
    st.warning("Keine gültigen Daten empfangen. Bitte prüfe Access Token oder API.")

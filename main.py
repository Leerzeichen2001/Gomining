import streamlit as st
import requests
import pandas as pd
import base64
import json
import time
import math
import plotly.graph_objects as go

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
st.title("⛏️ BTC Mining Wars Booster-Rechner (Plotly interaktiv)")

check_token(st.secrets["ACCESS_TOKEN"])
data = fetch_round_state()

if data and "data" in data:
    clans = data["data"]["array"]
    me = data["data"]["me"]
    df = pd.DataFrame([{"Clan": c["clanName"], "Score": c["score"]} for c in clans])
    df_sorted = df.sort_values(by="Score", ascending=False)
    top_scores = df_sorted.head(3)

    # Dein Score vs. Top 3 interaktiv
    fig = go.Figure()
    for idx, row in top_scores.iterrows():
        fig.add_trace(go.Bar(name=f"{row['Clan']} (Top {idx+1})", x=["Score"], y=[row["Score"]]))
    fig.add_trace(go.Bar(name="Du", x=["Score"], y=[me["score"]], marker_color="red"))
    fig.update_layout(
        title="Dein Score vs. Top 3",
        yaxis_title="Punkte",
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Booster Bedarf Diagramme interaktiv
    for idx, row in top_scores.iterrows():
        target = row["Score"]
        diff = max(0, target - me["score"])
        st.markdown(f"### {row['Clan']} Ziel: {target:.2f} Punkte (Diff: {diff:.2f})")

        if diff == 0:
            st.success("✅ Du bist bereits auf oder vor diesem Platz!")
            continue

        echo_cycles = calc_echo_cycles(diff)
        blitz_count = math.ceil(diff / 400000)
        rakete_sec = math.ceil(diff / 1800)

        booster_names = ["🔄 Echo Zyklen", "🚀 Blitz Booster", "⚡ Rakete Sekunden"]
        booster_values = [echo_cycles or 0, blitz_count, rakete_sec]

        fig_boost = go.Figure()
        fig_boost.add_trace(go.Bar(
            x=booster_names,
            y=booster_values,
            text=booster_values,
            textposition='auto',
            marker_color=["blue", "green", "purple"]
        ))
        fig_boost.update_layout(
            title=f"Booster-Bedarf für {row['Clan']}",
            yaxis_title="Benötigte Menge",
            yaxis_type="log"
        )
        st.plotly_chart(fig_boost, use_container_width=True)

else:
    st.warning("Keine gültigen Daten empfangen. Bitte prüfe Access Token oder API.")

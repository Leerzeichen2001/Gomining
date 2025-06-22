import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

API_URL = "https://api.gomining.com/api/nft-game/round/get-last"

def fetch_current_round():
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json().get("data")
    except Exception as err:
        st.warning(f"Live-Daten konnten nicht geladen werden: {err}")
        return None

def generate_mock_data():
    now = datetime.utcnow()
    return {
        "id": 999999,
        "blockNumber": 123456,
        "active": True,
        "startedAt": now.isoformat(),
        "endedAt": (now + timedelta(minutes=5)).isoformat(),
        "userRounds": [
            {"power": 1000, "basePoints": 1200, "clanId": 1, "userId": 1},
            {"power": 850, "basePoints": 900, "clanId": 2, "userId": 2},
            {"power": 600, "basePoints": 650, "clanId": 3, "userId": 3}
        ]
    }

def display_dashboard(round_data):
    if not round_data:
        st.warning("Keine Runden-Daten verfügbar.")
        return

    st.title("GoMining Runden Dashboard")

    st.subheader("Allgemeine Informationen")
    st.write(f"Runden-ID: {round_data.get('id')}")
    st.write(f"Block Number: {round_data.get('blockNumber')}")
    st.write(f"Aktiv: {round_data.get('active')}")
    st.write(f"Gestartet: {round_data.get('startedAt')}")
    st.write(f"Beendet: {round_data.get('endedAt')}")

    user_rounds = round_data.get("userRounds", [])
    if user_rounds:
        df = pd.DataFrame(user_rounds)
        st.subheader("User Runden Übersicht")
        st.dataframe(df)
    else:
        st.info("Keine User-Runden-Daten vorhanden.")

def main():
    st.set_page_config(page_title="GoMining Dashboard", layout="wide")
    st.sidebar.title("GoMining Dashboard")

    if st.sidebar.button("Daten aktualisieren") or st.button("Daten aktualisieren"):
        round_data = fetch_current_round()
        if not round_data:
            st.info("Mock-Daten werden angezeigt (User-Simulator).")
            round_data = generate_mock_data()
        display_dashboard(round_data)
    else:
        st.info("Klicke auf den Button 'Daten aktualisieren', um die neuesten Runden-Daten zu laden.")

if __name__ == "__main__":
    main()

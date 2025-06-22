import requests
import streamlit as st
import pandas as pd
from datetime import datetime

API_URL = "https://api.gomining.com/api/nft-game/round/get-last"

def fetch_current_rounds():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("array", [])
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Runden-Daten: {e}")
        return []

def calculate_round_durations(rounds_data, last_n=20):
    records = []
    for round_info in rounds_data[-last_n:]:
        started_at = round_info.get("startedAt")
        ended_at = round_info.get("endedAt")
        if started_at and ended_at:
            try:
                start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
                duration_sec = (end_dt - start_dt).total_seconds()
                records.append({
                    "Round ID": round_info.get("id"),
                    "Start": start_dt,
                    "End": end_dt,
                    "Duration (sec)": duration_sec
                })
            except Exception as e:
                st.warning(f"Fehler bei Runde {round_info.get('id')}: {e}")
                continue
    return pd.DataFrame(records)

def main():
    st.title("⛏️ GoMining Rundenlängen Dashboard")
    st.write("Live Analyse der letzten Runden")

    with st.spinner("Hole aktuelle Runden..."):
        rounds = fetch_current_rounds()

    if not rounds:
        st.error("Keine Daten empfangen. Bitte versuche es später erneut.")
        return

    df = calculate_round_durations(rounds)

    if df.empty:
        st.warning("Nicht genügend abgeschlossene Runden gefunden.")
        return

    st.subheader("Letzte 20 Rundenlängen")
    st.dataframe(df.style.format({"Duration (sec)": "{:.2f}"}))

    avg_duration = df["Duration (sec)"].mean()
    st.metric("⏱️ Durchschnittliche Rundenlänge (Sekunden)", f"{avg_duration:.2f}")

    st.subheader("Rundenlänge Verlauf")
    st.line_chart(df.set_index("Round ID")["Duration (sec)"])

if __name__ == "__main__":
    main()

import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# API-Endpunkte
LATEST_BLOCK_URL = "https://blockchain.info/latestblock"
RAWBLOCK_URL = "https://blockchain.info/rawblock/{}"

# Helper: Zeitformat
def format_time(seconds):
    return str(timedelta(seconds=seconds))

# Helper: Lade Block-Info
def fetch_block_info(block_hash):
    r = requests.get(RAWBLOCK_URL.format(block_hash))
    r.raise_for_status()
    b = r.json()
    return {
        "height": b["height"],
        "hash": b["hash"],
        "time": b["time"],
        "prev_block": b["prev_block"]
    }

# Lade aktuelle Blöcke parallel
def fetch_recent_blocks(n=20, max_workers=5):
    # Starte mit aktuellem Block
    latest = requests.get(LATEST_BLOCK_URL).json()
    block_hashes = [latest["hash"]]

    # Hole alle Hashes sequenziell (nur die Hashes, keine Details)
    for _ in range(n - 1):
        info = fetch_block_info(block_hashes[-1])
        block_hashes.append(info["prev_block"])

    # Jetzt lade alle Block-Details parallel
    blocks = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        progress = st.progress(0)
        for i, block in enumerate(executor.map(fetch_block_info, block_hashes)):
            blocks.append(block)
            progress.progress((i + 1) / n)
    return blocks

# Dashboard
def main():
    st.title("📊 BTC Block-Duration Analyzer")
    st.write("Dieses Tool lädt aktuelle BTC-Blöcke und schätzt die Blocklänge.")
    
    n_blocks = st.slider("Anzahl Blöcke", min_value=5, max_value=100, value=20, step=5)
    max_workers = st.slider("Parallel-Threads", min_value=1, max_value=10, value=5)

    if st.button("🔄 Blöcke laden"):
        try:
            blocks = fetch_recent_blocks(n=n_blocks, max_workers=max_workers)
            
            # Daten vorbereiten
            df = pd.DataFrame(blocks)
            df["datetime"] = pd.to_datetime(df["time"], unit="s")
            df = df.sort_values("height")
            df["duration"] = df["datetime"].diff().dt.total_seconds().fillna(0)

            # Anzeige
            st.subheader("Block-Zeiten und Längen")
            df_show = df[["height", "hash", "datetime", "duration"]].copy()
            df_show["duration"] = df_show["duration"].apply(format_time)
            st.dataframe(df_show)

            # Heatmap
            st.subheader("⏱ Heatmap der Blocklängen")
            df_heat = df.pivot_table(values="duration", index="height", aggfunc="mean")
            st.heatmap(df_heat.T, cmap="coolwarm")

            # Prognose
            avg_duration = df["duration"][1:].mean()  # skip 0
            st.success(f"⏳ Durchschnittliche Blocklänge: {format_time(int(avg_duration))}")
            st.info(f"🔮 Prognose nächste Blocklänge: {format_time(int(avg_duration))}")

        except Exception as e:
            st.error(f"Fehler beim Laden: {e}")

if __name__ == "__main__":
    main()

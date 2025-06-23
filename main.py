import streamlit as st
import requests
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np

# =======================
# API Funktionen
# =======================
def get_latest_block():
    url = 'https://blockchain.info/latestblock'
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_block_by_hash(block_hash):
    url = f'https://blockchain.info/rawblock/{block_hash}'
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def fetch_recent_blocks(n=10):
    blocks = []
    latest = get_latest_block()
    blocks.append({
        'hash': latest['hash'],
        'time': latest['time'],
        'height': latest['height']
    })
    
    current_hash = latest['hash']
    for _ in range(n - 1):
        block = get_block_by_hash(current_hash)
        blocks.append({
            'hash': block['hash'],
            'time': block['time'],
            'height': block['height']
        })
        current_hash = block['prev_block']
    return blocks

# =======================
# Hilfsfunktionen
# =======================
def seconds_to_hms(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

def calculate_estimate(blocks):
    blocks_sorted = sorted(blocks, key=lambda x: x['height'], reverse=True)
    times = [b['time'] for b in blocks_sorted]
    heights = [b['height'] for b in blocks_sorted]
    
    intervals = [t1 - t2 for t1, t2 in zip(times[:-1], times[1:])]
    avg_interval = sum(intervals) / len(intervals)
    
    seconds_since_last = int(time.time()) - times[0]
    estimate_remaining = max(avg_interval - seconds_since_last, 0)
    
    return intervals, avg_interval, estimate_remaining, seconds_since_last, heights

# =======================
# Streamlit App
# =======================
def main():
    st.title("⛏ Bitcoin Blockzeit Vorhersage")
    st.write("Schätzung der Blockzeit und Heatmap der Intervalle.")

    block_count = st.slider("Anzahl der letzten Blöcke für Analyse:", min_value=5, max_value=100, value=20, step=5)
    
    if st.button("🔄 Daten aktualisieren"):
        try:
            with st.spinner(f"Lade die letzten {block_count} Blöcke..."):
                blocks = fetch_recent_blocks(n=block_count)
                intervals, avg_interval, estimate_remaining, seconds_since_last, heights = calculate_estimate(blocks)
            
            st.success(f"{block_count} Blöcke erfolgreich geladen und analysiert!")
            
            # Ergebnisse
            st.write(f"📊 **Durchschnittliches Block-Intervall (über {len(intervals)} Intervalle):** {seconds_to_hms(avg_interval)}")
            st.write(f"🕒 **Seit letztem Block:** {seconds_to_hms(seconds_since_last)}")
            st.write(f"⏳ **Geschätzte Restzeit bis nächster Block:** {seconds_to_hms(estimate_remaining)}")
            st.write(f"🔍 **Vermutete Gesamtdauer dieses Blocks:** {seconds_to_hms(avg_interval)}")

            # Bar Chart
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(heights[1:], intervals, color="skyblue")
            ax.set_xlabel("Blockhöhe")
            ax.set_ylabel("Intervall (Sekunden)")
            ax.set_title(f"Block-Intervalle (letzte {block_count} Blöcke)")
            ax.invert_xaxis()
            st.pyplot(fig)

            # Heatmap
            st.subheader("🟧 Heatmap der Blockzeiten (je röter, desto länger)")
            interval_array = np.array(intervals).reshape(1, -1)
            fig2, ax2 = plt.subplots(figsize=(10, 1.5))
            im = ax2.imshow(interval_array, cmap="YlOrRd", aspect="auto")
            ax2.set_yticks([])
            ax2.set_xticks(range(len(heights)-1))
            ax2.set_xticklabels(heights[1:], rotation=90, fontsize=6)
            fig2.colorbar(im, orientation="horizontal", pad=0.2, label="Intervall (Sekunden)")
            st.pyplot(fig2)

            # Letzte Blöcke
            st.subheader("Letzte Blöcke (Zeit UTC, Hash gekürzt)")
            for b in blocks[:5]:  # Zeige die letzten 5
                block_time = datetime.datetime.utcfromtimestamp(b['time']).strftime('%Y-%m-%d %H:%M:%S')
                st.write(f"Block {b['height']} | Zeit: {block_time} | Hash: {b['hash'][:16]}...")

        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Daten: {e}")

if __name__ == "__main__":
    main()

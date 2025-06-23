import streamlit as st
import requests
import time
import datetime
import matplotlib.pyplot as plt

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
# Schätzung berechnen
# =======================
def calculate_estimate(blocks):
    blocks_sorted = sorted(blocks, key=lambda x: x['height'], reverse=True)
    times = [b['time'] for b in blocks_sorted]
    heights = [b['height'] for b in blocks_sorted]
    
    intervals = [t1 - t2 for t1, t2 in zip(times[:-1], times[1:])]
    avg_interval = sum(intervals) / len(intervals)
    
    seconds_since_last = int(time.time()) - times[0]
    estimate_in = avg_interval - seconds_since_last
    
    return intervals, avg_interval, estimate_in, heights

# =======================
# Streamlit App
# =======================
def main():
    st.title("⛏ Bitcoin Blockzeit Vorhersage")
    st.write("Diese App schätzt die Zeit bis zum nächsten BTC-Block basierend auf den letzten Blöcken.")
    
    if st.button("🔄 Daten aktualisieren"):
        try:
            with st.spinner("Hole aktuelle Block-Daten..."):
                blocks = fetch_recent_blocks(n=10)
                intervals, avg_interval, estimate_in, heights = calculate_estimate(blocks)
            
            st.success("Daten erfolgreich geladen!")
            
            # Ergebnisse anzeigen
            st.write(f"📊 Durchschnittliches Block-Intervall (letzte 10 Blöcke): **{avg_interval:.1f} Sekunden**")
            st.write(f"🕒 Seit letztem Block: **{int(time.time()) - blocks[0]['time']} Sekunden**")
            
            if estimate_in > 0:
                st.write(f"⏳ Geschätzte Zeit bis nächster Block: **{estimate_in:.1f} Sekunden (~{estimate_in/60:.1f} Minuten)**")
            else:
                st.write("⚡ Block wird jederzeit erwartet oder schon gefunden!")
            
            # Chart
            fig, ax = plt.subplots()
            ax.bar(heights[1:], intervals)
            ax.set_xlabel("Blockhöhe")
            ax.set_ylabel("Intervall (Sekunden)")
            ax.set_title("Block-Intervalle (letzte 10 Blöcke)")
            ax.invert_xaxis()
            st.pyplot(fig)
            
            # Letzte Blöcke anzeigen
            st.subheader("Letzte Blöcke")
            for b in blocks:
                block_time = datetime.datetime.utcfromtimestamp(b['time']).strftime('%Y-%m-%d %H:%M:%S')
                st.write(f"Block {b['height']} | Zeit: {block_time} UTC | Hash: {b['hash'][:16]}...")
        
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Daten: {e}")

if __name__ == "__main__":
    main()

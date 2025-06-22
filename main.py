import requests
from datetime import datetime

API_URL = "https://api.gomining.com/api/nft-game/round/get-last"

def fetch_current_rounds():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {}).get("array", [])
    except Exception as e:
        print(f"Fehler beim Abrufen der Runden-Daten: {e}")
        return []

def calculate_round_durations(rounds_data, last_n=20):
    durations = []
    for round_info in rounds_data[-last_n:]:
        started_at = round_info.get("startedAt")
        ended_at = round_info.get("endedAt")
        if started_at and ended_at:
            try:
                start_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
                duration_sec = (end_dt - start_dt).total_seconds()
                durations.append(duration_sec)
            except Exception as e:
                print(f"Fehler beim Verarbeiten einer Runde: {e}")
                continue
    if durations:
        avg_duration = sum(durations) / len(durations)
    else:
        avg_duration = 0
    return durations, avg_duration

def main():
    rounds = fetch_current_rounds()
    if not rounds:
        print("Keine Runden-Daten erhalten.")
        return
    durations, avg_duration = calculate_round_durations(rounds)
    
    print("Letzte 20 Rundenlängen (Sekunden):")
    for idx, dur in enumerate(durations, 1):
        print(f"{idx}: {dur:.2f} Sek.")
    print(f"\nDurchschnittliche Rundenlänge: {avg_duration:.2f} Sekunden")

if __name__ == "__main__":
    main()

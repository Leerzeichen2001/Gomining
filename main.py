import json
from datetime import datetime
import matplotlib.pyplot as plt

def parse_timestamp(timestamp_str):
    """Hilfsfunktion zur Umwandlung des Timestamps in ein datetime-Objekt"""
    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except Exception as e:
        print(f"Fehler beim Parsen des Timestamps {timestamp_str}: {e}")
        return None

def calculate_round_durations(rounds_data, last_n=20):
    """Berechne die Rundenlängen der letzten N abgeschlossenen Runden"""
    durations = []
    count = 0
    for round_item in reversed(rounds_data):  # Neueste zuerst
        started_at = round_item.get("startedAt")
        ended_at = round_item.get("endedAt")
        if started_at and ended_at:
            start_time = parse_timestamp(started_at)
            end_time = parse_timestamp(ended_at)
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()
                durations.append(duration)
                count += 1
                if count >= last_n:
                    break
    avg_duration = sum(durations) / len(durations) if durations else 0
    return durations, avg_duration

def main():
    # Lade deine JSON-Daten (ersetze 'runden.json' durch deinen Pfad)
    with open('runden.json', 'r') as f:
        data = json.load(f)

    rounds_data = data["data"]["array"]
    
    # Berechne Rundenlängen
    durations, avg_duration = calculate_round_durations(rounds_data, last_n=20)

    # Ausgabe
    print("Rundenlängen der letzten 20 abgeschlossenen Runden (in Sekunden):")
    for i, dur in enumerate(durations, 1):
        print(f"Runde {i}: {dur:.2f} Sekunden")

    print(f"\nDurchschnittliche Rundenlänge: {avg_duration:.2f} Sekunden")

    # Vorhersage
    print(f"Vorhergesagte nächste Rundenlänge: {avg_duration:.2f} Sekunden")

    # Visualisierung (optional)
    plt.plot(list(range(1, len(durations)+1)), durations, marker='o')
    plt.title("Rundenlängen der letzten 20 Runden")
    plt.xlabel("Runde (1 = älteste, 20 = neueste)")
    plt.ylabel("Dauer (Sekunden)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()

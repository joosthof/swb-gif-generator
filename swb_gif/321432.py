import os
import json
from swb_config_script import save_folder

def count_stations(save_path):
    """Count the number of unique stations in a save file."""
    with open(save_path, "r", encoding="utf-8") as f:
        save = json.load(f)

    stations = save.get("data", {}).get("stations", [])
    return len(stations)

def main():
    save_files = [os.path.join(save_folder, f) for f in os.listdir(save_folder) if f.lower().endswith(".json")]
    save_files.sort(key=os.path.getctime)

    if not save_files:
        print("No JSON save files found in", save_folder)
        return

    total_stations = set()

    for save_file in save_files:
        num_stations = count_stations(save_file)
        print(f"{os.path.basename(save_file)}: {num_stations} stations")

if __name__ == "__main__":
    main()

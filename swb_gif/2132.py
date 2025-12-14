import os
import json
import re

save_folder = r"C:/Users/oosth/OneDrive/Documenten/SubwayBuilder/saves/COL"

# Define your lines per color (extensions included)
COLOR_TO_NAME = {
    "#00add0": { "names": ["DT", "MP", "R"], "shape": "square" },
    "#ff6319": { "names": ["F"], "shape": "square" },
    "#662483": { "names": ["CA"], "shape": "square" },
    "#ffa300": { "names": ["H"], "shape": "square" },
    "#6cbe45": { "names": ["W"], "shape": "square" },
}

# Function to normalize color strings
def normalize_color(c):
    if not c:
        return None
    c = c.strip().lower()
    if c.startswith("rgb"):
        nums = list(map(int, re.findall(r"\d+", c)))
        if len(nums) == 3:
            c = "#{:02x}{:02x}{:02x}".format(*nums)
    return c

# Load save files
save_files = [os.path.join(save_folder, f) for f in os.listdir(save_folder) if f.lower().endswith(".json")]
save_files.sort(key=os.path.getctime)

revealed_lines = set()
next_name_index = {color.lower(): 0 for color in COLOR_TO_NAME}

print("Checking when lines are revealed in saves:\n")

for save_path in save_files:
    save_name = os.path.basename(save_path)
    with open(save_path, "r", encoding="utf-8") as f:
        save = json.load(f)

    new_lines = []

    for track in save.get("data", {}).get("tracks", []):
        color_raw = track.get("color")
        color = normalize_color(color_raw)
        if not color:
            continue
        if color not in COLOR_TO_NAME:
            continue

        idx = next_name_index[color]
        names = COLOR_TO_NAME[color]["names"]
        if idx >= len(names):
            continue

        line_name = names[idx]
        key = (color, line_name)
        if key not in revealed_lines:
            revealed_lines.add(key)
            new_lines.append(f"{line_name} ({color} {idx+1})")
            next_name_index[color] += 1

    if new_lines:
        print(f"{save_name}: {', '.join(new_lines)}")

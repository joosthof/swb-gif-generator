import os
import json
import re
from collections import OrderedDict
from swb_config_script import save_folder

global_line_order = OrderedDict()

def extract_svg_and_colors(path):
    """
    Extracts the SVG content and line colors from a SubwayBuilder JSON save file.

    Returns:
        svg (str) - the SVG thumbnail
        line_colors (OrderedDict) - mapping of line_id -> color
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON in {path}: {e}")
        return None, {}

    svg = data.get("routeThumbnail", "")
    if not svg:
        return None, {}

    colors = re.findall(r'stroke="(#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}))"', svg)
    line_colors = OrderedDict()

    for i, color in enumerate(colors):
        line_id = str(i + 1)
        line_colors[line_id] = color
        if color.lower() not in global_line_order:
            global_line_order[color.lower()] = None

    return svg, line_colors


# --------------------------- GET LAST SAVE ---------------------------
save_files = [os.path.join(save_folder, f) for f in os.listdir(save_folder) if f.endswith(".json")]

if not save_files:
    print("No save files found in the folder!")
    exit()

last_save = max(save_files, key=os.path.getctime)

svg, line_colors = extract_svg_and_colors(last_save)

if not line_colors:
    print("ERROR: No line colors found in the last save.")
else:
    print(f"Line colors in '{os.path.basename(last_save)}':")
    for line_id, color in line_colors.items():
        print(f"  Line {line_id}: {color}")
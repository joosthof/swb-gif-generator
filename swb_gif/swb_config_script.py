import json
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
else:
    base_path = Path(__file__).parent

config_path = base_path / "config.json"

with open(config_path, "r") as f:
    config = json.load(f)

save_folder = config.get("save_folder")
output_folder = config.get("output_folder")
output_name = config.get("output_name", "output")
fps = config.get("fps", 1)
TARGET_RES = config.get("target_res", 2000)
THREADS = config.get("threads", 4)
add_legend_flag = config.get("add_legend", True)
BACKGROUND_COLOR = config.get("background_color", "#1e1e1e")
export_gif = config.get("export_gif", True)
LINE_WIDTH = config.get("line_width", 2.5)
export_last_png = config.get("export_last_png", False)
show_stations = config.get("show_stations", True)
raw_color_to_name = config.get("color_to_name", {})
COLOR_TO_NAME = {}
for color, value in raw_color_to_name.items():
    if isinstance(value, list):
        COLOR_TO_NAME[color.lower()] = {"names": value, "shape": "square"}
    elif isinstance(value, dict):
        COLOR_TO_NAME[color.lower()] = {
            "names": value.get("names", [color]),
            "shape": value.get("shape", "square")
        }

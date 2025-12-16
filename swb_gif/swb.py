import os
import json
import re
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from geopy.distance import geodesic
from collections import OrderedDict
from swb_config_script import (save_folder, output_name, fps, TARGET_RES, THREADS, add_legend_flag, BACKGROUND_COLOR, export_gif, COLOR_TO_NAME,
                               LINE_WIDTH, export_last_png, show_stations, output_folder, show_network_length, show_station_count, unit)
from extract_colors import extract_svg_and_colors

# --------------------------- HELPERS ---------------------------

def add_background(svg_text, color=BACKGROUND_COLOR):
    """Inject a solid background rect into the SVG."""
    return svg_text.replace(">", f"><rect width='100%' height='100%' fill='{color}'/>", 1)

def thin_lines(svg_text, new_width=LINE_WIDTH):
    return re.sub(r'stroke-width="[\d\.]+"', f'stroke-width="{new_width}"', svg_text)

def calculate_network_length(save_path, unit="km"):
    with open(save_path, "r", encoding="utf-8") as f:
        save = json.load(f)

    track_divisor = {}

    for group in save.get("data", {}).get("trackGroups", []):
        lanes_type = group.get("trackLanesType", "single")
        divisor = {
            "single": 1,
            "parallel": 2,
            "quad": 4
        }.get(lanes_type, 1)

        for tid in group.get("trackIds", []):
            track_divisor[tid] = divisor

    seen_segments = set()
    total_km = 0.0

    for track in save.get("data", {}).get("tracks", []):
        coords = track.get("coords", [])
        divisor = track_divisor.get(track.get("id"), 1)

        for i in range(len(coords) - 1):
            p1, p2 = tuple(coords[i]), tuple(coords[i + 1])
            segment = tuple(sorted([p1, p2]))

            if segment in seen_segments:
                continue

            dist_km = geodesic(p1[::-1], p2[::-1]).km
            total_km += dist_km / divisor
            seen_segments.add(segment)

    if unit == "km":
        return total_km
    else:
        return total_km * 0.621371

def svg_to_png(svg_text, size):
    svg_io = BytesIO(svg_text.encode("utf-8"))
    drawing = svg2rlg(svg_io)
    scale_x = size / drawing.width
    scale_y = size / drawing.height
    drawing.width *= scale_x
    drawing.height *= scale_y
    drawing.scale(scale_x, scale_y)
    png_bytes = BytesIO()
    renderPM.drawToFile(drawing, png_bytes, fmt="PNG")
    png_bytes.seek(0)
    return Image.open(png_bytes).convert("RGBA")

def render_task(path):
    svg, line_colors = extract_svg_and_colors(path)
    if not svg:
        return None, {}
    svg = add_background(svg, BACKGROUND_COLOR)
    svg = thin_lines(svg, LINE_WIDTH)
    try:
        png = svg_to_png(svg, TARGET_RES)
        return png, line_colors
    except Exception as e:
        print(f"SVG error in {os.path.basename(path)}: {e}")
        return None, {}

# --------------------------- LEGEND ---------------------------

def draw_legend_shape(draw, shape, xy, color, radius=6):
    x0, y0, x1, y1 = xy
    if shape == "square":
        draw.rectangle(xy, fill=color)
    elif shape == "rounded_square":
        draw.rounded_rectangle(xy, fill=color, radius=radius)
    elif shape == "circle":
        draw.ellipse(xy, fill=color)
    elif shape == "diamond":
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        points = [(cx, y0), (x1, cy), (cx, y1), (x0, cy)]
        draw.polygon(points, fill=color)
    else:
        draw.rectangle(xy, fill=color)

def add_legend(png, legend_items, network_length_km=None, station_count=None):
    """Draws a legend on the PNG using a dict of (color,name) -> {"color":..., "name":..., "shape":...}.
       Optionally adds a single box with network length and station count below the line legend."""
    if not legend_items and network_length_km is None and station_count is None:
        return png

    png = png.convert("RGBA")
    draw = ImageDraw.Draw(png)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    padding = 15
    line_height = 36
    color_box_size = 30

    legend_list = list(legend_items.values())

    if legend_list:
        longest_name = max((item["name"] for item in legend_list), key=lambda s: draw.textlength(s, font=font))
        name_width = draw.textlength(longest_name, font=font)
        box_width = 60 + name_width + 40
        box_height = line_height * len(legend_list) + padding * 2
        radius = 20

        x0 = png.width - box_width - 20
        y0 = 20
        x1 = x0 + box_width
        y1 = y0 + box_height

        draw.rounded_rectangle([x0, y0, x1, y1], fill=(20, 20, 20, 200), radius=radius)

        for i, item in enumerate(legend_list):
            y = y0 + padding + i * line_height
            draw_legend_shape(draw, item.get("shape", "square"),
                              [x0 + 10, y, x0 + 10 + color_box_size, y + color_box_size],
                              item["color"])
            draw.text((x0 + 20 + color_box_size, y), item["name"], fill="white", font=font)
    else:
        x0 = png.width - 300 - 20
        y1 = 20

    lines = []
    if network_length_km is not None:
        lines.append(f"{network_length_km:.1f}{unit}")
    if station_count is not None:
        lines.append(f"{station_count} sts.")

    if lines:
        max_text_width = max(draw.textlength(line, font=font) for line in lines)
        box_height = len(lines) * line_height + 2 * padding
        box_x0 = x0
        box_y0 = y1 + 15
        box_x1 = box_x0 + box_width
        box_y1 = box_y0 + box_height

        draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], fill=(20, 20, 20, 200), radius=15)

        for i, line in enumerate(lines):
            draw.text((box_x0 + padding, box_y0 + padding + i * line_height), line, fill="white", font=font)

    return png.convert("RGB")


# --------------------------- LOAD SAVE FILES ---------------------------

save_files = [os.path.join(save_folder, f) for f in os.listdir(save_folder) if f.lower().endswith(".json")]
save_files.sort(key=os.path.getctime)

if not save_files:
    print("No .json save files found. Exiting.")
    exit()

for save_file in save_files:
    length_km = calculate_network_length(save_file, unit=unit)
    print(f"{os.path.basename(save_file)} network length: {length_km:.1f} {unit}")

# --------------------------- RENDER ---------------------------

print("Rendering thumbnails...")
thumbnails = []
line_info = []

with ThreadPoolExecutor(max_workers=THREADS) as executor:
    for png, lines in tqdm(executor.map(render_task, save_files),
                           total=len(save_files), desc="Thumbnails"):
        if png:
            thumbnails.append(png)
            line_info.append(lines)

# --------------------------- ADD LEGEND CUMULATIVELY ---------------------------

if add_legend_flag:
    cumulative_legend = OrderedDict()
    color_counters = {}

    for i in range(len(thumbnails)):
        current_lines = line_info[i]

        current_color_counts = {}
        for color in current_lines.values():
            color_lower = color.lower()
            current_color_counts[color_lower] = current_color_counts.get(color_lower, 0) + 1

        for color_lower, count_in_frame in current_color_counts.items():
            config_item = COLOR_TO_NAME.get(color_lower, {"names": [f"Line"], "shape": "square"})
            names = config_item["names"]
            shape = config_item.get("shape", "square")
            already_used = color_counters.get(color_lower, 0)

            for idx in range(already_used, min(count_in_frame, len(names))):
                name_to_use = names[idx]
                key = (color_lower, name_to_use)
                if key not in cumulative_legend:
                    cumulative_legend[key] = {"color": color_lower, "name": name_to_use, "shape": shape}

            color_counters[color_lower] = max(already_used, min(count_in_frame, len(names)))

        nl = calculate_network_length(save_files[i], unit=unit) if show_network_length else None

        station_count = None
        if show_station_count:
            with open(save_files[i], "r", encoding="utf-8") as f:
                save_data = json.load(f)
            station_count = len(save_data.get("data", {}).get("stations", []))

        thumbnails[i] = add_legend(thumbnails[i], cumulative_legend, network_length_km=nl, station_count=station_count)

# --------------------------- EXPORT GIF ---------------------------

if export_gif:
    print("Creating GIF...")
    gif_frames = [im.convert("P", palette=Image.ADAPTIVE) for im in thumbnails]
    gif_path = os.path.join(output_folder, output_name + ".gif")
    os.makedirs(output_folder, exist_ok=True)
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True
    )
    print(f"GIF saved as {gif_path}")

# --------------------------- EXPORT LAST PNG ---------------------------

if export_last_png and thumbnails:
    if not thumbnails:
        print("No valid SVG thumbnails found, GIF not created.")
        exit()
    last_png = thumbnails[-1]
    last_path = os.path.join(output_folder, output_name + "_LAST.png")
    os.makedirs(output_folder, exist_ok=True)
    last_png.save(last_path)
    print(f"Last save exported as {last_path}")

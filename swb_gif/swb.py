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
                               LINE_WIDTH, export_last_png, show_stations, output_folder, show_network_length, show_station_count)
from extract_colors import extract_svg_and_colors

# --------------------------- HELPERS ---------------------------

def add_background(svg_text, color=BACKGROUND_COLOR):
    """Inject a solid background rect into the SVG."""
    return svg_text.replace(">", f"><rect width='100%' height='100%' fill='{color}'/>", 1)

def thin_lines(svg_text, new_width=LINE_WIDTH):
    return re.sub(r'stroke-width="[\d\.]+"', f'stroke-width="{new_width}"', svg_text)

def calculate_network_length(save_path):
    """Calculate total network length (in km) from a save file, avoiding double-counted segments."""
    with open(save_path, "r", encoding="utf-8") as f:
        save = json.load(f)

    seen_segments = set()
    total_km = 0

    for track in save.get("data", {}).get("tracks", []):
        coords = track.get("coords", [])
        for i in range(len(coords)-1):
            p1, p2 = tuple(coords[i]), tuple(coords[i+1])
            segment = tuple(sorted([p1, p2]))
            if segment not in seen_segments:
                total_km += geodesic(p1[::-1], p2[::-1]).km / 2
                seen_segments.add(segment)

    return total_km

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

def add_legend(png, legend_items, network_length_km=None):
    """Draws a legend on the PNG using a dict of (color,name) -> {"color":..., "name":..., "shape":...}.
       Optionally adds a network length box below the line legend."""
    if not legend_items and network_length_km is None:
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
        y0 = 20
        box_width = 300
        y1 = y0

    if network_length_km is not None:
        text = f"{network_length_km:.1f} km"
        text_width = draw.textlength(text, font=font)
        text_height = line_height
        nl_box_width = text_width + 2 * padding
        nl_box_height = text_height + 2 * padding
        nl_x0 = x0
        nl_y0 = y1 + 15
        nl_x1 = nl_x0 + nl_box_width
        nl_y1 = nl_y0 + nl_box_height
        draw.rounded_rectangle([nl_x0, nl_y0, nl_x1, nl_y1], fill=(20, 20, 20, 200), radius=15)
        draw.text((nl_x0 + padding, nl_y0 + padding), text, fill="white", font=font)

    return png.convert("RGB")

# --------------------------- LOAD SAVE FILES ---------------------------

save_files = [os.path.join(save_folder, f) for f in os.listdir(save_folder) if f.lower().endswith(".json")]
save_files.sort(key=os.path.getctime)

if not save_files:
    print("No .json save files found. Exiting.")
    exit()

for save_file in save_files:
    length_km = calculate_network_length(save_file)
    print(f"{os.path.basename(save_file)} network length: {length_km:.1f} km")

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
    next_name_index = {}
    seen_lines = set()

    for i in range(len(thumbnails)):
        current_lines = line_info[i]

        for line_id, color in current_lines.items():
            if line_id in seen_lines:
                continue

            config_item = COLOR_TO_NAME.get(color.lower(), {"names":[f"Line {line_id}"], "shape":"square"})
            names = config_item["names"]
            shape = config_item.get("shape", "square")

            if line_id not in next_name_index:
                next_name_index[line_id] = 0

            idx = next_name_index[line_id]
            if idx < len(names):
                name_to_add = names[idx]
                key = (line_id, name_to_add)
                if key not in cumulative_legend:
                    cumulative_legend[key] = {"color": color.lower(), "name": name_to_add, "shape": shape}
                    next_name_index[line_id] += 1
                    seen_lines.add(line_id)

        nl = calculate_network_length(save_files[i]) if show_network_length else None
        thumbnails[i] = add_legend(thumbnails[i], cumulative_legend, network_length_km=nl)

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

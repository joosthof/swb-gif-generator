import os
import json
import re
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image, ImageDraw, ImageFont
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from collections import OrderedDict
from swb_config_script import save_folder, output_name, fps, TARGET_RES, THREADS, add_legend_flag, BACKGROUND_COLOR, export_gif, COLOR_TO_NAME, LINE_WIDTH, export_last_png
from extract_colors import extract_svg_and_colors, global_line_order

# --------------------------- HELPERS ---------------------------
def add_background(svg_text, color=BACKGROUND_COLOR):
    """Inject a solid background rect into the SVG."""
    return svg_text.replace(">", f"><rect width='100%' height='100%' fill='{color}'/>", 1)

def thin_lines(svg_text, new_width=LINE_WIDTH):
    return re.sub(r'stroke-width="[\d\.]+"', f'stroke-width="{new_width}"', svg_text)

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

def add_legend(png, line_colors, color_to_name=COLOR_TO_NAME):
    if not line_colors:
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

    legend_items = []
    for line_id, color in line_colors.items():
        color = color.lower()
        names = color_to_name.get(color, [f"Line {line_id}"])
        if not isinstance(names, list):
            names = [names]
        for name in names:
            legend_items.append((color, name))

    seen = set()
    unique_items = []
    for item in legend_items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    longest_name = max(
        (name for (_, name) in unique_items),
        key=lambda s: draw.textlength(s, font=font)
    )
    name_width = draw.textlength(longest_name, font=font)

    box_width = 60 + name_width + 20
    box_height = line_height * len(unique_items) + padding * 2
    radius = 20

    x0 = png.width - box_width - 20
    y0 = 20
    x1 = x0 + box_width
    y1 = y0 + box_height

    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        fill=(20, 20, 20, 200),
        radius=radius
    )

    # Draw legend rows
    for i, (color, name) in enumerate(unique_items):
        y = y0 + padding + i * line_height
        draw.rounded_rectangle(
            [x0 + 10, y, x0 + 10 + color_box_size, y + color_box_size],
            fill=color,
            radius=6
        )
        draw.text((x0 + 20 + color_box_size, y), name, fill="white", font=font)

    return png.convert("RGB")


# --------------------------- LOAD SAVE FILES ---------------------------
save_files = [
    os.path.join(save_folder, f)
    for f in os.listdir(save_folder)
    if f.lower().endswith(".json")
]
save_files.sort(key=os.path.getctime)

if not save_files:
    print("No .json save files found. Exiting.")
    exit()

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

# --------------------------- ADD LEGEND ---------------------------
if add_legend_flag:
    for i in range(len(thumbnails)):
        thumbnails[i] = add_legend(thumbnails[i], line_info[i])

# --------------------------- EXPORT GIF ---------------------------
if export_gif:
    print("Creating GIF...")
    gif_frames = [im.convert("P", palette=Image.ADAPTIVE) for im in thumbnails]

    gif_path = output_name + ".gif"
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
    last_png = thumbnails[-1]
    last_path = output_name + "_LAST.png"
    last_png.save(last_path)
    print(f"Last save exported as {last_path}")
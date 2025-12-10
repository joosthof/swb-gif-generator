import os
import json
import re
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from PIL import ImageDraw, ImageFont, ImageColor

save_folder = "C:/Users/oosth/OneDrive/Documenten/SubwayBuilder/saves/pjil"
output_name = "evolution"
fps = 1
export_gif = True
TARGET_RES = 2000
THREADS = 4
add_legend = True


def add_background(svg_text, color="#1e1e1e"):
    return svg_text.replace(">", f"><rect width='100%' height='100%' fill='{color}'/>", 1)

def thin_lines(svg_text, new_width=2.5):
    return re.sub(r'stroke-width="[\d\.]+"', f'stroke-width="{new_width}"', svg_text)

def extract_svg_and_colors(path):
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
    line_colors = {str(i+1): c for i, c in enumerate(colors)}

    return svg, line_colors

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
    return Image.open(png_bytes).convert("RGB")

def render_task(path):
    svg, line_colors = extract_svg_and_colors(path)

    if not svg:
        return None, {}

    svg = add_background(svg, "#1e1e1e")
    svg = thin_lines(svg, 2)

    try:
        png = svg_to_png(svg, TARGET_RES)
        return png, line_colors
    except Exception as e:
        print(f"SVG error in {os.path.basename(path)}: {e}")
        return None, {}

save_files = [
    os.path.join(save_folder, f)
    for f in os.listdir(save_folder)
    if f.lower().endswith(".json")
]

save_files.sort(key=os.path.getctime)

if not save_files:
    print("No .json save files found. Exiting.")
    exit()

print("Rendering thumbnails...")
thumbnails = []
line_info = []

with ThreadPoolExecutor(max_workers=THREADS) as executor:
    for png, lines in tqdm(executor.map(render_task, save_files),
                           total=len(save_files), desc="Thumbnails"):
        if png:
            thumbnails.append(png)
            line_info.append(lines)

if not thumbnails:
    print("No SVG thumbnails extracted.")
    exit()

def add_legend(png, line_colors):
    if not line_colors:
        return png

    draw = ImageDraw.Draw(png)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    padding = 10
    line_height = 36

    longest_name = max((f"Line {k}" for k in line_colors.keys()), key=len)
    name_width = draw.textlength(longest_name, font=font)
    box_width = 60 + name_width + 20
    box_height = line_height * len(line_colors) + padding * 2

    x0 = png.width - box_width - 20
    y0 = 20
    x1 = x0 + box_width
    y1 = y0 + box_height

    draw.rectangle([x0, y0, x1, y1], fill=(30, 30, 30, 200))

    for i, (line_id, color) in enumerate(line_colors.items()):
        y = y0 + padding + i * line_height
        # Color box
        draw.rectangle([x0 + 10, y, x0 + 50, y + 30], fill=color)
        # Line label
        draw.text((x0 + 60, y), f"Line {line_id}", fill="white", font=font)

    return png

if add_legend == True:
    for i in range(len(thumbnails)):
        thumbnails[i] = add_legend(thumbnails[i], line_info[i])

for i, lines in enumerate(line_info):
    print(f"\nFile: {os.path.basename(save_files[i])}")
    if not lines:
        print("  No line colors found")
    else:
        for line_id, color in lines.items():
            print(f"  Line {line_id}: {color}")

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
        optimize=True,
    )

    print(f"GIF saved as {gif_path}")

import os
import json
from PIL import Image
from io import BytesIO
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import webbrowser

save_folder = "C:/Users/oosth/OneDrive/Documenten/SubwayBuilder/saves/pjil"
output_name = "evolution"
fps = 1
export_gif = True
TARGET_RES = 2000
THREADS = 4

def add_background(svg_text, color="#1e1e1e"):
    return svg_text.replace(
        ">", f"><rect width='100%' height='100%' fill='{color}'/>", 1
    )

def thin_lines(svg_text, new_width=2.5):
    return re.sub(r'stroke-width="[\d\.]+"', f'stroke-width="{new_width}"', svg_text)

def extract_svg_from_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON in {path}: {e}")
        return None
    return data.get("routeThumbnail", None)

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
    svg = extract_svg_from_json(path)
    if not svg:
        return None
    svg = add_background(svg, "#1e1e1e")
    svg = thin_lines(svg, 2)
    try:
        return svg_to_png(svg, TARGET_RES)
    except Exception as e:
        print(f"SVG error in {os.path.basename(path)}: {e}")
        return None

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
with ThreadPoolExecutor(max_workers=THREADS) as executor:
    for result in tqdm(executor.map(render_task, save_files), total=len(save_files), desc="Thumbnails"):
        if result:
            thumbnails.append(result)

if not thumbnails:
    print("No SVG thumbnails extracted.")
    exit()

if export_gif:
    print("Creating GIF...")
    gif_frames = [im.convert("P", palette=Image.ADAPTIVE) for im in tqdm(thumbnails, desc="Converting frames")]

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

    try:
        webbrowser.open(gif_path)
    except Exception as e:
        print(f"Could not open GIF automatically: {e}")

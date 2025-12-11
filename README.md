# Subwaybuilder GIF Generator

Create animated GIFs showing the evolution of your **SubwayBuilder** city — directly from your save files.  
No Python installation required. Just configure, double-click, and enjoy the animation.

⚠️ **Note:** The `.exe` method is **not compatible with macOS**.  
If you want to use this tool on macOS, you'll need to install Python and run the source code manually.  
A tutorial for macOS users will be provided soon!

---

## 📦 Download

Go to the latest release:

👉 **https://github.com/joosthof/swb-gif-generator/releases/tag/v0.1.0**

Download these two files:

- `swb.exe`
- `config.json`

Place both files together in the **same folder** (any folder you like):

---

## ⚙️ Step 1 — Configure

Open `config.json` in any text editor (Notepad is fine). Then, set the save folder variable to the location of your JSON files.

- `save_folder` — folder containing your `.metro` saves  
- `output_file` — name of the GIF to generate  
- `fps` — frames per second of the GIF  
- `target_res` — resolution for each frame  
- `threads` — CPU threads to use  
- `add_legend` — add a color/name legend to frames  
- `background_color` — background hex color  
- `export_gif` — whether to export a GIF  
- `color_to_name` — map of line colors → line names

Example:

```json
{
  "save_folder": "C:/Users/YourName/Documents/SubwayBuilder/saves/MyCity",
  "output_file": "my_city.gif",
  "fps": 1,
  "target_res": 2000,
  "threads": 4,
  "add_legend": true,
  "background_color": "#1e1e1e",
  "export_gif": true,
  "color_to_name": {
    "#ffa300": "L",
    "#ff6319": "J",
    "#00933c": "W",
    "#0039a6": "MA"
  }
}
```

---

## ▶️ Step 2 — Run the Program

1. Open the folder where `swb.exe` and `config.json` are located.
2. Right-click inside the folder → **Open in Terminal**.
3. Run the following command: `./swb.exe`
4. The program will print all line colors found in your saves. Add these colors (with line names) to the `color_to_name` section in `config.json`. And edit any other setting you'd like.
5. When finished, simply **double-click `swb.exe`** to generate the GIF.

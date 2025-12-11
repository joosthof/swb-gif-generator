# Subwaybuilder GIF Generator

Create animated GIFs showing the evolution of your **SubwayBuilder** city — directly from your save files.  
No Python installation required. Just configure, double-click, and enjoy the animation.

---

## 📦 Download

Go to the latest release:

👉 **https://github.com/joosthof/swb-gif-generator/releases/tag/v0.1.0**

Download these two files:

- `swb.exe`
- `config.json`

Place both files together in the **same folder** (any folder you like):

---

---

## ⚙️ Step 1 — Configure

Open `config.json` in any text editor (Notepad is fine).

Fill in the following fields:

- `save_folder` — the folder where SubwayBuilder stores your `.metro` saves  
- `output_file` — name of the GIF that will be created  
- `threads` — number of threads to use (recommended: 4)

Example config:

```json
{
    "save_folder": "C:/Users/YourName/Documents/SubwayBuilder/saves/MyCity",
    "output_file": "my_city.gif",
    "threads": 4
}

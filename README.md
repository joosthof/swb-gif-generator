# Subwaybuilder GIF Generator

Create animated GIFs showing the evolution of your **SubwayBuilder** city — directly from your save files.  
No Python installation required. Just configure, double-click, and enjoy the animation.

---

# Windows

---

## 📦 Download

Go to the latest release:

👉 **https://github.com/joosthof/swb-gif-generator/releases/tag/v0.2.0**

Download these two files:

- `win_executable.zip`

Extract the file to any folder you like:

---

## ⚙️ Step 1 — Save your games as JSON files

1. Click **Load/Save** in SubwayBuilder.
2. Click **Export Current Game**.
3. Choose **Legacy JSON (.json)** and save the file.
> **Note:** Save the `.json` files in a different folder than the `.metro` files!

---

## ⚙️ Step 2 — Configure

Open `config.json` in any text editor (Notepad is fine). Then, set the save folder variable to the location of your JSON files.
**Note:** The path should NOT include single backslashes. Only double backslashes or single forward slashes: ```"C:/Users/YourName/Documents/SubwayBuilder/saves/MyCity"``` or ```"C:\\Users\\YourName\\Documents\\SubwayBuilder\\saves\\MyCity"```

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

## ▶️ Step 3 — Run the Program

1. Open the folder where `swb.exe` and `config.json` are located.
2. Right-click inside the folder → **Open in Terminal**.
3. Run the following command: `./swb.exe`
4. The program will print all line colors found in your saves. Add these colors (with line names) to the `color_to_name` section in `config.json`. And edit any other setting you'd like.
5. When finished, simply **run the command again (`./swb.exe`)** to generate the GIF.

---

# MacOS:

---

## 📦 Download (macOS)

Go to the latest release:

👉 **https://github.com/joosthof/swb-gif-generator/releases/tag/v0.1.0**

Download these two files:

- `macos-executable.zip`  
- `config.json`  

Extract `macos-executable.zip` and place both files together in the **same folder** (any folder you like).

> **Note:** macOS executables do not have `.exe` extensions. The file `swb` is already runnable.

---

## ⚙️ Step 1 — Save your games as JSON files

1. Click **Load/Save** in SubwayBuilder.  
2. Click **Export Current Game**.  
3. Choose **Legacy JSON (.json)** and save the file.
> **Note:** Save the `.json` files in a different folder than the `.metro` files!

---

## ⚙️ Step 2 — Configure

Open `config.json` in any text editor (TextEdit works fine — use **Plain Text mode**). Then, set the save folder variable to the location of your JSON files.  

**Note:** On macOS, paths use forward slashes (`/`) only. Example: `"/Users/YourName/Documents/SubwayBuilder/saves/MyCity"`

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
  "save_folder": "/Users/YourName/Documents/SubwayBuilder/saves/MyCity",
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

## ▶️ Step 3 — Run the Program (macOS)

1. Open the folder where `swb` and `config.json` are located.  
2. Open **Terminal**:
   - Right-click the folder → **Services → New Terminal at Folder**,  
   - or open Terminal and `cd` into the folder manually.
3. Make the executable runnable (first time only): `chmod +x ./swb`
4. Run the program by typing: `./swb`
5. The program will print all line colors found in your saves.
   - Add these colors (with line names) to the `color_to_name` section in `config.json`.
   - Edit any other settings you want (e.g., fps, output_file, target_res).
6. When finished, run the command again to generate the GIF: `./swb`


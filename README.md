# Subwaybuilder GIF Generator

Create animated GIFs showing the evolution of your **SubwayBuilder** city — directly from your save files.  
No Python installation required. Just configure, double-click, and enjoy the animation.

⚠️ **Note:** The `.exe` method is **not compatible with macOS**.  
If you want to use this tool on macOS, you'll need to install Python and run the source code manually.

---

## 📦 Download

Go to the latest release:

👉 **https://github.com/joosthof/swb-gif-generator/releases/tag/v0.1.0**

Download these two files:

- `swb.exe`
- `config.json`

Place both files together in the **same folder** (any folder you like):

---

## ⚙️ Step 1 — Save your games as JSON files

1. Click **Load/Save** in SubwayBuilder.
2. Click **Export Current Game**.
3. Choose **Legacy JSON (.json)** and save the file.

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

# For MacOS users:

---

## 📦 Step 1 — Install Python
**Note:** If you already have Python **3.10.6+** installed, you can skip this step.

1. Go to the official Python website: https://www.python.org/downloads/macos/ and download the latest macOS installer (`.pkg`).
2. Open the downloaded `.pkg` file and follow the installation steps.
3. After installation, open **Terminal** and verify Python by running: ```bash python3 --version```

---

## ⚙️ Step 2 — Save your games as JSON files

1. Click **Load/Save** in SubwayBuilder.
2. Click **Export Current Game**.
3. Choose **Legacy JSON (.json)** and save the file.

---

## 📥 Step 3 — Download the Source Code

1. Download the latest version of the project from https://github.com/joosthof/swb-gif-generator
2. Extract the downloaded `.zip` file to any folder on your Mac.
3. Open Terminal and navigate to the extracted project folder: ```bash cd /path/to/SubwayBuilder-GIF-Generator```
4. Install Python dependencies by running **requirements.txt** with ```pip3 install -r requirements.txt```
   **Note:** If you get a permission error, run ```pip3 install --user -r requirements.txt``` instead.

---

## 🖥️ Step 4 — Running the Source Code
1. Open `config.json` in any text editor (Notepad is fine). Then, set the save folder variable to the location of your JSON files.
   **Note:** The path should NOT include single backslashes. Only double backslashes or single forward slashes: ```"C:/Users/YourName/Documents/SubwayBuilder/saves/MyCity"``` or ```"C:\\Users\\YourName\\Documents\\SubwayBuilder\\saves\\MyCity"```
3. Open the folder where the source code is located and run open **Terminal**
4. Run the command ```python extract_colors.py```.
5. The program will print all line colors found in your saves. Add these colors (with line names) to the `color_to_name` section in `config.json`. And edit any other setting you'd like.
6. Run the following command: `python swb.py` to generate the GIF


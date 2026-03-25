🌐 **Read this in other languages:** [English](README.md) | [🇰🇷 한국어 (Korean)](README_ko.md)

# AI Batch Background Remover

A professional, offline, and completely free desktop application for removing image backgrounds in bulk. Built with Python, this tool runs locally on your machine without requiring any expensive API keys or internet connection for the core AI processing.

## 🚀 Features
* **100% Offline & Free:** No API limits, no subscription fees.
* **Batch Processing:** Process a single image or an entire folder of images at once.
* **AI-Powered:** Uses the highly accurate `rembg` library (based on the U2Net model).
* **Intuitive GUI:** Easy-to-use drag-and-drop interface built with `Tkinter`.
* **Standalone Executable:** Available as a single `.exe` file for Windows users (No Python installation required).

## 🛠️ Tech Stack
* **Core Logic:** Python 3.10+
* **AI Model:** `rembg`
* **GUI Framework:** `Tkinter` / `tkinterdnd2`
* **Package Manager:** `uv`
* **Build Tool:** `PyInstaller`

## 📦 Download & Run (For General Users)
You don't need to be a developer to use this tool. 
1. Go to the [Releases](../../releases) page.
2. Download the latest `BgRemover.exe`.
3. Double-click to run and start removing backgrounds!

## 💻 Quick Start (For Developers)
If you want to run from the source code or build it yourself:

### 1. Clone the repository
```bash
git clone [https://github.com/gohard-lab/batch_bg_remover.git](https://github.com/gohard-lab/batch_bg_remover.git)
cd batch_bg_remover
```
### 2. Install dependencies using uv (Fastest way)
```Bash
uv sync
```
### 3. Run the application
```Bash
uv run python src/main.py
```
### 4. Build the EXE (Optional)
```Bash
uv run pyinstaller --noconsole --onefile --copy-metadata pymatting src/main.py
```

## 📺 Video Tutorial
Want to understand the code or see how this tool was built from scratch? Check out the full step-by-step developer guide on my YouTube channel.

* [**Watch the Tutorial Video**] (https://youtu.be/HzuSu2b_5N4)

📊 Privacy & Transparency
※ This program collects minimal, anonymized usage statistics (e.g., feature click counts) to improve service and fix errors. No personally identifiable information is collected.

📄 License
This project is open-source and available under the MIT License.

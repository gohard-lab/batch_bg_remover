import os
import sys
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Style
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES

from processor import process_images
from tracker_exe import log_app_usage 

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path.cwd()

CONFIG_FILE = BASE_DIR / "config.json"

class BgRemoverApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Batch Background Remover")
        self.geometry("500x350")
        self.resizable(False, False)
        
        self.input_paths = []
        self.output_dir = tk.StringVar()
        
        self.load_config()
        self._build_ui()
        
        log_app_usage("batch_bg_remover", "app_opened")

    def _build_ui(self):
        self.drop_frame = tk.Frame(self, bg="#f0f0f0", bd=5, relief="solid")
        self.drop_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        self.default_drop_text = "Drag and drop images or folders here\n(or click to select)"
        self.drop_label = tk.Label(
            self.drop_frame, text=self.default_drop_text, bg="#f0f0f0", fg="#555555", font=("", 10)
        )
        self.drop_label.pack(expand=True)
        
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_frame.bind("<Button-1>", lambda e: self.select_input_folder())
        self.drop_label.bind("<Button-1>", lambda e: self.select_input_folder())

        output_frame = tk.Frame(self)
        output_frame.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(output_frame, text="Output Folder:").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir, state='readonly', width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="Change Path", command=self.select_output_folder).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Ready...")
        tk.Label(self, textvariable=self.status_var).pack(pady=5)
        
        self.progress = Progressbar(self, orient=tk.HORIZONTAL, length=460, mode='determinate')
        self.progress.pack(pady=5)

        self.start_btn = tk.Button(self, text="Start Processing", command=self.start_processing, bg="#4CAF50", fg="white", font=("", 10, "bold"))
        self.start_btn.pack(pady=10, ipadx=10, ipady=5)

    def update_dropzone_ui(self, message):
        self.drop_label.config(text=message, fg="#0052cc", font=("", 11, "bold"))

    def reset_dropzone_ui(self):
        self.drop_label.config(text=self.default_drop_text, fg="#555555", font=("", 10, "normal"))

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.input_paths = list(files)
        self.status_var.set(f"{len(self.input_paths)} items selected.")
        self.update_dropzone_ui(f"✅ {len(self.input_paths)} items recognized!")
        
        log_app_usage("batch_bg_remover", "input_received", {"method": "drag_and_drop", "item_count": len(self.input_paths)})

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_paths = [folder]
            folder_name = Path(folder).name
            self.status_var.set(f"Selected folder: {folder_name}")
            self.update_dropzone_ui(f"✅ Folder '{folder_name}' recognized!")
            
            log_app_usage("batch_bg_remover", "input_received", {"method": "folder_select", "item_count": 1})

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir.set(folder)
            self.save_config()

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.output_dir.set(config.get("output_dir", str(BASE_DIR / "output")))
            except:
                self.output_dir.set(str(BASE_DIR / "output"))
        else:
            self.output_dir.set(str(BASE_DIR / "output"))

    def save_config(self):
        config_data = {"output_dir": self.output_dir.get()}
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
        except:
            pass

    def update_progress(self, current, total):
        percent = (current / total) * 100
        self.progress['value'] = percent
        self.status_var.set(f"Processing... ({current}/{total})")
        self.update_idletasks()

    def start_processing(self):
        if not self.input_paths:
            messagebox.showwarning("Warning", "Please add images or a folder first.")
            return
        if not self.output_dir.get():
            messagebox.showwarning("Warning", "Please specify an output folder.")
            return

        log_app_usage("batch_bg_remover", "process_started")

        self.save_config()
        self.start_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_var.set("Loading AI model...")
        self.update_dropzone_ui("⚙️ Background removal in progress...")

        thread = threading.Thread(target=self._run_process_thread)
        thread.daemon = True
        thread.start()

    def _run_process_thread(self):
        success = process_images(
            input_paths=self.input_paths,
            output_folder=self.output_dir.get(),
            progress_callback=self.update_progress
        )
        
        if success:
            self.status_var.set("All tasks completed successfully!")
            messagebox.showinfo("Success", "Processing finished successfully.")
            
            log_app_usage("batch_bg_remover", "process_completed_successfully")
        else:
            self.status_var.set("No valid images found to process.")
            
        self.start_btn.config(state=tk.NORMAL)
        self.input_paths = [] 
        self.reset_dropzone_ui()
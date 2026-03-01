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

# 프로그램 실행 위치를 정확하게 추적하여 설정 파일(config.json)의 절대 경로를 고정
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path.cwd()

CONFIG_FILE = BASE_DIR / "config.json"

class BgRemoverApp(TkinterDnD.Tk):
    """
    드래그 앤 드롭을 지원하는 배경 제거 프로그램의 메인 GUI 클래스.
    """
    def __init__(self):
        super().__init__()
        self.title("AI 대량 이미지 배경 제거기")
        self.geometry("500x350")
        self.resizable(False, False)
        
        self.input_paths = []
        self.output_dir = tk.StringVar()
        
        self.load_config()
        self._build_ui()

    def _build_ui(self):
        self.drop_frame = tk.Frame(self, bg="#f0f0f0", bd=5, relief="solid")
        self.drop_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        self.default_drop_text = "여기에 이미지 파일이나 폴더를 드래그 앤 드롭 하세요\n(또는 클릭하여 폴더 선택)"
        self.drop_label = tk.Label(
            self.drop_frame, 
            text=self.default_drop_text, 
            bg="#f0f0f0", fg="#555555", font=("", 10)
        )
        self.drop_label.pack(expand=True)
        
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
        self.drop_frame.bind("<Button-1>", lambda e: self.select_input_folder())
        self.drop_label.bind("<Button-1>", lambda e: self.select_input_folder())

        output_frame = tk.Frame(self)
        output_frame.pack(pady=5, padx=20, fill=tk.X)
        
        tk.Label(output_frame, text="저장 폴더:").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir, state='readonly', width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="경로 변경", command=self.select_output_folder).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="대기 중...")
        tk.Label(self, textvariable=self.status_var).pack(pady=5)
        
        self.progress = Progressbar(self, orient=tk.HORIZONTAL, length=460, mode='determinate')
        self.progress.pack(pady=5)

        self.start_btn = tk.Button(self, text="배경 제거 시작", command=self.start_processing, bg="#4CAF50", fg="white", font=("", 10, "bold"))
        self.start_btn.pack(pady=10, ipadx=10, ipady=5)

    def update_dropzone_ui(self, message):
        self.drop_label.config(text=message, fg="#0052cc", font=("", 11, "bold"))

    def reset_dropzone_ui(self):
        self.drop_label.config(text=self.default_drop_text, fg="#555555", font=("", 10, "normal"))

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.input_paths = list(files)
        self.status_var.set(f"{len(self.input_paths)}개의 항목이 선택되었습니다.")
        self.update_dropzone_ui(f"✅ {len(self.input_paths)}개의 항목이 인식되었습니다!\n\n(아래 시작 버튼을 눌러주세요)")

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="입력 폴더 선택")
        if folder:
            self.input_paths = [folder]
            folder_name = Path(folder).name
            self.status_var.set(f"선택된 폴더: {folder_name}")
            self.update_dropzone_ui(f"✅ '{folder_name}' 폴더가 인식되었습니다!\n\n(아래 시작 버튼을 눌러주세요)")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="출력(저장) 폴더 선택")
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
        self.status_var.set(f"처리 중... ({current}/{total})")
        self.update_idletasks()

    def start_processing(self):
        if not self.input_paths:
            messagebox.showwarning("경고", "먼저 이미지 파일이나 폴더를 드래그해서 넣어주세요.")
            return
            
        if not self.output_dir.get():
            messagebox.showwarning("경고", "출력 폴더를 지정해 주세요.")
            return

        # 작업 시작 전 한 번 더 확실하게 현재 경로 설정 저장
        self.save_config()

        self.start_btn.config(state=tk.DISABLED)
        self.progress['value'] = 0
        self.status_var.set("AI 모델 로딩 중... (최초 1회 시간이 걸릴 수 있습니다)")
        
        self.update_dropzone_ui("⚙️ 배경 제거 작업이 진행 중입니다...")

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
            self.status_var.set("모든 배경 제거 작업이 완료되었습니다!")
            messagebox.showinfo("완료", "작업이 성공적으로 끝났습니다.")
        else:
            self.status_var.set("처리할 이미지를 찾지 못했습니다.")
            
        self.start_btn.config(state=tk.NORMAL)
        self.input_paths = [] 
        self.reset_dropzone_ui()
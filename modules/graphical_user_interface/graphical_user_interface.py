import tkinter as tk
from tkinter import ttk
import re

class GraphicalUserInterface:
    def __init__(self, root, device_options: list) -> None:
        self.root = root
        self.device_was_updated = False
        self.is_running_transcription_and_translation = False

        self._init_window()
        self._init_combo_box(device_options)
        self._init_progress_bar()
        self._init_button()
        self._init_text_area()

    def _init_window(self) -> None:
        self.root.title("Transcrição e tradução em tempo real (EN -> PT)")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.container = tk.Frame(self.root)
        self.container.pack(expand=True)

    def _init_combo_box(self, device_options) -> None:
        self.frame_combo_box = tk.Frame(self.container)
        self.frame_combo_box.pack()

        self.device_options = device_options
        self.device_option_selected = tk.StringVar(value=self.device_options[0])

        self.combo_box = ttk.Combobox(self.frame_combo_box, textvariable=self.device_option_selected, values=self.device_options, state='readonly')
        self.combo_box.pack()
        self.combo_box.config(width=20)
        self.combo_box.bind('<<ComboboxSelected>>', self._device_option_selected_changed)

    def _device_option_selected_changed(self, value) -> None:
        self.device_was_updated = True

    def get_device_index(self) -> int:
        return int(self.device_option_selected.get().split('INDEX:')[1].replace(')', ''))

    def _init_progress_bar(self) -> None:
        self.frame_progress = tk.Frame(self.container)
        self.frame_progress.pack(pady=15)

        style = ttk.Style()
        style.configure("TProgressbar", background='green')

        self.progress_bar = ttk.Progressbar(self.frame_progress, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack()

    def update_progress_bar(self, value):
        self.progress_bar["value"] = value

    def _init_button(self) -> None:
        self.frame_button = tk.Frame(self.container)
        self.frame_button.pack(pady=10)

        self.start_stop_button = tk.Button(self.frame_button, text="Começar", command=self.toggle_start_stop)
        self.start_stop_button.pack()

    def toggle_start_stop(self) -> None:
        self.is_running_transcription_and_translation = not self.is_running_transcription_and_translation

        if self.is_running_transcription_and_translation:
            self.start_stop_button.config(text="Parar")
        else:
            self.start_stop_button.config(text="Começar")

    def _init_text_area(self) -> None:
        self.frame_texts = tk.Frame(self.container)
        self.frame_texts.pack(pady=15)

        self.label_text1 = tk.Label(self.frame_texts, text="Transcrição:")
        self.label_text1.grid(row=0, column=0, sticky='w')
        self.text_area1 = tk.Text(self.frame_texts, height=20, width=40, padx=10, pady=10)
        self.text_area1.grid(row=1, column=0, pady=(0, 10))
        self.text_area1.config(state=tk.DISABLED)

        self.label_text2 = tk.Label(self.frame_texts, text="Tradução:")
        self.label_text2.grid(row=0, column=1, padx=(10, 0), sticky='w')
        self.text_area2 = tk.Text(self.frame_texts, height=20, width=40, padx=10, pady=10)
        self.text_area2.grid(row=1, column=1, padx=(10, 0), pady=(0, 10))
        self.text_area2.config(state=tk.DISABLED)

    def set_text_area_transcription(self, text: str) -> None:
        self._update_text_area(self.text_area1, text)

    def set_text_area_translation(self, text: str) -> None:
        self._update_text_area(self.text_area2, text)

    def _update_text_area(self, text_area, text: str) -> None:
        text_area.config(state=tk.NORMAL)
        text_area.delete(1.0, tk.END)
        formatted_text = self._format_text(text)
        text_area.insert(tk.END, formatted_text)
        text_area.config(state=tk.DISABLED)
        text_area.see(tk.END)

    def _format_text(self, text: str) -> str:
        formatted_text = re.sub(r'([.!?…]+)\s*', r'\1\n\n', text)  # Quebra após pontuações
        formatted_text = formatted_text.strip()  # Remove espaços no início e fim
        return f"...{formatted_text}"
    
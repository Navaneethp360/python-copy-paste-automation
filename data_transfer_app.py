import tkinter as tk
from tkinter import ttk
import pyperclip
import time
import keyboard
import threading
import os

class DataTransferApp:
    ACCENT_COLOR = "#007acc"
    BG_COLOR = "#ffffff"
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE = 10

    def __init__(self, master):
        self.master = master
        self.master.title("Data Transfer App")
        self.master.geometry("320x550")
        self.master.configure(bg=self.BG_COLOR)

        self.style = ttk.Style()
        self.style.theme_use('default')

        # Configure style for ttk buttons with rounded corners and accent color
        self.style.configure('Accent.TButton',
                             background=self.ACCENT_COLOR,
                             foreground='white',
                             font=(self.FONT_FAMILY, self.FONT_SIZE),
                             borderwidth=0,
                             focusthickness=3,
                             focuscolor='none',
                             padding=6)
        self.style.map('Accent.TButton',
                       background=[('active', '#005a9e')],
                       foreground=[('active', 'white')])

        # Configure style for ttk entry
        self.style.configure('TEntry',
                             font=(self.FONT_FAMILY, self.FONT_SIZE),
                             padding=5)

        # Configure style for labels
        label_font = (self.FONT_FAMILY, self.FONT_SIZE)

        # Add WELCOME header label at the very top
        self.welcome_label = tk.Label(master, text="WELCOME", bg=self.BG_COLOR, font=(self.FONT_FAMILY, self.FONT_SIZE + 4, 'bold'))
        self.welcome_label.pack(pady=(10, 5))

        self.mode_var = tk.StringVar(value="copy")

        # Add MODE section header above mode selector toggles
        self.mode_header_label = tk.Label(master, text="MODE", bg=self.BG_COLOR, font=(self.FONT_FAMILY, self.FONT_SIZE))
        self.mode_header_label.pack()

        # Mode selection frame
        self.mode_frame = tk.Frame(master, bg=self.BG_COLOR)
        self.mode_frame.pack(pady=5)

        # Use ttk Radiobuttons for better styling
        self.copy_mode_button = ttk.Radiobutton(self.mode_frame, text="Copy Mode", variable=self.mode_var, value="copy",
                                                command=self.update_mode_buttons)
        self.copy_mode_button.pack(side=tk.LEFT, padx=10)

        self.paste_mode_button = ttk.Radiobutton(self.mode_frame, text="Paste Mode", variable=self.mode_var, value="paste",
                                                 command=self.update_mode_buttons)
        self.paste_mode_button.pack(side=tk.LEFT, padx=10)

        self.update_mode_buttons()

        # Controls frame
        self.controls_frame = tk.Frame(master, bg=self.BG_COLOR)
        self.controls_frame.pack(pady=15)
        self.controls_label = tk.Label(self.controls_frame, text="Controls", bg=self.BG_COLOR, font=label_font)
        self.controls_label.pack(pady=(0, 10))
        self.start_button = ttk.Button(self.controls_frame, text="Start", command=self.start_process_thread, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = ttk.Button(self.controls_frame, text="Pause", command=self.pause_process, style='Accent.TButton')
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(self.controls_frame, text="Stop", command=self.stop_process, style='Accent.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Label to show current record info in paste mode
        self.record_label = tk.Label(master, text="", bg=self.BG_COLOR, font=label_font)
        self.record_label.pack(pady=10)

        # Stepper frame
        self.stepper_frame = tk.Frame(master, bg=self.BG_COLOR)
        self.stepper_frame.pack(pady=15)
        self.stepper_label = tk.Label(self.stepper_frame, text="Stepper", bg=self.BG_COLOR, font=label_font)
        self.stepper_label.pack(pady=(0, 10))
        self.prev_button = ttk.Button(self.stepper_frame, text="Previous", command=self.prev_record, style='Accent.TButton')
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(self.stepper_frame, text="Next", command=self.next_record, style='Accent.TButton')
        self.next_button.pack(side=tk.LEFT, padx=5)

        # File control frame
        self.file_control_frame = tk.Frame(master, bg=self.BG_COLOR)
        self.file_control_frame.pack(pady=15)
        self.file_control_label = tk.Label(self.file_control_frame, text="File Control", bg=self.BG_COLOR, font=label_font)
        self.file_control_label.pack(pady=(0, 10))
        self.open_txt_button = ttk.Button(self.file_control_frame, text="Open TXT File", command=self.open_txt_file, style='Accent.TButton')
        self.open_txt_button.pack(side=tk.LEFT, padx=5)
        self.flush_button = ttk.Button(self.file_control_frame, text="Flush Data", command=self.flush_data, style='Accent.TButton')
        self.flush_button.pack(side=tk.LEFT, padx=5)

        self.max_records_label = tk.Label(master, text="Max records to copy (optional):", bg=self.BG_COLOR, font=label_font)
        self.max_records_label.pack(pady=5)
        self.max_records_entry = ttk.Entry(master, style='TEntry')
        self.max_records_entry.pack(pady=5, ipadx=5, ipady=3)

        # Add footer label with welcome message
        self.footer_label = tk.Label(master, text="developed by Navaneeth P - 2025", bg=self.BG_COLOR, font=(self.FONT_FAMILY, self.FONT_SIZE - 2))
        self.footer_label.pack(side=tk.BOTTOM, pady=10)

        self.is_running = False
        self.is_paused = False
        self.data_file = "copied_data.txt"
        self.records = []
        self.current_index = 0
        self.paste_mode_active = False
        self.paste_thread = None
        self.paste_lock = threading.Lock()

        # Register global hotkeys
        keyboard.add_hotkey('shift+1', self.start_process_thread)
        keyboard.add_hotkey('shift+2', self.pause_process)
        keyboard.add_hotkey('shift+3', self.stop_process)


    def update_mode_buttons(self):
        # Update the appearance of mode buttons based on selection
        if self.mode_var.get() == "copy":
            self.copy_mode_button.state(['selected'])
            self.paste_mode_button.state(['!selected'])
        else:
            self.paste_mode_button.state(['selected'])
            self.copy_mode_button.state(['!selected'])

    def start_process_thread(self):
        if not self.is_running:
            threading.Thread(target=self.start_process, daemon=True).start()

    def open_txt_file(self):
        try:
            os.startfile(self.data_file)
        except Exception as e:
            print(f"Failed to open file: {e}")

    def start_process(self):
        if self.is_paused:
            print("Resuming process...")
            print("Please focus the target window where you want to paste data within 4 seconds...")
            time.sleep(4)  # Delay before resuming to allow user to place pointer
            self.is_paused = False
            self.is_running = True
        else:
            self.is_running = True
            print("Please focus the target window where you want to paste data within 4 seconds...")
            time.sleep(4)  # Delay before starting to allow user to place pointer
            if self.mode_var.get() == "copy":
                self.copy_data()
                return
            else:
                self.load_records()
                self.paste_mode_active = True
                self.update_record_label()
        if not self.paste_thread or not self.paste_thread.is_alive():
            self.paste_thread = threading.Thread(target=self.paste_loop, daemon=True)
            self.paste_thread.start()

    def pause_process(self):
        if self.is_running:
            self.is_paused = True
            self.is_running = False
            print(f"Process paused at record {self.current_index + 1}.")
            self.update_record_label()

    def flush_data(self):
        with self.paste_lock:
            try:
                with open(self.data_file, "w") as f:
                    f.truncate(0)
                self.records = []
                self.current_index = 0
                self.max_records_entry.delete(0, tk.END)  # Clear max records input
                print("Data file flushed successfully.")
                self.update_record_label()
            except Exception as e:
                print(f"Error flushing data file: {e}")

    def stop_process(self):
        self.is_running = False
        self.is_paused = False
        self.paste_mode_active = False
        self.current_index = 0
        print("Process stopped and index reset to 0.")
        self.update_record_label()

    def copy_data(self):
        with open(self.data_file, "a") as f:
            max_records = None
            try:
                max_records_input = self.max_records_entry.get()
                if max_records_input.strip():
                    max_records = int(max_records_input.strip()) * 2
            except ValueError:
                max_records = None

            count = 0
            while self.is_running:
                if max_records is not None and count >= max_records:
                    print(f"Reached max copy limit of {max_records} records.")
                    self.stop_process()
                    break
                time.sleep(0.1)
                keyboard.press_and_release('ctrl+c')
                time.sleep(0.1)
                data = pyperclip.paste()
                f.write(f"{data}\n")
                keyboard.press_and_release('tab')
                count += 1

    def load_records(self):
        try:
            with open(self.data_file, "r") as f:
                self.records = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.records = []

    def paste_loop(self):
        while self.is_running and self.paste_mode_active:
            if self.is_paused:
                time.sleep(0.5)
                continue
            with self.paste_lock:
                if 0 <= self.current_index < len(self.records):
                    data = self.records[self.current_index]
                    print(f"Pasting record {self.current_index + 1}/{len(self.records)}: {data}")
                    pyperclip.copy(data)
                    time.sleep(0.1)
                    keyboard.press_and_release('ctrl+v')
                    time.sleep(0.6)
                    keyboard.press_and_release('tab')
                    self.current_index += 1
                    self.update_record_label()
                else:
                    print("No more records to paste.")
                    self.stop_process()
                    break
            time.sleep(0.5)

    def update_record_label(self):
        if 0 <= self.current_index < len(self.records):
            self.record_label.config(text=f"Record {self.current_index + 1} of {len(self.records)}: {self.records[self.current_index]}")
        else:
            self.record_label.config(text="No record selected")

    def prev_record(self):
        with self.paste_lock:
            if self.paste_mode_active and self.current_index > 0:
                self.current_index -= 1
                self.update_record_label()

    def next_record(self):
        with self.paste_lock:
            if self.paste_mode_active and self.current_index < len(self.records) - 1:
                self.current_index += 1
                self.update_record_label()

if __name__ == "__main__":
    root = tk.Tk()
    app = DataTransferApp(root)
    root.mainloop()

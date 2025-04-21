import tkinter as tk
import pyperclip
import time
import keyboard
import threading

class DataTransferApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Transfer App")
        
        self.mode_var = tk.StringVar(value="copy")  # Default mode is copy

        self.copy_mode_button = tk.Radiobutton(master, text="Copy Mode", variable=self.mode_var, value="copy")
        self.copy_mode_button.pack(pady=10)

        self.paste_mode_button = tk.Radiobutton(master, text="Paste Mode", variable=self.mode_var, value="paste")
        self.paste_mode_button.pack(pady=10)

        self.start_button = tk.Button(master, text="Start", command=self.start_process_thread)
        self.start_button.pack(pady=10)

        self.pause_button = tk.Button(master, text="Pause", command=self.pause_process)
        self.pause_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_process)
        self.stop_button.pack(pady=10)

        # Label to show current record info in paste mode
        self.record_label = tk.Label(master, text="")
        self.record_label.pack(pady=10)

        # Buttons for stepping in paste mode
        self.prev_button = tk.Button(master, text="Previous", command=self.prev_record)
        self.next_button = tk.Button(master, text="Next", command=self.next_record)
        self.prev_button.pack(pady=5)
        self.next_button.pack(pady=5)

        self.flush_button = tk.Button(self.master, text="Flush Data", command=self.flush_data)
        self.flush_button.pack(pady=10)

        self.max_records_label = tk.Label(self.master, text="Max records to copy (optional):")
        self.max_records_label.pack(pady=5)
        self.max_records_entry = tk.Entry(self.master)
        self.max_records_entry.pack(pady=5)

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

    def start_process_thread(self):
        if not self.is_running:
            threading.Thread(target=self.start_process, daemon=True).start()

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

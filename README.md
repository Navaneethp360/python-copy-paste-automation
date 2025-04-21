# 📋 Data Transfer App

A simple yet powerful Python-based desktop app for automated copy-paste workflows.  
Supports both **Copy Mode** (auto-copy from active window) and **Paste Mode** (auto-paste from saved data) with global hotkeys and GUI control.

---

## 🔧 Features

- 🖱️ **GUI Interface** built using `tkinter` with custom styling
- 📎 **Copy Mode**: Automatically copies data using `Ctrl+C` and moves to the next field (`Tab`)
- 📤 **Paste Mode**: Pastes from a saved `.txt` file with a built-in stepper to review records
- ⏸️ Pause, Resume, and Stop operations easily
- ⌨️ **Global Hotkeys**:  
  - `Shift+1` → Start  
  - `Shift+2` → Pause  
  - `Shift+3` → Stop
- 🧾 Flush saved records and open text file directly
- 📌 Always stays **on top** of all other windows
- 🎯 Automatically tracks current record while pasting

---

## 🛠️ Technologies Used

| Tool        | Purpose                     |
|-------------|-----------------------------|
| `tkinter`   | GUI window and widgets      |
| `keyboard`  | Global hotkeys & key presses|
| `pyperclip` | Clipboard access            |
| `threading` | Async background operations |
| `os`        | File handling                |
| `ctypes`    | Set "always on top" window  |

---

## 🚀 Getting Started
### 1. Clone the repository:
```bash
git clone https://github.com/Navaneethp360/python-data-transfer-app.git
cd python-data-transfer-app
```

### 2. Run the App:
You can run the application either by using python data_transfer_app.py command in cmd 
OR
Locate the .exe file in the dist folder and run the application.

## 🎨 Screenshots
![image](https://github.com/user-attachments/assets/e3bbe4dc-c5d2-441f-8b9b-58dc902ca9db)




## 📌 Notes
Designed for Windows (due to use of keyboard and os.startfile)

Runs as a GUI-only app with no console (when compiled with --noconsole)

Handles clipboard and paste automation reliably with timing control

Keeps the app window always on top for easy access

## 🧑‍💻 Developed By
Navaneeth P — 2025

Feel free to connect or contribute!


import tkinter as tk
import pyautogui
import pytesseract
import threading
from groq import Groq
import os
import time
import datetime

# --- CONFIGURATION ---
TESSERACT_EXE = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

GROQ_API_KEY = "YOUR_API_KEY_HERE"
client = Groq(api_key=GROQ_API_KEY)
LOG_FILE = "ai_study_logs.txt"

class HusseinUltimateSniper:
    def __init__(self, root):
        self.root = root
        self.root.title("Hussein AI Sniper V6")
        self.selected_region = None
        self.is_running = True
        self.result_window = None
        self.setup_selector_ui()
        threading.Thread(target=self.solve_loop, daemon=True).start()

    def setup_selector_ui(self):
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.3)
        self.root.overrideredirect(True)
        sw, sh = pyautogui.size()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.start_x = self.start_y = self.rect = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline="red", width=2)

    def on_move_press(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y
        self.selected_region = (min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
        self.root.attributes("-alpha", 0.0)

    def save_to_permanent_log(self, raw_text, answer, logic):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"{'='*60}\nTIME: {timestamp}\n{'-'*60}\nEXTRACTED TEXT:\n{raw_text.strip()}\n\nAI ANSWER:\n{answer}\n\nREASONING:\n{logic}\n{'='*60}\n\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(entry)

    def solve_loop(self):
        while self.is_running:
            if self.selected_region:
                try:
                    shot = pyautogui.screenshot(region=self.selected_region)
                    text = pytesseract.image_to_string(shot, lang='eng')
                    if len(text.strip()) > 10:
                        res = client.chat.completions.create(
                            messages=[{"role": "user", "content": f"Analyze: {text}\nFormat:\nANSWER: [text]\nREASON: [text]"}],
                            model="llama-3.1-8b-instant"
                        )
                        full_res = res.choices[0].message.content
                        ans = full_res.split("ANSWER:")[1].split("REASON:")[0].strip() if "ANSWER:" in full_res else "N/A"
                        logic = full_res.split("REASON:")[1].strip() if "REASON:" in full_res else "N/A"
                        self.root.after(0, lambda: self.show_popup(ans))
                        self.save_to_permanent_log(text, ans, logic)
                        self.selected_region = None # Stop until next scan
                except Exception as e: print(f"Error: {e}")
            time.sleep(0.2)

    def reset_ui(self):
        self.selected_region = None
        if self.result_window: self.result_window.destroy()
        self.root.attributes("-alpha", 0.3)
        self.canvas.delete("all")

    def show_popup(self, text):
        self.result_window = tk.Toplevel()
        self.result_window.attributes("-topmost", True, "-toolwindow", True)
        self.result_window.overrideredirect(True)
        x, y, w, h = self.selected_region if self.selected_region else (100, 100, 300, 100)
        self.result_window.geometry(f"320x130+{x}+{max(0, y-140)}")
        self.result_window.configure(bg="#1a1a1a", padx=10, pady=10)
        tk.Label(self.result_window, text=f"AI: {text}", fg="#2ecc71", bg="#1a1a1a", font=("Segoe UI", 10, "bold"), wraplength=300).pack()
        btn_f = tk.Frame(self.result_window, bg="#1a1a1a")
        btn_f.pack(fill="x", pady=5)
        tk.Button(btn_f, text="🔄 New Scan", command=self.reset_ui, bg="#3498db", fg="white").pack(side="left", expand=True, fill="x")
        tk.Button(btn_f, text="❌ Exit", command=self.root.destroy, bg="#e74c3c", fg="white").pack(side="right", expand=True, fill="x")

if __name__ == "__main__":
    root = tk.Tk()
    app = HusseinUltimateSniper(root)
    root.mainloop()
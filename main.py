import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import qrcode
import cv2
from ab_qr import ABHistory, ab_timestamp

APP_TITLE = "QR Generátor + Olvasó"
BASE = Path(__file__).parent
OUT_DIR = BASE / "out"
DATA_DIR = BASE / "data"
HISTORY_PATH = DATA_DIR / "history.json"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x680")
        self.minsize(900, 600)

        self.history = ABHistory(HISTORY_PATH)
        self.current_qr_pil = None
        self.current_img_pil = None
        self.current_img_tk = None

        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Szöveg a QR-hez:").pack(side="left")
        self.text_var = tk.StringVar()
        self.text_entry = ttk.Entry(top, textvariable=self.text_var, width=60)
        self.text_entry.pack(side="left", padx=8)
        ttk.Button(top, text="QR generálás (Enter)", command=self.on_generate).pack(side="left")
        ttk.Button(top, text="PNG mentése (Ctrl+S)", command=self.on_save_qr).pack(side="left", padx=6)
        ttk.Button(top, text="Kép megnyitása (Ctrl+O)", command=self.on_open_image).pack(side="left")

        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.Frame(mid)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="Előnézet").pack(anchor="w")
        self.canvas = tk.Canvas(left, bg="#111")
        self.canvas.pack(fill="both", expand=True, pady=6)

        right = ttk.Frame(mid, width=300)
        right.pack(side="left", fill="y")
        ttk.Label(right, text="Felismert adat").pack(anchor="w", pady=(0,4))
        self.decoded_var = tk.StringVar()
        self.decoded_label = ttk.Label(right, textvariable=self.decoded_var, wraplength=280)
        self.decoded_label.pack(fill="x", pady=(0,10))
        ttk.Label(right, text="Előzmények").pack(anchor="w")
        self.hist_list = tk.Listbox(right, height=20)
        self.hist_list.pack(fill="both", expand=True)
        ttk.Button(right, text="Előzmény megnyitása", command=self.on_open_from_history).pack(pady=6)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(0,10))
        ttk.Label(bottom, text="Billentyűk: Enter = generálás, Ctrl+S = mentés, Ctrl+O = megnyitás").pack(anchor="w")

        self.bind("<Return>", lambda e: self.on_generate())
        self.bind("<Control-s>", lambda e: self.on_save_qr())
        self.bind("<Control-o>", lambda e: self.on_open_image())
        self.canvas.bind("<Configure>", lambda e: self.redraw_canvas())

        self.refresh_history()
        self.text_entry.focus_set()

    def on_generate(self):
        text = self.text_var.get().strip()
        if not text:
            messagebox.showinfo("Hiányzó szöveg", "Írj be szöveget a QR generáláshoz.")
            return
        img = qrcode.make(text)
        self.current_qr_pil = img
        self.decoded_var.set("")
        self.show_image(img)
        ts = ab_timestamp()
        self.history.add("generate", text, "", ts)
        self.refresh_history()

    def on_save_qr(self):
        if self.current_qr_pil is None:
            messagebox.showinfo("Nincs QR", "Előbb generálj QR kódot.")
            return
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = ab_timestamp()
        path = OUT_DIR / f"AB_qr_{ts}.png"
        self.current_qr_pil.save(path)
        messagebox.showinfo("Mentve", str(path))
        self.history.add("save_qr", self.text_var.get(), str(path), ts)
        self.refresh_history()

    def on_open_image(self):
        filetypes = [("Képek", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"), ("Minden fájl", "*.*")]
        p = filedialog.askopenfilename(title="Kép megnyitása", filetypes=filetypes)
        if not p:
            return
        self.load_and_decode(Path(p))

    def on_open_from_history(self):
        sel = self.hist_list.curselection()
        if not sel:
            return
        idx = sel[0]
        items = self.history.recent(200)
        item = items[idx]
        image_path = item.get("image_path") or ""
        if image_path and Path(image_path).exists():
            self.load_and_decode(Path(image_path))

    def load_and_decode(self, path: Path):
        try:
            pil_img = Image.open(path)
        except Exception as e:
            messagebox.showerror("Hiba", f"Nem sikerült megnyitni: {e}")
            return
        self.current_img_pil = pil_img
        self.show_image(pil_img)
        img_cv = cv2.imread(str(path))
        if img_cv is None:
            self.decoded_var.set("Nem olvasható kép")
            return
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        detector = cv2.QRCodeDetector()
        data, points, straight_qrcode = detector.detectAndDecode(gray)
        if data:
            self.decoded_var.set(data)
        else:
            self.decoded_var.set("Nem találtam QR kódot")
        ts = ab_timestamp()
        self.history.add("decode", self.decoded_var.get(), str(path), ts)
        self.refresh_history()

    def show_image(self, pil_img: Image.Image):
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 500
        img = pil_img.copy()
        img.thumbnail((cw - 20, ch - 20))
        self.current_img_tk = ImageTk.PhotoImage(img)
        self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        if self.current_img_tk:
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            iw = self.current_img_tk.width()
            ih = self.current_img_tk.height()
            x = (cw - iw) // 2
            y = (ch - ih) // 2
            self.canvas.create_image(x, y, image=self.current_img_tk, anchor="nw")

    def refresh_history(self):
        self.hist_list.delete(0, "end")
        for item in self.history.recent(200):
            line = f"{item['ts']} | {item['action']} | {item['text'][:30]}"
            self.hist_list.insert("end", line)

if __name__ == "__main__":
    app = App()
    app.mainloop()

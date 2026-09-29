"""Small local desktop interface for the Mavic panorama stitcher."""
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from PIL import Image, ImageTk

from stitch import stitch, collect
from viewer import PanoramaViewer
from branding import NAME, CREDIT, ASSETS, set_icon


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(NAME + " | Ahmad Alhasanat")
        set_icon(self)
        self.geometry("840x720")
        self.minsize(760, 650)
        self.folder = tk.StringVar()
        self.output = tk.StringVar()
        self.resolution = tk.StringVar(value="8000 × 4000 — High")
        ttk.Label(self, text=CREDIT, anchor="center").pack(side="bottom", fill="x", pady=10)
        frame = ttk.Frame(self, padding=18)
        frame.pack(fill="both", expand=True)
        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 12))
        with Image.open(ASSETS / 'logo.jpg') as source:
            logo = source.copy()
            logo.thumbnail((65, 75), Image.Resampling.LANCZOS)
        self.logo = ImageTk.PhotoImage(logo)
        ttk.Label(header, image=self.logo).pack(side="left", padx=(0, 18))
        ttk.Label(header, text=NAME, font=("Arial", 24, "bold")).pack(side="left")
        ttk.Label(frame, text="Select one capture folder with source photos and its DJI CSV. Review your result in the 360 viewer.", wraplength=670).pack(anchor="w", pady=(4, 18))
        self.row(frame, "Source folder", self.folder, self.pick_folder)
        self.row(frame, "Output image", self.output, self.pick_output)
        settings = ttk.Frame(frame)
        settings.pack(fill="x", pady=10)
        ttk.Label(settings, text="Panorama resolution").pack(side="left")
        ttk.Combobox(settings, textvariable=self.resolution, state="readonly", width=30,
                     values=["4000 × 2000 — Preview", "8000 × 4000 — High", "12000 × 6000 — Ultra"]).pack(side="left", padx=12)
        ttk.Label(frame, text="Choose PNG or TIFF for lossless export. Ultra uses more memory and processing time.").pack(anchor="w")
        self.button = ttk.Button(frame, text="Stitch panorama", command=self.start)
        self.button.pack(anchor="w", pady=10)
        self.viewer_button = ttk.Button(frame, text="Open 360 viewer", command=self.open_viewer)
        self.viewer_button.pack(anchor="w", pady=(0, 10))
        self.log = tk.Text(frame, height=6, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)
        self.preview = ttk.Label(frame, text="Your stitched panorama preview will appear here.")
        self.preview.pack(fill="x", pady=(12, 0))

    def row(self, parent, label, variable, action):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label, width=15).pack(side="left")
        ttk.Entry(row, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Browse…", command=action).pack(side="left", padx=(8, 0))

    def pick_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder.set(path)
            if not self.output.get():
                self.output.set(str(Path(path).parent / (Path(path).name + "_panorama.jpg")))
            try:
                self.write(f"Found {len(collect(path))} images in this folder.")
            except Exception as exc:
                self.write(str(exc))

    def pick_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg"), ("PNG lossless", "*.png"), ("TIFF lossless", "*.tif")])
        if path:
            self.output.set(path)

    def write(self, line):
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start(self):
        try:
            edge = int(self.resolution.get().split()[0]) // 2
            if edge < 512:
                raise ValueError("Input max edge must be at least 512 pixels.")
            folder, output = Path(self.folder.get()), Path(self.output.get())
            collect(folder)
            if not output.name or output.suffix.lower() not in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
                raise ValueError("Choose an output filename ending in .jpg, .png or .tif")
            if output.resolve() in [p.resolve() for p in collect(folder)]:
                raise ValueError("Output must not overwrite an input image.")
        except Exception as exc:
            messagebox.showerror("Check input", str(exc))
            return
        self.button.configure(state="disabled")
        self.write("Starting...")

        def worker():
            try:
                result = stitch(folder, output, edge, lambda msg: self.after(0, self.write, msg))
                self.after(0, self.show_preview, result)
            except Exception as exc:
                self.after(0, self.write, f"ERROR: {exc}")
            finally:
                self.after(0, lambda: self.button.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    def show_preview(self, path):
        try:
            with Image.open(path) as source:
                thumb = source.copy()
            thumb.thumbnail((660, 90), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(thumb)
            self.preview.configure(image=photo, text="")
            self.preview.image = photo
        except Exception as exc:
            self.write(f"Preview unavailable: {exc}")

    def open_viewer(self):
        path = Path(self.output.get())
        if not path.is_file():
            selected = filedialog.askopenfilename(filetypes=[("Panorama images", "*.jpg *.jpeg *.png *.tif *.tiff")])
            if not selected:
                return
            path = Path(selected)
        try:
            PanoramaViewer(self, path)
        except Exception as exc:
            messagebox.showerror("360 viewer", str(exc))


if __name__ == "__main__":
    App().mainloop()

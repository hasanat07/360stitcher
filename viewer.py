"""Interactive local 360 viewer for equirectangular images."""
import math
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from branding import set_icon, CREDIT

import numpy as np
from PIL import Image, ImageTk


def render_view(texture, width, height, yaw, pitch, fov):
    """Render a perspective view; black source pixels remain black."""
    yy, xx = np.mgrid[0:height, 0:width]
    focal = (width / 2) / math.tan(math.radians(fov) / 2)
    right = (xx - (width - 1) / 2) / focal
    up = ((height - 1) / 2 - yy) / focal
    norm = np.sqrt(1 + right * right + up * up)
    forward = 1 / norm
    right /= norm
    up /= norm
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    wx = forward * cp * sy + right * cy - up * sp * sy
    wy = forward * cp * cy - right * sy - up * sp * cy
    wz = forward * sp + up * cp
    lon = np.arctan2(wx, wy)
    lat = np.arcsin(np.clip(wz, -1, 1))
    th, tw = texture.shape[:2]
    # Bilinear sampling removes blocky nearest-neighbour zoom.
    u = (lon + np.pi) / (2 * np.pi) * tw - 0.5
    v = np.clip((np.pi / 2 - lat) / np.pi * th - 0.5, 0, th - 1)
    x0 = np.floor(u).astype(np.int32); y0 = np.floor(v).astype(np.int32)
    dx = (u - x0)[:,:,None]; dy = (v - y0)[:,:,None]
    x1 = (x0 + 1) % tw; x0 %= tw
    y1 = np.minimum(y0 + 1, th - 1)
    return ((texture[y0,x0] * (1-dx) + texture[y0,x1]*dx) * (1-dy) +
            (texture[y1,x0] * (1-dx) + texture[y1,x1]*dx) * dy).astype(np.uint8)



class PanoramaViewer(tk.Toplevel):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.title(f"360 viewer — {Path(path).name}")
        self.geometry("980x620")
        set_icon(self)
        self.yaw = 0.0
        self.pitch = 0.0
        self.fov = 75.0
        self.drag_origin = None
        self.render_job = None
        with Image.open(path) as source:
            image = source.convert("RGB")
            image.thumbnail((8192, 4096), Image.Resampling.LANCZOS)
            self.texture = np.asarray(image).copy()
        ttk.Label(self, text=CREDIT, anchor="center").pack(side="bottom", fill="x", pady=5)
        toolbar = ttk.Frame(self, padding=10)
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="Drag to look around • Mouse wheel to zoom • Black areas are missing image coverage").pack(side="left")
        ttk.Button(toolbar, text="Reset view", command=self.reset).pack(side="right")
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda _: self.zoom(-1))
        self.canvas.bind("<Button-5>", lambda _: self.zoom(1))
        self.canvas.bind("<Configure>", lambda _: self.schedule_render())
        self.after(50, self.render)

    def reset(self):
        self.yaw = self.pitch = 0.0
        self.fov = 75.0
        self.schedule_render()

    def on_press(self, event):
        self.drag_origin = (event.x, event.y)

    def on_drag(self, event):
        if self.drag_origin is None:
            return
        old_x, old_y = self.drag_origin
        self.yaw -= (event.x - old_x) * math.radians(self.fov) / max(1, self.canvas.winfo_width())
        self.pitch = max(-math.pi / 2, min(math.pi / 2, self.pitch + (event.y - old_y) * math.radians(self.fov) / max(1, self.canvas.winfo_width())))
        self.drag_origin = (event.x, event.y)
        self.schedule_render()

    def on_wheel(self, event):
        self.zoom(-1 if event.delta > 0 else 1)

    def zoom(self, direction):
        self.fov = max(30, min(110, self.fov * (0.9 if direction < 0 else 1.1)))
        self.schedule_render()

    def schedule_render(self):
        if self.render_job is not None:
            self.after_cancel(self.render_job)
        self.render_job = self.after(35, self.render)

    def render(self):
        self.render_job = None
        width = min(max(self.canvas.winfo_width(), 1), 1100)
        height = min(max(self.canvas.winfo_height(), 1), 650)
        pixels = render_view(self.texture, width, height, self.yaw, self.pitch, self.fov)
        self.photo = ImageTk.PhotoImage(Image.fromarray(pixels))
        self.canvas.delete("all")
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, image=self.photo)

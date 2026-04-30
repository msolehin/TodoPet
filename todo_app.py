"""TodoPet — frameless always-on-top to-do list with a wandering pet companion."""
import json
import os
import random
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

APP_NAME = "TodoPet"
DATA_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
DATA_FILE = DATA_DIR / "data.json"

PETS = {
    "Cat":     {"emoji": "🐱", "phrases": ["Meow!", "Purr...", "You got this!", "Don't forget me!"]},
    "Dog":     {"emoji": "🐶", "phrases": ["Woof!", "Good job!", "*tail wag*", "Let's go!"]},
    "Bunny":   {"emoji": "🐰", "phrases": ["Hop hop!", "Carrot break?", "You're hopping along!"]},
    "Fox":     {"emoji": "🦊", "phrases": ["Sly moves!", "*sniff sniff*", "Crafty work!"]},
    "Turtle":  {"emoji": "🐢", "phrases": ["Slow & steady!", "Almost there...", "Take your time."]},
    "Penguin": {"emoji": "🐧", "phrases": ["Brrr!", "Sliding through!", "Cool work!"]},
    "Panda":   {"emoji": "🐼", "phrases": ["Bamboo break!", "Chillin'", "You can do it!"]},
    "Hamster": {"emoji": "🐹", "phrases": ["Squeak!", "Wheel time?", "You're zipping!"]},
    "Frog":    {"emoji": "🐸", "phrases": ["Ribbit!", "*hop*", "Lily pad vibes."]},
    "Owl":     {"emoji": "🦉", "phrases": ["Hoot!", "Wise choice.", "Whoo's productive?"]},
    "Tung Tung Sahur": {"emoji": "🪵", "phrases": ["tung tung tung", "Sahur!", "*sleepy yawn*", "bonk."]},
    "Fish":    {"emoji": "🐟", "phrases": ["Blub blub!", "*swims by*", "Splash!", "🫧"]},
    "Chicken": {"emoji": "🐔", "phrases": ["Bok bok!", "Cluck!", "*pecks*", "Egg-cellent!"]},
    "Lizard":  {"emoji": "🦎", "phrases": ["*tongue flick*", "Hssss", "Just chillin'", "Bug snack?"]},
}

THEMES = {
    "Default": {
        "BG": "#1a1a1a", "PANEL": "#242424", "PANEL2": "#2e2e2e", "HOVER": "#3a3a3a",
        "BORDER": "#2a2a2a", "FG": "#ececec", "MUTED": "#808080", "ACCENT": "#d4d4d4",
        "GREEN": "#4ade80", "RED": "#ef4444"
    },
    "Light Mode": {
        "BG": "#f9fafb", "PANEL": "#ffffff", "PANEL2": "#f3f4f6", "HOVER": "#e5e7eb",
        "BORDER": "#d1d5db", "FG": "#111827", "MUTED": "#6b7280", "ACCENT": "#3b82f6",
        "GREEN": "#22c55e", "RED": "#ef4444"
    },
    "Ghibli Mode": {
        "BG": "#2c3e2e", "PANEL": "#3a4f3c", "PANEL2": "#476049", "HOVER": "#547157",
        "BORDER": "#3a4f3c", "FG": "#e8ecd7", "MUTED": "#a3b19b", "ACCENT": "#facc15",
        "GREEN": "#4ade80", "RED": "#ef4444"
    },
    "Pinky Mode": {
        "BG": "#fdf2f8", "PANEL": "#fce7f3", "PANEL2": "#fbcfe8", "HOVER": "#f9a8d4",
        "BORDER": "#f9a8d4", "FG": "#831843", "MUTED": "#db2777", "ACCENT": "#be185d",
        "GREEN": "#10b981", "RED": "#e11d48"
    }
}

BG = PANEL = PANEL2 = HOVER = BORDER = FG = MUTED = ACCENT = GREEN = RED = ""

def set_theme(name):
    global BG, PANEL, PANEL2, HOVER, BORDER, FG, MUTED, ACCENT, GREEN, RED
    t = THEMES.get(name, THEMES["Default"])
    BG, PANEL, PANEL2, HOVER = t["BG"], t["PANEL"], t["PANEL2"], t["HOVER"]
    BORDER, FG, MUTED, ACCENT = t["BORDER"], t["FG"], t["MUTED"], t["ACCENT"]
    GREEN, RED = t["GREEN"], t["RED"]

set_theme("Default")


def load_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                d = json.load(f)
            d.setdefault("active", [])
            d.setdefault("history", [])
            d.setdefault("pet", "Cat")
            d.setdefault("theme", "Default")
            d.setdefault("opacity", 1.0)
            d.setdefault("next_id", 1)
            return d
        except Exception:
            pass
    return {"active": [], "history": [], "pet": "Cat", "theme": "Default", "opacity": 1.0, "next_id": 1}


def save_data(d):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    tmp.replace(DATA_FILE)


def get_virtual_screen(root):
    """Return (vx, vy, vw, vh) covering ALL monitors. Falls back to primary."""
    if sys.platform == "win32":
        try:
            from ctypes import windll
            gsm = windll.user32.GetSystemMetrics
            return (gsm(76), gsm(77), gsm(78), gsm(79))  # SM_*VIRTUALSCREEN
        except Exception:
            pass
    return (0, 0, root.winfo_screenwidth(), root.winfo_screenheight())


# ---------------- Pet drawing (vector 3D-look chibi pets) ----------------

def _sphere(c, cx, cy, r, fill, hi=None, outline=None, ow=2):
    c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill,
                  outline=(outline or fill), width=ow)
    if hi:
        hr = r * 0.42
        hx = cx - r * 0.32
        hy = cy - r * 0.42
        c.create_oval(hx - hr / 2, hy - hr / 2, hx + hr / 2, hy + hr / 2,
                      fill=hi, outline="")


def _eyes(c, lx, rx, y, r):
    for ex in (lx, rx):
        c.create_oval(ex - r, y - r, ex + r, y + r, fill="black", outline="")
        c.create_oval(ex - r * 0.4, y - r * 0.6, ex - r * 0.05, y - r * 0.25,
                      fill="white", outline="")


def draw_cat(c, s):
    cx, cy = s / 2, s * 0.56
    R = s * 0.30
    for sign in (-1, 1):
        c.create_polygon(cx + sign * R * 0.65, cy - R * 0.55,
                         cx + sign * R * 1.05, cy - R * 1.45,
                         cx + sign * R * 0.18, cy - R * 0.85,
                         fill="#fbbf24", outline="#7c2d12", width=2)
        c.create_polygon(cx + sign * R * 0.6, cy - R * 0.6,
                         cx + sign * R * 0.82, cy - R * 1.18,
                         cx + sign * R * 0.32, cy - R * 0.85,
                         fill="#fb7185", outline="")
    _sphere(c, cx, cy, R, "#fbbf24", hi="#fef3c7", outline="#7c2d12")
    _eyes(c, cx - R * 0.32, cx + R * 0.32, cy - R * 0.05, R * 0.13)
    c.create_polygon(cx - R * 0.1, cy + R * 0.18, cx + R * 0.1, cy + R * 0.18,
                     cx, cy + R * 0.32,
                     fill="#ec4899", outline="#9f1239", width=1)
    c.create_line(cx, cy + R * 0.32, cx, cy + R * 0.42, fill="#7c2d12", width=1)
    c.create_arc(cx - R * 0.22, cy + R * 0.3, cx, cy + R * 0.55,
                 start=0, extent=-180, style="arc", outline="#7c2d12", width=1)
    c.create_arc(cx, cy + R * 0.3, cx + R * 0.22, cy + R * 0.55,
                 start=180, extent=180, style="arc", outline="#7c2d12", width=1)
    for sign in (-1, 1):
        for dy in (-3, 0, 3):
            c.create_line(cx + sign * R * 0.25, cy + R * 0.3 + dy,
                          cx + sign * R * 0.85, cy + R * 0.25 + dy * 1.5,
                          fill="#7c2d12", width=1)


def draw_dog(c, s):
    cx, cy = s / 2, s * 0.55
    R = s * 0.30
    for sign in (-1, 1):
        ex = cx + sign * R * 0.85
        c.create_oval(ex - R * 0.30, cy - R * 0.30, ex + R * 0.30, cy + R * 0.65,
                      fill="#92400e", outline="#451a03", width=2)
    _sphere(c, cx, cy, R, "#d97706", hi="#fde68a", outline="#451a03")
    c.create_oval(cx - R * 0.45, cy + R * 0.05, cx + R * 0.45, cy + R * 0.55,
                  fill="#fef3c7", outline="#92400e", width=1)
    c.create_oval(cx - R * 0.16, cy + R * 0.05, cx + R * 0.16, cy + R * 0.28,
                  fill="black", outline="")
    c.create_polygon(cx - R * 0.18, cy + R * 0.4, cx + R * 0.18, cy + R * 0.4,
                     cx + R * 0.1, cy + R * 0.6, cx - R * 0.1, cy + R * 0.6,
                     fill="#f43f5e", outline="#9f1239", width=1)
    _eyes(c, cx - R * 0.30, cx + R * 0.30, cy - R * 0.18, R * 0.11)


def draw_bunny(c, s):
    cx, cy = s / 2, s * 0.62
    R = s * 0.26
    for sign in (-1, 1):
        ex = cx + sign * R * 0.45
        c.create_oval(ex - R * 0.20, cy - R * 1.85, ex + R * 0.20, cy - R * 0.45,
                      fill="#fef2f2", outline="#9ca3af", width=2)
        c.create_oval(ex - R * 0.10, cy - R * 1.70, ex + R * 0.10, cy - R * 0.60,
                      fill="#fb7185", outline="")
    _sphere(c, cx, cy, R, "#fef2f2", hi="#ffffff", outline="#9ca3af")
    _eyes(c, cx - R * 0.32, cx + R * 0.32, cy - R * 0.05, R * 0.13)
    c.create_polygon(cx - R * 0.10, cy + R * 0.18, cx + R * 0.10, cy + R * 0.18,
                     cx, cy + R * 0.32,
                     fill="#fb7185", outline="#9f1239", width=1)
    for sign in (-1, 1):
        c.create_line(cx + sign * R * 0.12, cy + R * 0.32,
                      cx + sign * R * 0.65, cy + R * 0.28,
                      fill="#9ca3af", width=1)


def draw_fox(c, s):
    cx, cy = s / 2, s * 0.58
    R = s * 0.30
    for sign in (-1, 1):
        c.create_polygon(cx + sign * R * 0.7, cy - R * 0.5,
                         cx + sign * R * 1.0, cy - R * 1.4,
                         cx + sign * R * 0.3, cy - R * 0.85,
                         fill="#ea580c", outline="#7c2d12", width=2)
        c.create_polygon(cx + sign * R * 0.78, cy - R * 0.85,
                         cx + sign * R * 0.92, cy - R * 1.25,
                         cx + sign * R * 0.55, cy - R * 1.0,
                         fill="#fef2f2", outline="")
    _sphere(c, cx, cy, R, "#ea580c", hi="#fdba74", outline="#7c2d12")
    c.create_polygon(cx - R * 0.42, cy + R * 0.05,
                     cx + R * 0.42, cy + R * 0.05,
                     cx + R * 0.16, cy + R * 0.55,
                     cx - R * 0.16, cy + R * 0.55,
                     fill="#fef2f2", outline="#7c2d12", width=1)
    c.create_oval(cx - R * 0.10, cy + R * 0.15, cx + R * 0.10, cy + R * 0.32,
                  fill="black", outline="")
    _eyes(c, cx - R * 0.32, cx + R * 0.32, cy - R * 0.15, R * 0.11)


def draw_turtle(c, s):
    cx, cy = s / 2, s * 0.55
    R = s * 0.30
    c.create_oval(cx - R * 0.45, cy + R * 0.20, cx + R * 0.45, cy + R * 0.75,
                  fill="#86efac", outline="#14532d", width=2)
    _eyes(c, cx - R * 0.18, cx + R * 0.18, cy + R * 0.40, R * 0.07)
    _sphere(c, cx, cy, R, "#16a34a", hi="#bbf7d0", outline="#14532d")
    c.create_polygon(cx - R * 0.55, cy - R * 0.05, cx, cy - R * 0.55,
                     cx + R * 0.55, cy - R * 0.05,
                     cx + R * 0.32, cy + R * 0.45, cx - R * 0.32, cy + R * 0.45,
                     fill="", outline="#14532d", width=2)
    c.create_oval(cx - R * 0.18, cy - R * 0.18, cx + R * 0.18, cy + R * 0.18,
                  fill="#65a30d", outline="#14532d", width=1)


def draw_penguin(c, s):
    cx, cy = s / 2, s * 0.50
    R = s * 0.32
    _sphere(c, cx, cy, R, "#1e293b", hi="#475569", outline="#0f172a")
    c.create_oval(cx - R * 0.55, cy - R * 0.20, cx + R * 0.55, cy + R * 0.85,
                  fill="#f9fafb", outline="")
    _eyes(c, cx - R * 0.22, cx + R * 0.22, cy - R * 0.32, R * 0.10)
    c.create_polygon(cx - R * 0.12, cy - R * 0.05, cx + R * 0.12, cy - R * 0.05,
                     cx, cy + R * 0.18,
                     fill="#fbbf24", outline="#b45309", width=1)
    c.create_oval(cx - R * 0.50, cy + R * 0.85, cx - R * 0.12, cy + R * 1.05,
                  fill="#fbbf24", outline="#b45309", width=1)
    c.create_oval(cx + R * 0.12, cy + R * 0.85, cx + R * 0.50, cy + R * 1.05,
                  fill="#fbbf24", outline="#b45309", width=1)


def draw_panda(c, s):
    cx, cy = s / 2, s * 0.55
    R = s * 0.30
    for sign in (-1, 1):
        ex = cx + sign * R * 0.78
        c.create_oval(ex - R * 0.24, cy - R * 1.05, ex + R * 0.24, cy - R * 0.50,
                      fill="#1f2937", outline="black", width=1)
    _sphere(c, cx, cy, R, "#f9fafb", hi="#ffffff", outline="#9ca3af")
    for sign in (-1, 1):
        ex = cx + sign * R * 0.32
        c.create_oval(ex - R * 0.20, cy - R * 0.30, ex + R * 0.20, cy + R * 0.18,
                      fill="#1f2937", outline="black", width=1)
    _eyes(c, cx - R * 0.30, cx + R * 0.30, cy - R * 0.06, R * 0.09)
    c.create_oval(cx - R * 0.10, cy + R * 0.20, cx + R * 0.10, cy + R * 0.35,
                  fill="black", outline="")
    c.create_arc(cx - R * 0.20, cy + R * 0.30, cx + R * 0.20, cy + R * 0.55,
                 start=180, extent=180, style="arc", outline="black", width=1)


def draw_hamster(c, s):
    cx, cy = s / 2, s * 0.56
    R = s * 0.32
    for sign in (-1, 1):
        ex = cx + sign * R * 0.55
        c.create_oval(ex - R * 0.13, cy - R * 0.95, ex + R * 0.13, cy - R * 0.55,
                      fill="#92400e", outline="#451a03", width=1)
    _sphere(c, cx, cy, R, "#fbbf24", hi="#fef3c7", outline="#92400e")
    c.create_oval(cx - R * 1.0, cy + R * 0.05, cx - R * 0.32, cy + R * 0.6,
                  fill="#fde68a", outline="#92400e", width=1)
    c.create_oval(cx + R * 0.32, cy + R * 0.05, cx + R * 1.0, cy + R * 0.6,
                  fill="#fde68a", outline="#92400e", width=1)
    _eyes(c, cx - R * 0.25, cx + R * 0.25, cy - R * 0.10, R * 0.10)
    c.create_oval(cx - R * 0.07, cy + R * 0.18, cx + R * 0.07, cy + R * 0.30,
                  fill="#fb7185", outline="#9f1239", width=1)


def draw_frog(c, s):
    cx, cy = s / 2, s * 0.6
    R = s * 0.30
    _sphere(c, cx, cy, R, "#84cc16", hi="#d9f99d", outline="#365314")
    c.create_oval(cx - R * 0.6, cy + R * 0.15, cx + R * 0.6, cy + R * 0.85,
                  fill="#bef264", outline="")
    for sign in (-1, 1):
        ex = cx + sign * R * 0.45
        c.create_oval(ex - R * 0.32, cy - R * 1.10, ex + R * 0.32, cy - R * 0.45,
                      fill="#84cc16", outline="#365314", width=2)
        c.create_oval(ex - R * 0.24, cy - R * 1.00, ex + R * 0.24, cy - R * 0.55,
                      fill="white", outline="")
        c.create_oval(ex - R * 0.14, cy - R * 0.90, ex + R * 0.14, cy - R * 0.60,
                      fill="black", outline="")
        c.create_oval(ex - R * 0.02, cy - R * 0.85, ex + R * 0.08, cy - R * 0.72,
                      fill="white", outline="")
    c.create_arc(cx - R * 0.55, cy - R * 0.15, cx + R * 0.55, cy + R * 0.40,
                 start=180, extent=180, style="arc", outline="#365314", width=2)


def draw_owl(c, s):
    cx, cy = s / 2, s * 0.55
    R = s * 0.32
    for sign in (-1, 1):
        c.create_oval(cx + sign * R * 1.05 - R * 0.30, cy - R * 0.30,
                      cx + sign * R * 0.50, cy + R * 0.75,
                      fill="#78350f", outline="#451a03", width=2)
    _sphere(c, cx, cy, R, "#92400e", hi="#d97706", outline="#451a03")
    for sign in (-1, 1):
        c.create_polygon(cx + sign * R * 0.65, cy - R * 0.7,
                         cx + sign * R * 0.85, cy - R * 1.15,
                         cx + sign * R * 0.45, cy - R * 0.95,
                         fill="#92400e", outline="#451a03", width=1)
    for sign in (-1, 1):
        ex = cx + sign * R * 0.32
        c.create_oval(ex - R * 0.30, cy - R * 0.35, ex + R * 0.30, cy + R * 0.25,
                      fill="white", outline="#451a03", width=2)
        c.create_oval(ex - R * 0.18, cy - R * 0.25, ex + R * 0.18, cy + R * 0.15,
                      fill="black", outline="")
        c.create_oval(ex - R * 0.08, cy - R * 0.22, ex + R * 0.04, cy - R * 0.10,
                      fill="white", outline="")
    c.create_polygon(cx - R * 0.12, cy + R * 0.25,
                     cx + R * 0.12, cy + R * 0.25,
                     cx, cy + R * 0.55,
                     fill="#fbbf24", outline="#b45309", width=1)


def draw_tungtung(c, s):
    """Tung Tung Tung Sahur — sleepy wooden brainrot character."""
    cx, cy = s / 2, s * 0.50
    body_w = s * 0.27
    body_h = s * 0.42
    bx1, by1 = cx - body_w, cy - body_h
    bx2, by2 = cx + body_w, cy + body_h
    c.create_oval(bx1, by1, bx2, by2, fill="#a16207", outline="#451a03", width=2)
    for x_off in (-body_w * 0.55, -body_w * 0.05, body_w * 0.45):
        c.create_line(cx + x_off, by1 + body_h * 0.18,
                      cx + x_off + s * 0.012, cy,
                      cx + x_off, by2 - body_h * 0.18,
                      smooth=True, fill="#78350f", width=1)
    c.create_oval(bx1 + body_w * 0.18, by1 + body_h * 0.15,
                  bx1 + body_w * 0.65, cy - body_h * 0.10,
                  fill="#d97706", outline="")
    eye_y = cy - body_h * 0.28
    for sign in (-1, 1):
        ex = cx + sign * body_w * 0.40
        c.create_arc(ex - body_w * 0.22, eye_y - body_h * 0.07,
                     ex + body_w * 0.22, eye_y + body_h * 0.07,
                     start=200, extent=140, style="arc",
                     outline="black", width=2)
        c.create_line(ex - body_w * 0.20, eye_y + body_h * 0.04,
                      ex - body_w * 0.30, eye_y + body_h * 0.10,
                      fill="black", width=1)
    c.create_oval(cx - body_w * 0.12, cy + body_h * 0.10,
                  cx + body_w * 0.12, cy + body_h * 0.30,
                  fill="#451a03", outline="black", width=1)
    z_size = max(8, int(s * 0.11))
    c.create_text(cx + body_w * 1.05, by1 + body_h * 0.12,
                  text="z", fill="#9ca3af",
                  font=("Segoe UI", z_size, "bold italic"))
    c.create_text(cx + body_w * 1.40, by1 - body_h * 0.05,
                  text="Z", fill="#d1d5db",
                  font=("Segoe UI", int(z_size * 1.4), "bold italic"))


def draw_fish(c, s):
    cx, cy = s / 2 - s * 0.04, s * 0.55
    body_w, body_h = s * 0.32, s * 0.22
    # Tail fin
    tail_x = cx + body_w * 0.95
    c.create_polygon(tail_x, cy,
                     tail_x + s * 0.18, cy - s * 0.16,
                     tail_x + s * 0.20, cy + s * 0.16,
                     fill="#f97316", outline="#7c2d12", width=2)
    # Top fin
    c.create_polygon(cx - body_w * 0.3, cy - body_h * 0.85,
                     cx + body_w * 0.4, cy - body_h * 0.85,
                     cx + body_w * 0.05, cy - body_h * 1.55,
                     fill="#fb923c", outline="#7c2d12", width=2)
    # Body
    c.create_oval(cx - body_w, cy - body_h, cx + body_w, cy + body_h,
                  fill="#fb923c", outline="#7c2d12", width=2)
    # Belly highlight
    c.create_oval(cx - body_w * 0.85, cy - body_h * 0.10,
                  cx + body_w * 0.85, cy + body_h * 0.95,
                  fill="#fed7aa", outline="")
    # Vertical stripes
    c.create_line(cx - body_w * 0.25, cy - body_h * 0.85,
                  cx - body_w * 0.25, cy + body_h * 0.85,
                  fill="#7c2d12", width=2)
    c.create_line(cx + body_w * 0.25, cy - body_h * 0.7,
                  cx + body_w * 0.25, cy + body_h * 0.7,
                  fill="#7c2d12", width=2)
    # Side fin
    c.create_polygon(cx - body_w * 0.05, cy + body_h * 0.25,
                     cx + body_w * 0.25, cy + body_h * 0.30,
                     cx + body_w * 0.05, cy + body_h * 0.85,
                     fill="#f97316", outline="#7c2d12", width=1)
    # Eye
    eye_x = cx - body_w * 0.55
    c.create_oval(eye_x - s * 0.06, cy - s * 0.07,
                  eye_x + s * 0.06, cy + s * 0.05,
                  fill="white", outline="#7c2d12", width=1)
    c.create_oval(eye_x - s * 0.025, cy - s * 0.04,
                  eye_x + s * 0.025, cy + s * 0.01,
                  fill="black", outline="")
    # Mouth
    c.create_arc(cx - body_w * 1.05, cy + s * 0.02,
                 cx - body_w * 0.85, cy + s * 0.10,
                 start=0, extent=-180, style="arc",
                 outline="#7c2d12", width=1)
    # Bubble
    c.create_oval(cx - body_w * 1.30, cy - body_h * 0.9,
                  cx - body_w * 1.18, cy - body_h * 0.7,
                  outline="#7c2d12", width=1)


def draw_chicken(c, s):
    cx, cy = s / 2, s * 0.62
    body_w, body_h = s * 0.30, s * 0.26
    # Body
    c.create_oval(cx - body_w, cy - body_h, cx + body_w, cy + body_h,
                  fill="#fef9c3", outline="#a16207", width=2)
    # Body highlight
    c.create_oval(cx - body_w * 0.55, cy - body_h * 0.7,
                  cx + body_w * 0.10, cy + body_h * 0.10,
                  fill="#fef3c7", outline="")
    # Wing
    c.create_oval(cx - body_w * 0.20, cy - body_h * 0.10,
                  cx + body_w * 0.55, cy + body_h * 0.55,
                  fill="#fde68a", outline="#a16207", width=1)
    c.create_arc(cx - body_w * 0.10, cy + body_h * 0.05,
                 cx + body_w * 0.45, cy + body_h * 0.45,
                 start=180, extent=180, style="arc",
                 outline="#a16207", width=1)
    # Head
    head_y = cy - body_h * 0.95
    head_r = s * 0.15
    c.create_oval(cx - head_r, head_y - head_r,
                  cx + head_r, head_y + head_r,
                  fill="#fef9c3", outline="#a16207", width=2)
    # Comb (red wavy)
    for sign in (-1, 0, 1):
        cx_b = cx + sign * head_r * 0.42
        c.create_oval(cx_b - head_r * 0.18, head_y - head_r * 1.30,
                      cx_b + head_r * 0.18, head_y - head_r * 0.65,
                      fill="#dc2626", outline="#7f1d1d", width=1)
    # Beak (yellow)
    c.create_polygon(cx + head_r * 0.85, head_y - head_r * 0.05,
                     cx + head_r * 1.55, head_y - head_r * 0.10,
                     cx + head_r * 1.55, head_y + head_r * 0.20,
                     cx + head_r * 0.85, head_y + head_r * 0.20,
                     fill="#fbbf24", outline="#92400e", width=1)
    c.create_line(cx + head_r * 0.85, head_y + head_r * 0.05,
                  cx + head_r * 1.55, head_y + head_r * 0.05,
                  fill="#92400e", width=1)
    # Wattle (red dangly)
    c.create_oval(cx + head_r * 0.55, head_y + head_r * 0.20,
                  cx + head_r * 1.00, head_y + head_r * 0.80,
                  fill="#dc2626", outline="#7f1d1d", width=1)
    # Eye
    c.create_oval(cx + head_r * 0.05, head_y - head_r * 0.30,
                  cx + head_r * 0.40, head_y + head_r * 0.05,
                  fill="black", outline="")
    c.create_oval(cx + head_r * 0.13, head_y - head_r * 0.25,
                  cx + head_r * 0.25, head_y - head_r * 0.13,
                  fill="white", outline="")
    # Legs
    for off in (-body_w * 0.25, body_w * 0.05):
        c.create_line(cx + off, cy + body_h * 0.92,
                      cx + off - s * 0.02, cy + body_h * 1.45,
                      fill="#fbbf24", width=int(max(2, s * 0.022)))
        # toes
        for tx in (-s * 0.04, 0, s * 0.04):
            c.create_line(cx + off - s * 0.02, cy + body_h * 1.45,
                          cx + off - s * 0.02 + tx, cy + body_h * 1.55,
                          fill="#fbbf24", width=int(max(2, s * 0.018)))


def draw_lizard(c, s):
    """Cute green lizard with curled tail and big bulgy eye."""
    cx, cy = s / 2 + s * 0.05, s * 0.58
    body_w, body_h = s * 0.26, s * 0.16
    # Curly tail (smooth line going right and curling back)
    c.create_line(
        cx + body_w * 0.95, cy + body_h * 0.10,
        cx + s * 0.30,      cy + s * 0.05,
        cx + s * 0.40,      cy - s * 0.10,
        cx + s * 0.30,      cy - s * 0.22,
        cx + s * 0.18,      cy - s * 0.18,
        smooth=True, width=int(max(3, s * 0.07)),
        fill="#22c55e", capstyle="round"
    )
    # Tail outline (slightly thicker darker behind)
    # Body
    c.create_oval(cx - body_w, cy - body_h, cx + body_w, cy + body_h,
                  fill="#22c55e", outline="#14532d", width=2)
    # Belly highlight
    c.create_oval(cx - body_w * 0.85, cy - body_h * 0.4,
                  cx + body_w * 0.6, cy + body_h * 0.85,
                  fill="#86efac", outline="")
    # Spots
    for px, py in [(-0.45, -0.20), (-0.05, 0.25), (0.30, -0.10), (0.10, -0.45)]:
        c.create_oval(cx + px * body_w - s * 0.02, cy + py * body_h - s * 0.02,
                      cx + px * body_w + s * 0.02, cy + py * body_h + s * 0.02,
                      fill="#15803d", outline="")
    # Head
    head_x = cx - body_w * 1.15
    head_y = cy - body_h * 0.20
    head_w = s * 0.16
    head_h = s * 0.13
    c.create_oval(head_x - head_w, head_y - head_h,
                  head_x + head_w * 0.85, head_y + head_h,
                  fill="#22c55e", outline="#14532d", width=2)
    # Bulgy eye on top
    eye_w = s * 0.10
    eye_h = s * 0.10
    c.create_oval(head_x - eye_w * 0.30, head_y - head_h - eye_h * 0.40,
                  head_x + eye_w * 0.85, head_y - head_h * 0.10,
                  fill="#22c55e", outline="#14532d", width=2)
    c.create_oval(head_x - eye_w * 0.15, head_y - head_h - eye_h * 0.25,
                  head_x + eye_w * 0.65, head_y - head_h * 0.20,
                  fill="white", outline="")
    c.create_oval(head_x + eye_w * 0.05, head_y - head_h - eye_h * 0.10,
                  head_x + eye_w * 0.40, head_y - head_h * 0.30,
                  fill="black", outline="")
    c.create_oval(head_x + eye_w * 0.18, head_y - head_h - eye_h * 0.05,
                  head_x + eye_w * 0.27, head_y - head_h * 0.42,
                  fill="white", outline="")
    # Smile
    c.create_arc(head_x - head_w * 0.6, head_y + head_h * 0.05,
                 head_x + head_w * 0.5, head_y + head_h * 0.75,
                 start=180, extent=180, style="arc",
                 outline="#14532d", width=1)
    # Forked tongue (pink, sticking out)
    c.create_line(head_x - head_w * 0.5, head_y + head_h * 0.55,
                  head_x - head_w * 1.20, head_y + head_h * 0.45,
                  fill="#ec4899", width=int(max(2, s * 0.018)))
    c.create_line(head_x - head_w * 1.20, head_y + head_h * 0.45,
                  head_x - head_w * 1.40, head_y + head_h * 0.30,
                  fill="#ec4899", width=int(max(1, s * 0.012)))
    c.create_line(head_x - head_w * 1.20, head_y + head_h * 0.45,
                  head_x - head_w * 1.40, head_y + head_h * 0.65,
                  fill="#ec4899", width=int(max(1, s * 0.012)))
    # Front leg
    c.create_oval(cx - body_w * 0.7, cy + body_h * 0.5,
                  cx - body_w * 0.4, cy + body_h * 1.3,
                  fill="#22c55e", outline="#14532d", width=1)
    # Back leg
    c.create_oval(cx + body_w * 0.3, cy + body_h * 0.6,
                  cx + body_w * 0.65, cy + body_h * 1.4,
                  fill="#22c55e", outline="#14532d", width=1)


PET_DRAWERS = {
    "Cat": draw_cat,
    "Dog": draw_dog,
    "Bunny": draw_bunny,
    "Fox": draw_fox,
    "Turtle": draw_turtle,
    "Penguin": draw_penguin,
    "Panda": draw_panda,
    "Hamster": draw_hamster,
    "Frog": draw_frog,
    "Owl": draw_owl,
    "Tung Tung Sahur": draw_tungtung,
    "Fish": draw_fish,
    "Chicken": draw_chicken,
    "Lizard": draw_lizard,
}


class FloatingPet:
    """Frameless transparent always-on-top pet — colorful 3D vector pet drawn
    on a Canvas, drag anywhere across all monitors, mouse-wheel to resize."""
    TRANSP = "#fe00fe"  # uncommon magenta — used as Windows color-key alpha
    MIN_SIZE = 50
    MAX_SIZE = 240
    DEFAULT_SIZE = 110

    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.size = self.DEFAULT_SIZE

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self._transparent = False
        try:
            self.win.attributes("-transparentcolor", self.TRANSP)
            self.win.attributes("-alpha", 1.0)
            self._transparent = True
        except tk.TclError:
            pass

        canvas_bg = self.TRANSP if self._transparent else PANEL2
        self.win.configure(bg=canvas_bg)
        self.canvas = tk.Canvas(self.win, width=self.size, height=self.size,
                                bg=canvas_bg, highlightthickness=0, bd=0,
                                cursor="fleur")
        self.canvas.pack()

        # Initial position: visible on primary screen
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.x = float(sw // 2 - self.size // 2)
        self.y = float(max(80, sh // 4))
        self.win.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")
        self.win.update_idletasks()

        self.dx = 1.6
        self.dy = 0.0
        self._dragging = False
        self._is_speaking = False
        self._dragged = False
        self._press_x = self._press_y = 0
        self._drag_dx = self._drag_dy = 0
        self._speech_win = None
        self._speech_timer = None

        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())

        self._draw_pet()
        self._animate()
        self._chatter_loop()

    def update_theme(self):
        canvas_bg = self.TRANSP if self._transparent else PANEL2
        self.win.configure(bg=canvas_bg)
        self.canvas.configure(bg=canvas_bg)

    def set_pet(self, value):
        self._draw_pet()

    def _draw_pet(self):
        self.canvas.delete("all")
        self.canvas.configure(width=self.size, height=self.size)
        try:
            name = self.app.pet_var.get()
        except Exception:
            name = "Cat"
        drawer = PET_DRAWERS.get(name, draw_cat)
        drawer(self.canvas, self.size)

    def _on_wheel(self, e):
        step = 8 if e.delta > 0 else -8
        self.set_size(self.size + step)

    def set_size(self, new_size):
        new_size = int(max(self.MIN_SIZE, min(self.MAX_SIZE, new_size)))
        if new_size == self.size:
            return
        old = self.size
        self.size = new_size
        self.x += (old - new_size) / 2
        self.y += (old - new_size) / 2
        self.win.geometry(f"{self.size}x{self.size}+{int(self.x)}+{int(self.y)}")
        self._draw_pet()
        self._reposition_speech()

    def say(self, msg):
        self._clear_speech()
        self._is_speaking = True

        sw = tk.Toplevel(self.win)
        sw.overrideredirect(True)
        sw.attributes("-topmost", True)
        try:
            sw.attributes("-alpha", 0.96)
        except tk.TclError:
            pass
        sw.configure(bg=BORDER)
        bub_inner = tk.Frame(sw, bg=PANEL2)
        bub_inner.pack(padx=1, pady=1)
        tk.Label(bub_inner, text=msg, bg=PANEL2, fg=FG,
                 font=("Segoe UI", 9), padx=10, pady=5).pack()

        sw.update_idletasks()
        self._speech_win = sw
        self._reposition_speech()

        self._speech_timer = self.win.after(2400, self._clear_speech)

    def _reposition_speech(self):
        if not self._speech_win:
            return
        try:
            bw = self._speech_win.winfo_width()
            bh = self._speech_win.winfo_height()
        except tk.TclError:
            return
        vx, vy, vw, vh = get_virtual_screen(self.root)
        bx = int(self.x + self.size / 2 - bw / 2)
        by = int(self.y - bh - 6)
        if by < vy:
            by = int(self.y + self.size + 6)
        bx = max(vx, min(bx, vx + vw - bw))
        try:
            self._speech_win.geometry(f"+{bx}+{by}")
        except tk.TclError:
            pass

    def _clear_speech(self):
        self._is_speaking = False
        if self._speech_timer:
            try:
                self.win.after_cancel(self._speech_timer)
            except Exception:
                pass
            self._speech_timer = None
        if self._speech_win:
            try:
                self._speech_win.destroy()
            except Exception:
                pass
            self._speech_win = None

    def _on_press(self, e):
        self._press_x = e.x_root
        self._press_y = e.y_root
        self._drag_dx = e.x_root - self.win.winfo_x()
        self._drag_dy = e.y_root - self.win.winfo_y()
        self._dragged = False
        self._dragging = True

    def _on_drag_motion(self, e):
        if abs(e.x_root - self._press_x) > 3 or abs(e.y_root - self._press_y) > 3:
            self._dragged = True
        if self._dragging:
            new_x = e.x_root - self._drag_dx
            new_y = e.y_root - self._drag_dy
            self.x = float(new_x)
            self.y = float(new_y)
            self.win.geometry(f"+{new_x}+{new_y}")
            self._reposition_speech()

    def _on_release(self, _e):
        self._dragging = False
        if not self._dragged:
            self._chatter()

    def _chatter(self):
        try:
            phrases = PETS[self.app.pet_var.get()]["phrases"]
        except Exception:
            phrases = ["Hi!"]
        self.say(random.choice(phrases))

    def _chatter_loop(self):
        if random.random() < 0.4 and not self._dragging and not self._is_speaking:
            self._chatter()
        self.win.after(random.randint(22000, 45000), self._chatter_loop)

    def _animate(self):
        if not self._dragging and not self._is_speaking:
            vx, vy, vw, vh = get_virtual_screen(self.root)
            self.x += self.dx
            self.y += self.dy
            if random.random() < 0.04:
                self.dy = random.choice([-1.0, -0.5, 0.0, 0.5, 1.0])
            if random.random() < 0.01:
                self.dx = random.choice([-2.0, -1.5, 1.5, 2.0])
            if self.x < vx:
                self.x = vx
                self.dx = abs(self.dx)
            elif self.x > vx + vw - self.size:
                self.x = vx + vw - self.size
                self.dx = -abs(self.dx)
            if self.y < vy:
                self.y = vy
                self.dy = abs(self.dy)
            elif self.y > vy + vh - self.size - 50:
                self.y = vy + vh - self.size - 50
                self.dy = -abs(self.dy)
            self.win.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.win.after(50, self._animate)


def force_taskbar_presence(root):
    """With overrideredirect the window normally vanishes from the taskbar AND
    can't be minimized. Apply WS_EX_APPWINDOW for taskbar, plus WS_MINIMIZEBOX |
    WS_SYSMENU on the base style so Windows actually permits minimize."""
    if sys.platform != "win32":
        return
    try:
        from ctypes import windll
        GWL_EXSTYLE = -20
        GWL_STYLE = -16
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        WS_MINIMIZEBOX = 0x00020000
        WS_SYSMENU = 0x00080000
        hwnd = windll.user32.GetParent(root.winfo_id())

        ex_style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex_style = (ex_style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)

        style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style |= WS_MINIMIZEBOX | WS_SYSMENU
        windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)

        # Re-show for the change to take effect
        root.withdraw()
        root.after(10, root.deiconify)
    except Exception:
        pass


_single_instance_handle = None  # holds the mutex so it isn't GC'd


def acquire_single_instance_or_focus():
    """Return True if this is the first instance. If another instance already
    runs, try to bring its window to the foreground (which on Win10/11 also
    switches to its virtual desktop) and return False."""
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        from ctypes import wintypes
        ERROR_ALREADY_EXISTS = 183
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        handle = kernel32.CreateMutexW(None, True, "Local\\TodoPet_SingleInstance_v1")
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            try:
                user32 = ctypes.windll.user32
                hwnd = user32.FindWindowW(None, "TodoPet")
                if hwnd:
                    SW_RESTORE = 9
                    user32.ShowWindow(hwnd, SW_RESTORE)
                    user32.SetForegroundWindow(hwnd)
            except Exception:
                pass
            return False
        global _single_instance_handle
        _single_instance_handle = handle
        return True
    except Exception:
        return True


class HoverButton(tk.Label):
    """A flat label-button that lights up on hover."""
    def __init__(self, parent, text, command, *,
                 bg=PANEL2, fg=FG, hover_bg=HOVER, hover_fg=FG,
                 font=("Segoe UI", 10), pad=(12, 6), cursor="hand2"):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         padx=pad[0], pady=pad[1], cursor=cursor)
        self._bg, self._fg = bg, fg
        self._hbg, self._hfg = hover_bg, hover_fg
        self._command = command
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, _e):
        self.configure(bg=self._hbg, fg=self._hfg)

    def _on_leave(self, _e):
        self.configure(bg=self._bg, fg=self._fg)

    def _on_click(self, _e):
        if self._command:
            self._command()


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.data = load_data()
        set_theme(self.data.get("theme", "Default"))

        # Frameless window — small, top-right by default
        root.title("TodoPet")  # used by single-instance FindWindowW
        root.overrideredirect(True)
        root.configure(bg=BG)
        root.attributes("-topmost", True)
        try:
            root.attributes("-alpha", self.data.get("opacity", 1.0))
        except tk.TclError:
            pass

        default_w, default_h = 300, 400
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = max(0, screen_w - default_w - 30)
        y = max(0, (screen_h - default_h) // 4)
        root.geometry(f"{default_w}x{default_h}+{x}+{y}")

        self._minsize = (240, 300)
        self._drag_x = 0
        self._drag_y = 0
        self._rs = None
        self._task_labels = []

        # ttk theming for OptionMenu / Scrollbar
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=BG, foreground=FG, fieldbackground=PANEL, borderwidth=0)
        style.configure("TMenubutton", background=PANEL2, foreground=FG, padding=4,
                        relief="flat", borderwidth=0, arrowcolor=FG)
        style.map("TMenubutton",
                  background=[("active", HOVER)],
                  foreground=[("active", FG)])
        style.configure("Vertical.TScrollbar",
                        background=PANEL2, troughcolor=BG,
                        bordercolor=BG, arrowcolor=MUTED,
                        gripcount=0, relief="flat")
        style.map("Vertical.TScrollbar", background=[("active", HOVER)])
        style.configure("Horizontal.TScale", background=BG, troughcolor=PANEL2,
                        bordercolor=BG, lightcolor=ACCENT, darkcolor=ACCENT)

        # Pet state needs to exist before FloatingPet is created and before any view renders
        self.pet_var = tk.StringVar(value=self.data.get("pet", "Cat"))
        if self.pet_var.get() not in PETS:
            self.pet_var.set("Cat")
        self.view = "tasks"
        self.tab_buttons = {}
        self.list_canvas = None
        self.list_inner = None
        self.list_window = None
        self.entry = None

        # Build chrome
        self._build_titlebar()
        self._build_body()
        self._build_resize_grip()

        self._sweep_completed()

        # Floating screen-roaming pet (separate transparent toplevel)
        self.pet = None
        try:
            self.pet = FloatingPet(root, self)
        except Exception:
            self.pet = None

        # Run after the window has an HWND
        root.after(50, lambda: force_taskbar_presence(root))
        # Re-assert topmost when window is mapped (e.g., after restoring from minimized)
        root.bind("<Map>", self._on_map)

    def _apply_theme(self):
        set_theme(self.data.get("theme", "Default"))

        style = ttk.Style()
        style.configure(".", background=BG, foreground=FG, fieldbackground=PANEL, borderwidth=0)
        style.configure("TMenubutton", background=PANEL2, foreground=FG, padding=4, relief="flat", borderwidth=0, arrowcolor=FG)
        style.map("TMenubutton", background=[("active", HOVER)], foreground=[("active", FG)])
        style.configure("Vertical.TScrollbar", background=PANEL2, troughcolor=BG, bordercolor=BG, arrowcolor=MUTED, gripcount=0, relief="flat")
        style.map("Vertical.TScrollbar", background=[("active", HOVER)])
        style.configure("Horizontal.TScale", background=BG, troughcolor=PANEL2, bordercolor=BG, lightcolor=ACCENT, darkcolor=ACCENT)

        self.root.configure(bg=BG)

        for w in self.root.winfo_children():
            if isinstance(w, tk.Toplevel):
                continue
            w.destroy()

        self.tab_buttons = {}
        self.list_canvas = self.list_inner = self.list_window = self.entry = None

        self._build_titlebar()
        self._build_body()
        self._build_resize_grip()
        self._on_map(None)

        if self.pet:
            self.pet.update_theme()

    # ---------------- titlebar ----------------

    def _build_titlebar(self):
        self.titlebar = tk.Frame(self.root, bg=BG, height=30)
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)

        title = tk.Label(self.titlebar, text="✨  TodoPet",
                         bg=BG, fg=FG, font=("Segoe UI", 10, "bold"),
                         padx=10)
        title.pack(side="left", fill="y")

        # Window controls (right-aligned, in reverse order)
        close = HoverButton(self.titlebar, "✕", self._close,
                            bg=BG, fg=FG, hover_bg=RED, hover_fg="#ffffff",
                            font=("Segoe UI", 10), pad=(11, 6))
        close.pack(side="right", fill="y")

        mini = HoverButton(self.titlebar, "—", self._minimize,
                           bg=BG, fg=FG, hover_bg=HOVER, hover_fg=FG,
                           font=("Segoe UI", 10), pad=(11, 6))
        mini.pack(side="right", fill="y")

        # Drag-to-move on the titlebar background and the title label
        for w in (self.titlebar, title):
            w.bind("<Button-1>", self._start_drag)
            w.bind("<B1-Motion>", self._on_drag)

        # Subtle border under the titlebar
        sep = tk.Frame(self.root, bg=BORDER, height=1)
        sep.pack(fill="x", side="top")

    def _start_drag(self, e):
        self._drag_x = e.x_root - self.root.winfo_x()
        self._drag_y = e.y_root - self.root.winfo_y()

    def _on_drag(self, e):
        x = e.x_root - self._drag_x
        y = e.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _minimize(self):
        if sys.platform == "win32":
            try:
                from ctypes import windll
                hwnd = windll.user32.GetParent(self.root.winfo_id())
                SW_MINIMIZE = 6
                windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
                return
            except Exception:
                pass
        self.root.iconify()

    def _on_map(self, _e):
        # Re-assert topmost when window is restored from minimized
        try:
            self.root.attributes("-topmost", True)
        except tk.TclError:
            pass

    def _close(self):
        try:
            save_data(self.data)
        finally:
            self.root.destroy()

    # ---------------- body ----------------

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # Tabs at top
        self._build_tabs(body)

        # Content area — re-rendered when switching tabs
        self.content = tk.Frame(body, bg=BG)
        self.content.pack(fill="both", expand=True)

        self._switch_view(self.view)

    def _build_tabs(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", padx=8, pady=(6, 0))

        tabs = [("tasks", "📋 Tasks"), ("history", "📜 History"), ("settings", "⚙ Settings")]
        for key, label in tabs:
            col = tk.Frame(bar, bg=BG)
            col.pack(side="left", padx=2)
            lbl = tk.Label(col, text=label, bg=BG, fg=MUTED,
                           font=("Segoe UI", 9), cursor="hand2",
                           padx=10, pady=4)
            lbl.pack()
            ind = tk.Frame(col, bg=BG, height=2)
            ind.pack(fill="x")
            lbl.bind("<Button-1>", lambda e, k=key: self._switch_view(k))
            lbl.bind("<Enter>", lambda e, l=lbl, k=key: l.configure(
                fg=FG if k != self.view else FG))
            lbl.bind("<Leave>", lambda e, l=lbl, k=key: l.configure(
                fg=FG if k == self.view else MUTED))
            self.tab_buttons[key] = (lbl, ind)

        sep = tk.Frame(parent, bg=BORDER, height=1)
        sep.pack(fill="x", padx=10)

    def _switch_view(self, view):
        self.view = view
        for key, (lbl, ind) in self.tab_buttons.items():
            if key == view:
                lbl.configure(fg=FG)
                ind.configure(bg=ACCENT)
            else:
                lbl.configure(fg=MUTED)
                ind.configure(bg=BG)
        self._render_view()

    def _render_view(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.list_canvas = self.list_inner = self.list_window = None
        self.entry = None
        if self.view == "history":
            self._render_history_view()
        elif self.view == "settings":
            self._render_settings_view()
        else:
            self._render_tasks_view()

    def _render_tasks_view(self):
        # Add input row
        add_row = tk.Frame(self.content, bg=BG)
        add_row.pack(fill="x", padx=10, pady=(8, 4))

        entry_wrap = tk.Frame(add_row, bg=PANEL2)
        entry_wrap.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry = tk.Entry(entry_wrap, font=("Segoe UI", 10),
                              bg=PANEL2, fg=FG, insertbackground=FG,
                              relief="flat", borderwidth=0, highlightthickness=0)
        self.entry.pack(fill="x", expand=True, ipady=6, padx=8)
        self.entry.bind("<Return>", lambda e: self.add_todo())

        HoverButton(add_row, "+", self.add_todo,
                    bg=PANEL2, fg=FG, hover_bg=HOVER,
                    font=("Segoe UI", 11, "bold"), pad=(12, 5)).pack(side="right")

        # Scrollable task list
        list_wrap = tk.Frame(self.content, bg=BG)
        list_wrap.pack(fill="both", expand=True, padx=10, pady=4)

        self.list_canvas = tk.Canvas(list_wrap, bg=BG, highlightthickness=0)
        self.list_canvas.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(list_wrap, orient="vertical", command=self.list_canvas.yview)
        sb.pack(side="right", fill="y")
        self.list_canvas.configure(yscrollcommand=sb.set)

        self.list_inner = tk.Frame(self.list_canvas, bg=BG)
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_inner, anchor="nw")
        self.list_inner.bind("<Configure>",
                             lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind("<Configure>", self._on_list_configure)
        self.list_canvas.bind("<Enter>", lambda e: self.list_canvas.bind_all("<MouseWheel>", self._on_wheel))
        self.list_canvas.bind("<Leave>", lambda e: self.list_canvas.unbind_all("<MouseWheel>"))

        self._refresh_list()

    def _render_history_view(self):
        hdr = tk.Frame(self.content, bg=BG)
        hdr.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(hdr, text="Completed", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        HoverButton(hdr, "Clear All", self._clear_history_inplace,
                    bg=BG, fg=MUTED, hover_bg=HOVER, hover_fg=RED,
                    font=("Segoe UI", 8), pad=(8, 4)).pack(side="right")

        text_wrap = tk.Frame(self.content, bg=BG)
        text_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        text = tk.Text(text_wrap, bg=PANEL, fg=FG, font=("Segoe UI", 10), wrap="word",
                       relief="flat", padx=10, pady=10, borderwidth=0,
                       highlightthickness=0, insertbackground=FG)
        text.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(text_wrap, orient="vertical", command=text.yview)
        sb.pack(side="right", fill="y")
        text.configure(yscrollcommand=sb.set)

        if not self.data["history"]:
            text.insert("end", "No completed tasks yet ✨")
        else:
            for entry in reversed(self.data["history"]):
                ts = entry.get("completed", "")
                try:
                    ts = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    pass
                text.insert("end", f"✓  {entry['text']}\n", "done")
                text.insert("end", f"    {ts}\n\n", "ts")
        text.tag_configure("done", foreground=GREEN, font=("Segoe UI", 10))
        text.tag_configure("ts", foreground=MUTED, font=("Segoe UI", 9))
        text.configure(state="disabled")

    def _render_settings_view(self):
        wrap = tk.Frame(self.content, bg=BG)
        wrap.pack(fill="both", expand=True, padx=14, pady=10)

        # Theme picker
        tk.Label(wrap, text="THEME", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.data.get("theme", "Default"))
        theme_menu = ttk.OptionMenu(wrap, self.theme_var, self.theme_var.get(),
                                    *THEMES.keys(), command=self._on_theme_change)
        theme_menu.configure(style="TMenubutton")
        theme_menu.pack(anchor="w", fill="x", pady=(4, 14))

        # Opacity slider
        opacity_header = tk.Frame(wrap, bg=BG)
        opacity_header.pack(fill="x")
        tk.Label(opacity_header, text="OPACITY", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        current_opacity = self.data.get("opacity", 1.0)
        opacity_lbl = tk.Label(opacity_header, text=f"{int(current_opacity * 100)}%",
                               bg=BG, fg=FG, font=("Segoe UI", 9))
        opacity_lbl.pack(side="right")

        self.opacity_var = tk.DoubleVar(value=current_opacity)
        opacity_slider = ttk.Scale(wrap, from_=0.1, to=1.0,
                                   orient="horizontal", variable=self.opacity_var,
                                   command=lambda v, l=opacity_lbl: self._on_opacity_change(v, l))
        opacity_slider.pack(fill="x", pady=(4, 14))

        # Pet picker
        tk.Label(wrap, text="PET", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        pet_menu = ttk.OptionMenu(wrap, self.pet_var, self.pet_var.get(),
                                  *PETS.keys(), command=self._on_pet_change)
        pet_menu.configure(style="TMenubutton")
        pet_menu.pack(anchor="w", fill="x", pady=(4, 14))

        # Pet size slider
        size_header = tk.Frame(wrap, bg=BG)
        size_header.pack(fill="x")
        tk.Label(size_header, text="PET SIZE", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left")
        current_size = self.pet.size if self.pet else FloatingPet.DEFAULT_SIZE
        size_lbl = tk.Label(size_header, text=f"{int(current_size)} px",
                            bg=BG, fg=FG, font=("Segoe UI", 9))
        size_lbl.pack(side="right")

        self.size_var = tk.IntVar(value=int(current_size))
        slider = ttk.Scale(wrap, from_=FloatingPet.MIN_SIZE, to=FloatingPet.MAX_SIZE,
                           orient="horizontal", variable=self.size_var,
                           command=lambda v, l=size_lbl: self._on_size_change(v, l))
        slider.pack(fill="x", pady=(4, 14))

        # Hint
        tk.Label(wrap,
                 text="Tip: scroll the mouse wheel over the pet to resize too.\n"
                      "Drag the pet anywhere — it roams across all monitors.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8, "italic"),
                 justify="left").pack(anchor="w", pady=(8, 0))

    def _on_size_change(self, value, label_widget):
        try:
            size = int(float(value))
        except (TypeError, ValueError):
            return
        if label_widget:
            try:
                label_widget.configure(text=f"{size} px")
            except tk.TclError:
                pass
        if self.pet:
            self.pet.set_size(size)

    def _on_opacity_change(self, value, label_widget):
        try:
            opacity = float(value)
        except (TypeError, ValueError):
            return
        if label_widget:
            try:
                label_widget.configure(text=f"{int(opacity * 100)}%")
            except tk.TclError:
                pass
        try:
            self.root.attributes("-alpha", opacity)
        except tk.TclError:
            pass
        self.data["opacity"] = opacity
        save_data(self.data)

    def _on_theme_change(self, value):
        self.data["theme"] = value
        save_data(self.data)
        self._apply_theme()

    def _clear_history_inplace(self):
        if messagebox.askyesno("Clear history?",
                               "Delete all completed task history? This can't be undone.",
                               parent=self.root):
            self.data["history"] = []
            save_data(self.data)
            self._render_view()
            self._pet_say("Fresh start!")

    def _on_list_configure(self, e):
        self.list_canvas.itemconfig(self.list_window, width=e.width)
        wrap = max(80, e.width - 80)
        for lbl in self._task_labels:
            try:
                lbl.configure(wraplength=wrap)
            except tk.TclError:
                pass

    def _build_resize_grip(self):
        grip = tk.Frame(self.root, bg=BG, cursor="bottom_right_corner",
                        width=16, height=16)
        grip.place(relx=1.0, rely=1.0, anchor="se")
        dot = tk.Label(grip, text="◢", bg=BG, fg=MUTED,
                       font=("Segoe UI", 9), cursor="bottom_right_corner")
        dot.pack(fill="both", expand=True)
        for w in (grip, dot):
            w.bind("<Button-1>", self._start_resize)
            w.bind("<B1-Motion>", self._on_resize)
            w.bind("<Enter>", lambda e, d=dot: d.configure(fg=FG))
            w.bind("<Leave>", lambda e, d=dot: d.configure(fg=MUTED))

    def _start_resize(self, e):
        self._rs = (e.x_root, e.y_root,
                    self.root.winfo_width(), self.root.winfo_height())

    def _on_resize(self, e):
        if not self._rs:
            return
        sx, sy, sw, sh = self._rs
        new_w = max(self._minsize[0], sw + (e.x_root - sx))
        new_h = max(self._minsize[1], sh + (e.y_root - sy))
        self.root.geometry(f"{new_w}x{new_h}")

    def _on_wheel(self, event):
        self.list_canvas.yview_scroll(int(-event.delta / 120), "units")

    # ---------------- list ----------------

    def _refresh_list(self):
        if not self.list_inner:
            return
        for w in self.list_inner.winfo_children():
            w.destroy()
        self._task_labels = []

        undone = [t for t in self.data["active"] if not t.get("completed")]
        done = [t for t in self.data["active"] if t.get("completed")]
        done.sort(key=lambda t: t.get("completed", ""), reverse=True)

        if not undone and not done:
            tk.Label(self.list_inner, text="No tasks yet ✨",
                     bg=BG, fg=MUTED, font=("Segoe UI", 9, "italic")).pack(pady=20)
            return

        for todo in undone:
            self._make_row(todo, done=False)

        if done:
            sep_wrap = tk.Frame(self.list_inner, bg=BG)
            sep_wrap.pack(fill="x", pady=(8, 4))
            tk.Frame(sep_wrap, bg=BORDER, height=1).pack(fill="x", padx=4)
            tk.Label(sep_wrap, text=f"DONE · disappears in 24h",
                     bg=BG, fg=MUTED, font=("Segoe UI", 7, "bold")).pack(anchor="w", padx=6, pady=(4, 0))
            for todo in done:
                self._make_row(todo, done=True)

    def _make_row(self, todo, done=False):
        row_bg = PANEL if not done else "#1d1d1d"
        row = tk.Frame(self.list_inner, bg=row_bg)
        row.pack(fill="x", pady=2)

        if done:
            box_text, box_color = "◉", GREEN
            label_color = MUTED
            label_font = ("Segoe UI", 10, "overstrike")
        else:
            box_text, box_color = "○", MUTED
            label_color = FG
            label_font = ("Segoe UI", 10)

        box = tk.Label(row, text=box_text, bg=row_bg, fg=box_color,
                       font=("Segoe UI", 12), cursor="hand2", padx=8)
        box.pack(side="left", pady=4)
        box.bind("<Button-1>", lambda e, tid=todo["id"]: self.complete_todo(tid))
        if done:
            box.bind("<Enter>", lambda e: box.configure(fg=MUTED, text="○"))
            box.bind("<Leave>", lambda e: box.configure(fg=GREEN, text="◉"))
        else:
            box.bind("<Enter>", lambda e: box.configure(fg=GREEN, text="◉"))
            box.bind("<Leave>", lambda e: box.configure(fg=MUTED, text="○"))

        wrap = max(80, self.list_canvas.winfo_width() - 80)
        lbl = tk.Label(row, text=todo["text"], bg=row_bg, fg=label_color,
                       font=label_font, anchor="w", justify="left",
                       wraplength=wrap)
        lbl.pack(side="left", fill="x", expand=True, padx=2, pady=6)
        self._task_labels.append(lbl)

        rm = tk.Label(row, text="✕", bg=row_bg, fg=MUTED, cursor="hand2",
                      font=("Segoe UI", 10), padx=10)
        rm.pack(side="right", pady=4)
        rm.bind("<Button-1>", lambda e, tid=todo["id"]: self.remove_todo(tid))
        rm.bind("<Enter>", lambda e: rm.configure(fg=RED))
        rm.bind("<Leave>", lambda e: rm.configure(fg=MUTED))

    # ---------------- actions ----------------

    def add_todo(self):
        if not self.entry:
            return
        text = self.entry.get().strip()
        if not text:
            return
        todo = {"id": self.data["next_id"], "text": text,
                "created": datetime.now().isoformat(timespec="seconds")}
        self.data["next_id"] += 1
        self.data["active"].append(todo)
        save_data(self.data)
        self.entry.delete(0, tk.END)
        self._refresh_list()
        self._pet_say("New task!")

    def complete_todo(self, tid):
        for t in self.data["active"]:
            if t["id"] == tid:
                if t.get("completed"):
                    t.pop("completed", None)
                    save_data(self.data)
                    self._refresh_list()
                    self._pet_say("Back to it!")
                else:
                    t["completed"] = datetime.now().isoformat(timespec="seconds")
                    save_data(self.data)
                    self._refresh_list()
                    self._pet_say(random.choice(["Nice!", "Great job!", "🎉", "Yay!", "Crushed it!"]))
                return

    def _sweep_completed(self):
        """Move tasks completed >24h ago into history. Runs on launch and every 30 min."""
        now = datetime.now()
        keep = []
        moved = 0
        for t in self.data["active"]:
            comp = t.get("completed")
            if comp:
                try:
                    done_at = datetime.fromisoformat(comp)
                    if (now - done_at).total_seconds() >= 24 * 60 * 60:
                        self.data["history"].append({
                            "text": t["text"],
                            "created": t.get("created"),
                            "completed": comp,
                        })
                        moved += 1
                        continue
                except (ValueError, TypeError):
                    pass
            keep.append(t)
        if moved:
            self.data["active"] = keep
            save_data(self.data)
            self._refresh_list()
        self.root.after(30 * 60 * 1000, self._sweep_completed)

    def remove_todo(self, tid):
        for i, t in enumerate(self.data["active"]):
            if t["id"] == tid:
                self.data["active"].pop(i)
                save_data(self.data)
                self._refresh_list()
                self._pet_say("Gone!")
                return

    # ---------------- pet ----------------

    def _on_pet_change(self, value):
        self.data["pet"] = value
        save_data(self.data)
        if self.pet:
            self.pet.set_pet(value)
            self.pet.say("Hi!")

    def _pet_say(self, msg):
        if self.pet:
            self.pet.say(msg)


def main():
    if not acquire_single_instance_or_focus():
        return
    root = tk.Tk()
    TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk

# Bảng màu Vàng Chanh Pastel (Soft Pastel Lemon Theme)
BG = "#FDFBF7"            # Nền nội dung chính: Kem nhạt
SIDEBAR = "#FEF9C3"       # Nền Sidebar: Vàng chanh Pastel mềm dịu
PANEL = "#FFFFFF"         # Nền các ô/bảng: Trắng tinh
TEXT = "#1C1917"          # Chữ chính: Nâu đen đậm (dễ đọc)
MUTED = "#713F12"         # Chữ phụ/thẻ: Nâu vàng đậm
BORDER = "#FEF08A"        # Đường viền: Vàng nhạt

ACCENT = "#EAB308"        # Vàng chanh điểm nhấn
ACCENT_PASTEL = "#FEF08A" # Vàng chanh nhạt nổi bật
ACCENT_HOVER = "#CA8A04"  # Vàng chanh khi di chuột

SUCCESS = "#10B981"
WARNING = "#F59E0B"
DANGER = "#EF4444"


def configure_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 9))
    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=PANEL)

    style.configure(
        "Primary.TButton",
        background=ACCENT,
        foreground="#FFFFFF",
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_HOVER)],
        foreground=[("active", "#FFFFFF")],
    )

    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background="#F5F5F4",
        foreground=TEXT,
        padding=[14, 6],
        font=("Segoe UI", 9, "bold"),
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT_PASTEL)],
        foreground=[("selected", "#854D0E")],
    )

    style.configure(
        "Treeview",
        background=PANEL,
        foreground=TEXT,
        fieldbackground=PANEL,
        rowheight=30,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background="#FEF08A",
        foreground="#713F12",
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", ACCENT_PASTEL)],
        foreground=[("selected", "#713F12")],
    )


def setup_theme(root):
    configure_style(root)
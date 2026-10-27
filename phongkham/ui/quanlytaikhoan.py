# Thông tin tài khoản đang đăng nhập
import tkinter as tk

from services.auth import AuthService, role_label
from ui.theme import BORDER, MUTED, PANEL, TEXT
from ui.widgets import PastelButton


def info_rows(username, info):
    """Danh sách (nhãn, giá trị) của một tài khoản; bỏ qua mục trống."""
    rows = [
        ("Tên đăng nhập", username),
        ("Họ và tên", info.get("ho_ten", "")),
        ("Quyền", role_label(info)),
        ("Mã bác sĩ", info.get("ma_bs", "")),
        ("Chuyên khoa", info.get("chuyen_khoa", "")),
        ("Giới tính", info.get("gioi_tinh", "")),
        ("Số điện thoại", info.get("sdt", "")),
        ("Email", info.get("email", "")),
        ("Ngày tạo", info.get("ngay_tao", "")),
    ]
    return [(k, v) for k, v in rows if v]


def info_text(username, info):
    return "\n".join(f"{k}: {v}" for k, v in info_rows(username, info))


def show_account_info(parent, username):
    """Hộp thoại xem thông tin tài khoản đang đăng nhập."""
    info = AuthService().get_user(username) or {}
    win = tk.Toplevel(parent)
    win.title("Thông tin tài khoản")
    win.configure(bg=PANEL)
    win.resizable(False, False)
    win.transient(parent.winfo_toplevel())
    win.grab_set()

    tk.Label(win, text="👤 THÔNG TIN TÀI KHOẢN", bg=PANEL, fg=TEXT,
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=22, pady=(18, 8))
    box = tk.Frame(win, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
    box.pack(fill="x", padx=22)
    for i, (k, v) in enumerate(info_rows(username, info)):
        tk.Label(box, text=k, bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold"),
                 width=14, anchor="w").grid(row=i, column=0, sticky="w", padx=(12, 4), pady=4)
        tk.Label(box, text=v, bg=PANEL, fg=TEXT, font=("Segoe UI", 9),
                 anchor="w", justify="left", wraplength=230).grid(row=i, column=1, sticky="w", padx=(0, 12), pady=4)
    PastelButton(win, text="Đóng", variant="soft", command=win.destroy).pack(
        anchor="e", padx=22, pady=14)
    win.update_idletasks()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    win.geometry(f"+{px + 40}+{py + 60}")

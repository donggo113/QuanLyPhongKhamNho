# Thông tin tài khoản + Admin duyệt tài khoản đăng ký mới
import tkinter as tk
from tkinter import messagebox, ttk

from services.auth import (APPROVED, PENDING, REJECTED, STATUS_TEXT,
                           AuthService, role_label)
from ui.theme import ACCENT_PASTEL, BORDER, MUTED, PANEL, TEXT
from ui.widgets import PastelButton
from utils import is_admin, log_action


def info_rows(username, info):
    """Danh sách (nhãn, giá trị) của một tài khoản; bỏ qua mục trống."""
    status = info.get("status", APPROVED)
    rows = [
        ("Tên đăng nhập", username),
        ("Họ và tên", info.get("ho_ten", "")),
        ("Quyền", role_label(info)),
        ("Mã bác sĩ", info.get("ma_bs", "")),
        ("Chuyên khoa", info.get("chuyen_khoa", "")),
        ("Giới tính", info.get("gioi_tinh", "")),
        ("Số điện thoại", info.get("sdt", "")),
        ("Email", info.get("email", "")),
        ("Trạng thái", STATUS_TEXT.get(status, status)),
        ("Ngày tạo", info.get("ngay_tao", "")),
        ("Người duyệt", info.get("nguoi_duyet", "")),
        ("Ngày duyệt", info.get("ngay_duyet", "")),
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


class AccountApprovalView(tk.Frame):
    """Chỉ admin: xem danh sách tài khoản, duyệt / từ chối tài khoản đăng ký mới."""

    COLS = [
        ("TenDN", "Tên đăng nhập", 105, "w"),
        ("HoTen", "Họ và tên", 140, "w"),
        ("SDT", "Số điện thoại", 100, "center"),
        ("Email", "Email", 160, "w"),
        ("Quyen", "Quyền", 80, "center"),
        ("NgayTao", "Ngày đăng ký", 95, "center"),
        ("TrangThai", "Trạng thái", 110, "center"),
    ]
    FILTERS = {"Tất cả": None, "⏳ Chờ duyệt": PENDING, "✅ Đã duyệt": APPROVED, "❌ Từ chối": REJECTED}

    def __init__(self, parent, role="admin", username="", on_change=None):
        super().__init__(parent, bg="#FFFFFF")
        self.role, self.username = role, username
        self.on_change = on_change          # gọi lại để cập nhật số "chờ duyệt" ở menu
        self.auth = AuthService()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        tk.Label(self, text="🔑 DUYỆT TÀI KHOẢN", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        if not is_admin(self.role):
            tk.Label(self, text="Chỉ quản trị viên mới được duyệt tài khoản.", bg="#FFFFFF",
                     fg="#78716C", font=("Segoe UI", 10, "italic")).pack(anchor="w")
            return

        bar = tk.Frame(self, bg="#FFFFFF")
        bar.pack(fill="x", pady=(0, 8))
        tk.Label(bar, text="Hiển thị:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.cbo_filter = ttk.Combobox(bar, values=list(self.FILTERS), state="readonly", width=14)
        self.cbo_filter.set("⏳ Chờ duyệt")
        self.cbo_filter.pack(side="left", padx=6)
        self.cbo_filter.bind("<<ComboboxSelected>>", lambda e: self.load_data())
        PastelButton(bar, text="🔄 Làm mới", variant="plain", command=self.load_data).pack(side="left")
        self.lbl_count = tk.Label(bar, text="", bg="#FFFFFF", fg=MUTED, font=("Segoe UI", 9, "italic"))
        self.lbl_count.pack(side="right")

        table = tk.Frame(self, bg="#FFFFFF")
        table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=[c[0] for c in self.COLS], show="headings", height=8)
        for key, head, width, anchor in self.COLS:
            self.tree.heading(key, text=head)
            self.tree.column(key, width=width, anchor=anchor)
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.tag_configure("pending", background=ACCENT_PASTEL)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        detail = tk.LabelFrame(self, text=" Thông tin tài khoản đang chọn ", bg="#FFFFFF", fg="#1C1917",
                               font=("Segoe UI", 9, "bold"), bd=2, relief="groove")
        detail.pack(fill="x", pady=(10, 0))
        self.lbl_detail = tk.Label(detail, text="Chọn một tài khoản trong danh sách để xem thông tin.",
                                   bg="#FFFFFF", fg=TEXT, font=("Segoe UI", 9), justify="left", anchor="w")
        self.lbl_detail.pack(fill="x", padx=12, pady=8)

        btns = tk.Frame(detail, bg="#FFFFFF")
        btns.pack(fill="x", padx=12, pady=(0, 10))
        PastelButton(btns, text="🗑️ Xóa tài khoản", variant="plain", command=self.delete_account).pack(side="left")
        PastelButton(btns, text="❌ Từ chối", variant="danger", command=lambda: self.change_status(REJECTED)).pack(side="right", padx=(6, 0))
        PastelButton(btns, text="✅ Duyệt tài khoản", variant="success", command=lambda: self.change_status(APPROVED)).pack(side="right")

    def load_data(self):
        if not is_admin(self.role):
            return
        self.auth.reload()
        want = self.FILTERS[self.cbo_filter.get()]
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for uname, info in self.auth.list_users():
            status = self.auth.status_of(info)
            if want and status != want:
                continue
            shown += 1
            self.tree.insert("", "end", iid=uname, tags=("pending",) if status == PENDING else (),
                             values=(uname, info.get("ho_ten", ""), info.get("sdt", ""),
                                     info.get("email", ""), role_label(info),
                                     info.get("ngay_tao", "")[:10], STATUS_TEXT.get(status, status)))
        self.lbl_count.config(text=f"{shown} tài khoản • {self.auth.count_pending()} chờ duyệt")
        self.lbl_detail.config(text="Chọn một tài khoản trong danh sách để xem thông tin.")
        if self.on_change:
            self.on_change()

    def _selected(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def on_select(self, _e=None):
        uname = self._selected()
        if uname:
            self.lbl_detail.config(text=info_text(uname, self.auth.get_user(uname) or {}))

    def delete_account(self):
        uname = self._selected()
        if not uname:
            messagebox.showwarning("Chọn tài khoản", "Vui lòng chọn một tài khoản trong danh sách!", parent=self)
            return
        info = self.auth.get_user(uname) or {}
        if not messagebox.askyesno("Xác nhận xóa",
                                   f"Bạn muốn XÓA tài khoản này? Không thể hoàn tác.\n\n{info_text(uname, info)}",
                                   parent=self):
            return
        ok, msg = self.auth.delete_user(uname, self.username)
        if not ok:
            messagebox.showerror("Lỗi", msg, parent=self)
            return
        log_action(self.username, f"XÓA tài khoản '{uname}'")
        self.load_data()

    def change_status(self, status):
        uname = self._selected()
        if not uname:
            messagebox.showwarning("Chọn tài khoản", "Vui lòng chọn một tài khoản trong danh sách!", parent=self)
            return
        info = self.auth.get_user(uname) or {}
        if self.auth.status_of(info) == status:
            messagebox.showinfo("Thông báo", "Tài khoản đang ở trạng thái này rồi.", parent=self)
            return
        verb = "DUYỆT" if status == APPROVED else "TỪ CHỐI"
        if not messagebox.askyesno(f"Xác nhận {verb.lower()}",
                                   f"Bạn muốn {verb} tài khoản này?\n\n{info_text(uname, info)}", parent=self):
            return
        ok, msg = self.auth.set_status(uname, status, self.username)
        if not ok:
            messagebox.showerror("Lỗi", msg, parent=self)
            return
        log_action(self.username, f"{verb} tài khoản '{uname}'")
        self.load_data()

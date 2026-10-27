# Đăng ký & xếp lịch làm việc
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from db.models import QuanLyPhongKham
from ui.widgets import PastelButton
from utils import is_admin, log_action, today_str, validate_date

CA_LAM = ["Sáng (07:30 - 11:30)", "Chiều (13:30 - 17:30)", "Tối (17:30 - 21:00)"]


class ShiftManagementView(tk.Frame):
    def __init__(self, parent, username="admin", role="admin"):
        super().__init__(parent, bg="#FFFFFF")
        self.username = username
        self.role = role
        self.admin = is_admin(role)
        self.ql = QuanLyPhongKham()
        self.data_shifts = []

        self.setup_ui()
        self.load_shifts()

    def setup_ui(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))
        title = "XẾP LỊCH LÀM VIỆC (QUẢN TRỊ)" if self.admin else "ĐĂNG KÝ LỊCH LÀM VIỆC"
        tk.Label(header, text=f"📅 {title}", bg="#FFFFFF", fg="#EAB308",
                 font=("Segoe UI", 14, "bold")).pack(side="left")

        box = tk.LabelFrame(self, text=" 📝 Đăng ký ca làm ", bg="#FFFFFF", fg="#1C1917",
                            font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        box.pack(fill="x", pady=(0, 10), ipadx=10, ipady=5)
        grid = tk.Frame(box, bg="#FFFFFF")
        grid.pack(fill="x", padx=10, pady=5)

        def lbl(text, c):
            tk.Label(grid, text=text, bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(
                row=0, column=c, sticky="w", padx=(0, 5))

        lbl("Mã NV/Tên:", 0)
        self.ent_user = ttk.Entry(grid, width=20)
        self.ent_user.insert(0, self.username)
        if not self.admin:                       # nhân viên chỉ đăng ký cho chính mình
            self.ent_user.config(state="readonly")
        self.ent_user.grid(row=0, column=1, sticky="w", padx=(0, 20))

        lbl("Ngày làm (YYYY-MM-DD):", 2)
        self.ent_ngay = ttk.Entry(grid, width=20)
        self.ent_ngay.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.ent_ngay.grid(row=0, column=3, sticky="w", padx=(0, 20))

        lbl("Ca làm:", 4)
        self.cbo_ca = ttk.Combobox(grid, values=CA_LAM, state="readonly", width=22)
        self.cbo_ca.set(CA_LAM[0])
        self.cbo_ca.grid(row=0, column=5, sticky="w", padx=(0, 15))

        PastelButton(grid, text="📝 Đăng ký ca", variant="primary", command=self.register_shift).grid(row=0, column=6)

        table = tk.Frame(self, bg="#FFFFFF")
        table.pack(fill="both", expand=True, pady=(0, 10))
        self.tree = ttk.Treeview(table, columns=("MaNV", "Ngay", "CaLam", "TrangThai"), show="headings")
        for key, text, width, anchor in [("MaNV", "Mã NV", 120, "center"), ("Ngay", "Ngày", 120, "center"),
                                         ("CaLam", "Ca Làm", 250, "w"), ("TrangThai", "Trạng Thái", 120, "center")]:
            self.tree.heading(key, text=text)
            self.tree.column(key, anchor=anchor, width=width)
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if self.admin:
            btns = tk.Frame(self, bg="#FFFFFF")
            btns.pack(anchor="w")
            PastelButton(btns, text="✅ Duyệt ca chọn", variant="success",
                         command=lambda: self.change_status("Đã duyệt")).pack(side="left", padx=(0, 8))
            PastelButton(btns, text="❌ Từ chối ca chọn", variant="danger",
                         command=lambda: self.change_status("Từ chối")).pack(side="left")

    def load_shifts(self):
        self.data_shifts = self.ql.ds_lich_lam()
        self.tree.delete(*self.tree.get_children())
        for i, x in enumerate(self.data_shifts):      # iid = vị trí trong danh sách
            self.tree.insert("", "end", iid=str(i),
                             values=(x.get("MaNV", ""), x.get("Ngay", ""), x.get("CaLam", ""), x.get("TrangThai", "")))

    def register_shift(self):
        u = self.ent_user.get().strip()
        n = self.ent_ngay.get().strip()
        c = self.cbo_ca.get()

        if not u or not n:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ tên và ngày làm!", parent=self)
            return
        if not validate_date(n):
            messagebox.showwarning("Cảnh báo", "Ngày làm không hợp lệ (YYYY-MM-DD)!", parent=self)
            return
        if n < today_str():
            messagebox.showwarning("Cảnh báo", "Không thể đăng ký ca cho ngày đã qua!", parent=self)
            return
        if any(x.get("MaNV") == u and x.get("Ngay") == n and x.get("CaLam") == c
               and x.get("TrangThai") != "Từ chối" for x in self.data_shifts):
            messagebox.showerror("Trùng ca", f"{u} đã đăng ký ca này rồi!", parent=self)
            return

        self.data_shifts.append({"MaNV": u, "Ngay": n, "CaLam": c, "TrangThai": "Chờ duyệt"})
        try:
            self.ql.luu_lich_lam(self.data_shifts)
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không thể lưu: {e}", parent=self)
            self.load_shifts()
            return
        log_action(self.username, f"Đăng ký ca làm {c} ngày {n} cho {u}")
        messagebox.showinfo("Thành công", f"Đã đăng ký ca làm thành công cho {u}!", parent=self)
        self.load_shifts()

    def change_status(self, status):
        if not self.admin:           # chặn cả khi ai đó gọi trực tiếp hàm này
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ca làm cần xử lý!", parent=self)
            return
        self.data_shifts[int(sel[0])]["TrangThai"] = status
        try:
            self.ql.luu_lich_lam(self.data_shifts)
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không thể lưu: {e}", parent=self)
            self.load_shifts()
            return
        log_action(self.username, f"Admin chuyển trạng thái ca làm sang '{status}'")
        messagebox.showinfo("Thành công", f"Đã cập nhật trạng thái ca làm thành: {status}", parent=self)
        self.load_shifts()

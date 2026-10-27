# Đăng ký & đặt lịch khám
import os
import tkinter as tk
from tkinter import messagebox, ttk

from config import EXPORT_DIR
from db.models import LichKham, QuanLyPhongKham
from ui.widgets import PastelButton
from utils import export_to_csv, log_action, today_str, validate_date

GIO_KHAM = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]


def _split_label(label):
    ma, _, ten = label.partition(" - ")
    return ma.strip(), (ten.strip() or ma.strip())


class AppointmentRegistrationView(tk.Frame):
    def __init__(self, parent, role="admin", username=""):
        super().__init__(parent, bg="#FFFFFF")
        self.role = role
        self.username = username or str(role)
        self.ql = QuanLyPhongKham()
        self.filter_date = None      # None = hiện tất cả
        self.visible_rows = []       # các dòng đang hiển thị (dùng để xuất CSV)

        self.setup_ui()
        self.load_combobox_data()
        self.load_appointments()

    def setup_ui(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="📅 Đăng Ký & Đặt Lịch Khám", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 15, "bold")).pack(side="left")

        box = tk.LabelFrame(self, text=" ➕ Thêm Lịch Hẹn Mới ", bg="#FFFFFF", fg="#1C1917",
                            font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        box.pack(fill="x", pady=(0, 10), ipadx=10, ipady=5)
        grid = tk.Frame(box, bg="#FFFFFF")
        grid.pack(fill="x", padx=10, pady=5)

        def lbl(text, r, c, pady=0):
            tk.Label(grid, text=text, bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(
                row=r, column=c, sticky="w", padx=(0, 5), pady=(pady, 0))

        lbl("Bệnh nhân:", 0, 0)
        self.cbo_benh_nhan = ttk.Combobox(grid, width=32, state="readonly")
        self.cbo_benh_nhan.grid(row=0, column=1, sticky="w", padx=(0, 20))
        lbl("Bác sĩ khám:", 0, 2)
        self.cbo_bac_si = ttk.Combobox(grid, width=35, state="readonly")
        self.cbo_bac_si.grid(row=0, column=3, sticky="w")

        lbl("Ngày (YYYY-MM-DD):", 1, 0, 8)
        self.ent_ngay = ttk.Entry(grid, width=35)
        self.ent_ngay.insert(0, today_str())
        self.ent_ngay.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(8, 0))
        lbl("Giờ khám:", 1, 2, 8)
        self.cbo_gio = ttk.Combobox(grid, values=GIO_KHAM, state="readonly", width=15)
        self.cbo_gio.set("09:00")
        self.cbo_gio.grid(row=1, column=3, sticky="w", pady=(8, 0))
        PastelButton(grid, text="➕ Đặt Lịch", variant="primary", command=self.create_appointment).grid(
            row=1, column=4, padx=(15, 0), pady=(8, 0))

        # Thanh lọc theo ngày + xuất CSV
        bar = tk.Frame(self, bg="#FFFFFF")
        bar.pack(fill="x", pady=(0, 5))
        tk.Label(bar, text="Lọc theo ngày:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.ent_loc = ttk.Entry(bar, width=14)
        self.ent_loc.insert(0, today_str())
        self.ent_loc.pack(side="left", padx=5)
        PastelButton(bar, text="Lọc", variant="soft", command=self.apply_filter).pack(side="left", padx=2)
        PastelButton(bar, text="Hôm nay", variant="soft", command=self.filter_today).pack(side="left", padx=2)
        PastelButton(bar, text="Tất cả", variant="plain", command=self.filter_all).pack(side="left", padx=2)
        PastelButton(bar, text="📄 Xuất CSV (theo bộ lọc)", variant="soft", command=self.export_csv).pack(side="right")

        table = tk.Frame(self, bg="#FFFFFF")
        table.pack(fill="both", expand=True)
        cols = ("MaBS", "BacSi", "BenhNhan", "NgayKham", "GioKham")
        self.tree = ttk.Treeview(table, columns=cols, show="headings")
        for key, text, width, anchor in [
            ("MaBS", "Mã BS", 80, "center"), ("BacSi", "Bác Sĩ Khám", 200, "w"),
            ("BenhNhan", "Bệnh Nhân", 200, "w"), ("NgayKham", "Ngày Khám", 110, "center"),
            ("GioKham", "Giờ Khám", 90, "center"),
        ]:
            self.tree.heading(key, text=text)
            self.tree.column(key, anchor=anchor, width=width)
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    #  dữ liệu
    def load_combobox_data(self):
        ds_bn = [f"{x['MaBN']} - {x['HoTen']}" for x in self.ql.ds_benh_nhan()]
        ds_bs = [f"{x['MaBS']} - {x['HoTen']}" for x in self.ql.ds_bac_si()]
        self.cbo_benh_nhan["values"] = ds_bn
        self.cbo_bac_si["values"] = ds_bs
        if ds_bn:
            self.cbo_benh_nhan.set(ds_bn[0])
        if ds_bs:
            self.cbo_bac_si.set(ds_bs[0])

    def load_appointments(self):
        self.tree.delete(*self.tree.get_children())
        ds = sorted(self.ql.ds_lich_kham(), key=lambda x: (x.get("NgayKham", ""), x.get("GioKham", "")))
        self.visible_rows = []
        for x in ds:
            if self.filter_date and x.get("NgayKham") != self.filter_date:
                continue
            row = (x.get("MaBS", ""), x.get("BacSi", ""), x.get("BenhNhan", ""),
                   x.get("NgayKham", ""), x.get("GioKham", ""))
            self.visible_rows.append(row)
            self.tree.insert("", "end", values=row)

    #  bộ lọc
    def apply_filter(self):
        d = self.ent_loc.get().strip()
        if not validate_date(d):
            messagebox.showwarning("Cảnh báo", "Ngày lọc không hợp lệ (YYYY-MM-DD)!", parent=self)
            return
        self.filter_date = d
        self.load_appointments()

    def filter_today(self):
        self.ent_loc.delete(0, tk.END)
        self.ent_loc.insert(0, today_str())
        self.apply_filter()

    def filter_all(self):
        self.filter_date = None
        self.load_appointments()

    #  đặt lịch
    def create_appointment(self):
        bn, bs = self.cbo_benh_nhan.get(), self.cbo_bac_si.get()
        ngay, gio = self.ent_ngay.get().strip(), self.cbo_gio.get()

        if not bn or not bs:
            messagebox.showwarning("Cảnh báo", "Cần có bệnh nhân và bác sĩ trong hệ thống!", parent=self)
            return
        if not validate_date(ngay):
            messagebox.showwarning("Cảnh báo", "Ngày khám không hợp lệ (YYYY-MM-DD)!", parent=self)
            return
        if ngay < today_str():
            messagebox.showwarning("Cảnh báo", "Không thể đặt lịch cho ngày đã qua!", parent=self)
            return

        ma_bn, ten_bn = _split_label(bn)
        ma_bs, ten_bs = _split_label(bs)
        try:
            self.ql.dat_lich(LichKham(ma_bs, ten_bs, ma_bn, ten_bn, ngay, gio))   # tự chặn trùng
        except ValueError as e:
            messagebox.showerror("Trùng lịch", str(e), parent=self)
            return
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không thể lưu lịch hẹn: {e}", parent=self)
            return

        log_action(self.username, f"Đặt lịch khám cho {ten_bn} với {ten_bs} lúc {gio} ngày {ngay}")
        messagebox.showinfo("Thành công", f"Đã đặt lịch thành công cho bệnh nhân {ten_bn}!", parent=self)
        self.load_appointments()

    #  xuất CSV
    def export_csv(self):
        if not self.visible_rows:
            messagebox.showwarning("Cảnh báo", "Không có lịch hẹn nào để xuất!", parent=self)
            return
        suffix = self.filter_date or "tat_ca"
        path = os.path.join(EXPORT_DIR, f"bao_cao_lich_kham_{suffix}.csv")
        ok = export_to_csv(path, ["Mã BS", "Bác Sĩ Khám", "Bệnh Nhân", "Ngày Khám", "Giờ Khám"], self.visible_rows)
        if ok:
            log_action(self.username, f"Xuất báo cáo lịch khám ({suffix}) -> {path}")
            messagebox.showinfo("Thành công", f"Đã xuất {len(self.visible_rows)} lịch hẹn:\n{path}", parent=self)
        else:
            messagebox.showerror("Lỗi", "Không thể ghi file CSV (file đang mở trong Excel?).", parent=self)

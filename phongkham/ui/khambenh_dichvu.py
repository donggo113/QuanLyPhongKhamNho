# Khám bệnh, chỉ định dịch vụ, lưu phiếu, xuất hóa đơn TXT
import os
import tkinter as tk
from tkinter import messagebox, ttk

from config import EXPORT_DIR, FILE_DICHVU_API
from db.models import PhieuKhamBenh, QuanLyPhongKham
from db.storage import read_json
from services.api_crawler import DataCrawler
from ui.widgets import PastelButton
from utils import export_invoice_txt, is_admin, log_action, today_str

DICH_VU_MAC_DINH = [
    ("Khám Nội Tổng Quát", 150000),
    ("Xét Nghiệm Máu", 100000),
    ("Siêu Âm Tổng Quát", 200000),
    ("Chụp X-Quang", 180000),
]


def _split_label(label):
    ma, _, ten = label.partition(" - ")
    return ma.strip(), (ten.strip() or ma.strip())


class MedicalServiceView(tk.Frame):
    def __init__(self, parent, role="user", username=""):
        super().__init__(parent, bg="#FFFFFF")
        self.ql = QuanLyPhongKham()
        self.crawler = DataCrawler()
        self.role = role
        self.admin = is_admin(role)
        self.username = username if username else str(role)
        self.dich_vu_da_chon = []     # [{"ten_dv", "gia", "so_luong"}]
        self.dv_map = {}              # nhãn hiển thị -> (tên, giá)

        self.setup_ui()
        self.load_initial_data()

    #  UI
    def setup_ui(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 5))
        left = tk.Frame(header, bg="#FFFFFF")
        left.pack(side="left")
        tk.Label(left, text="🩺 Khám bệnh & Chỉ định dịch vụ", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(left, text="Ghi nhận chẩn đoán, dịch vụ và thanh toán", bg="#FFFFFF", fg="#78716C",
                 font=("Segoe UI", 9)).pack(anchor="w")
        PastelButton(header, text="🔄 Đồng bộ API Dịch vụ", variant="soft",
                     command=self.sync_api_data).pack(side="right", anchor="e")

        top = tk.LabelFrame(self, text="", bg="#FFFFFF", bd=1, relief="solid")
        top.pack(fill="x", pady=(0, 5), ipady=4, ipadx=10)
        g = tk.Frame(top, bg="#FFFFFF")
        g.pack(fill="x", padx=10, pady=2)

        def lbl(text, r, c):
            tk.Label(g, text=text, bg="#FFFFFF", font=("Segoe UI", 9, "bold")).grid(
                row=r, column=c, sticky="w", padx=(0, 5), pady=2)

        lbl("Bệnh nhân:", 0, 0)
        self.cbo_benh_nhan = ttk.Combobox(g, width=35, state="readonly")
        self.cbo_benh_nhan.grid(row=0, column=1, sticky="w", padx=(0, 30))
        lbl("Bác sĩ khám:", 0, 2)
        self.cbo_bac_si = ttk.Combobox(g, width=40, state="readonly")
        self.cbo_bac_si.grid(row=0, column=3, sticky="w")
        lbl("Chẩn đoán:", 1, 0)
        self.ent_chan_doan = ttk.Entry(g, width=38)
        self.ent_chan_doan.grid(row=1, column=1, sticky="w", padx=(0, 30))
        lbl("Ngày khám:", 1, 2)
        tk.Label(g, text=today_str(), bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=1, column=3, sticky="w")

        main = tk.LabelFrame(self, text=" Chi tiết khám bệnh ", bg="#FFFFFF", fg="#1C1917",
                             font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        main.pack(fill="x", pady=(0, 5), ipadx=10, ipady=5)
        inner = tk.Frame(main, bg="#FFFFFF")
        inner.pack(fill="x", padx=10, pady=5)

        tk.Label(inner, text="Nội dung / Triệu chứng khám bệnh:", bg="#FFFFFF",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))
        self.txt_noidung = tk.Text(inner, height=2, font=("Segoe UI", 9), bd=1, relief="solid")
        self.txt_noidung.pack(fill="x", pady=(0, 5))

        bar = tk.Frame(inner, bg="#FFFFFF")
        bar.pack(fill="x", pady=(0, 5))
        tk.Label(bar, text="Dịch vụ:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 5))
        self.cbo_dich_vu = ttk.Combobox(bar, width=42, state="readonly")
        self.cbo_dich_vu.pack(side="left", padx=(0, 8))
        tk.Label(bar, text="SL:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.spn_sl = ttk.Spinbox(bar, from_=1, to=99, width=4)
        self.spn_sl.set(1)
        self.spn_sl.pack(side="left", padx=(3, 8))
        PastelButton(bar, text="+ Dịch vụ", variant="plain", command=self.add_service).pack(side="left", padx=(0, 5))
        PastelButton(bar, text="Xóa dịch vụ", variant="plain", command=self.remove_service).pack(side="left")

        self.tree = ttk.Treeview(inner, columns=("TenDV", "SoLuong", "DonGia", "ThanhTien"),
                                 show="headings", height=3)
        for key, text, width, anchor in [("TenDV", "Tên Dịch Vụ", 350, "w"), ("SoLuong", "Số Lượng", 80, "center"),
                                         ("DonGia", "Đơn Giá", 110, "e"), ("ThanhTien", "Thành Tiền (VNĐ)", 130, "e")]:
            self.tree.heading(key, text=text)
            self.tree.column(key, anchor=anchor, width=width)
        self.tree.pack(fill="x", pady=(0, 5))

        bottom = tk.Frame(inner, bg="#FFFFFF")
        bottom.pack(fill="x")
        self.lbl_tong_tien = tk.Label(bottom, text="TỔNG CHI PHÍ HÓA ĐƠN: 0 VNĐ", bg="#FFFFFF",
                                      fg="#EAB308", font=("Segoe UI", 10, "bold"))
        self.lbl_tong_tien.pack(side="left")
        PastelButton(bottom, text="💾 Lưu phiếu & Xuất hóa đơn", variant="primary", padx=12, pady=4,
                     command=self.save_and_pay).pack(side="right")

        self.setup_payment_section()

    def setup_payment_section(self):
        box = tk.LabelFrame(self, text=" Danh Sách Phiếu Khám & Duyệt Thanh Toán ", bg="#FFFFFF", fg="#1C1917",
                            font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        box.pack(fill="both", expand=True, pady=(5, 0), ipadx=10, ipady=5)

        btns = tk.Frame(box, bg="#FFFFFF")
        btns.pack(anchor="w", padx=10, pady=4)
        if self.admin:
            PastelButton(btns, text="✅ Admin Duyệt & Thanh Toán", variant="success",
                         command=self.approve_payment).pack(side="left", padx=(0, 8))
        PastelButton(btns, text="🧾 Xuất hóa đơn TXT (phiếu chọn)", variant="soft",
                     command=self.export_selected_invoice).pack(side="left")

        cols = ("MaPK", "BenhNhan", "NgayKham", "ChanDoan", "TongTien", "TrangThai", "NguoiTao")
        self.tree_admin = ttk.Treeview(box, columns=cols, show="headings", height=5)
        for key, text, width, anchor in [("MaPK", "Mã PK", 70, "center"), ("BenhNhan", "Bệnh Nhân", 140, "w"),
                                         ("NgayKham", "Ngày Khám", 90, "center"), ("ChanDoan", "Chẩn Đoán", 180, "w"),
                                         ("TongTien", "Tổng Tiền (VNĐ)", 110, "e"), ("TrangThai", "Trạng Thái", 100, "center"),
                                         ("NguoiTao", "Người Tạo", 90, "center")]:
            self.tree_admin.heading(key, text=text)
            self.tree_admin.column(key, anchor=anchor, width=width)
        sb = ttk.Scrollbar(box, orient="vertical", command=self.tree_admin.yview)
        self.tree_admin.configure(yscrollcommand=sb.set)
        self.tree_admin.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 5))
        sb.pack(side="right", fill="y", pady=(0, 5), padx=(0, 5))

    #  dữ liệu
    def load_initial_data(self):
        ds_bn = [f"{x['MaBN']} - {x['HoTen']}" for x in self.ql.ds_benh_nhan()]
        ds_bs = [f"{x['MaBS']} - {x['HoTen']} ({x['ChuyenKhoa']})" for x in self.ql.ds_bac_si()]
        self.cbo_benh_nhan["values"] = ds_bn
        self.cbo_bac_si["values"] = ds_bs
        if ds_bn:
            self.cbo_benh_nhan.set(ds_bn[0])
        if ds_bs:
            self.cbo_bac_si.set(ds_bs[0])

        dich_vu = list(DICH_VU_MAC_DINH)
        crawled = read_json(FILE_DICHVU_API, [])
        if isinstance(crawled, list):
            for x in crawled:
                try:
                    dich_vu.append((x["ten_dich_vu"], int(x["don_gia"])))
                except (KeyError, TypeError, ValueError):
                    continue
        self.dv_map = {f"{ten} - {gia:,}đ": (ten, gia) for ten, gia in dich_vu}
        self.cbo_dich_vu["values"] = list(self.dv_map)
        if self.dv_map:
            self.cbo_dich_vu.set(next(iter(self.dv_map)))

        self.load_phieu_list()

    def load_phieu_list(self):
        self.tree_admin.delete(*self.tree_admin.get_children())
        for p in self.ql.ds_phieu_kham():
            if self.admin or p.get("NguoiTao") == self.username:   # nhân viên chỉ thấy phiếu của mình
                self.tree_admin.insert("", "end", iid=p.get("MaPK", ""), values=(
                    p.get("MaPK", ""), p.get("BenhNhan", ""), p.get("NgayKham", ""), p.get("ChanDoan", ""),
                    f"{int(p.get('TongTien', 0)):,}", p.get("TrangThai", ""), p.get("NguoiTao", "")))

    def sync_api_data(self):
        ok, msg = self.crawler.crawl_or_fetch_api_data()
        if ok:
            messagebox.showinfo("Thành công", msg, parent=self)
            self.load_initial_data()
        else:
            messagebox.showerror("Thất bại", msg, parent=self)

    #  dịch vụ
    def _refresh_services(self):
        self.tree.delete(*self.tree.get_children())
        for dv in self.dich_vu_da_chon:
            self.tree.insert("", "end", values=(dv["ten_dv"], dv["so_luong"], f"{dv['gia']:,}",
                                                f"{dv['gia'] * dv['so_luong']:,}"))
        tong = sum(d["gia"] * d["so_luong"] for d in self.dich_vu_da_chon)
        self.lbl_tong_tien.config(text=f"TỔNG CHI PHÍ HÓA ĐƠN: {tong:,} VNĐ")

    def add_service(self):
        info = self.dv_map.get(self.cbo_dich_vu.get())
        if not info:
            return
        try:
            sl = int(self.spn_sl.get())
            if not 1 <= sl <= 99:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Số lượng phải là số nguyên từ 1 đến 99!", parent=self)
            return
        ten, gia = info
        for dv in self.dich_vu_da_chon:       # cùng dịch vụ -> cộng dồn số lượng
            if dv["ten_dv"] == ten and dv["gia"] == gia:
                dv["so_luong"] += sl
                break
        else:
            self.dich_vu_da_chon.append({"ten_dv": ten, "gia": gia, "so_luong": sl})
        self._refresh_services()

    def remove_service(self):
        sel = self.tree.selection()
        if sel:
            self.dich_vu_da_chon.pop(self.tree.index(sel[0]))
            self._refresh_services()

    #  phiếu khám
    def save_and_pay(self):
        bn, bs = self.cbo_benh_nhan.get(), self.cbo_bac_si.get()
        chan_doan = self.ent_chan_doan.get().strip()
        if not bn or not bs:
            messagebox.showwarning("Cảnh báo", "Cần chọn bệnh nhân và bác sĩ!", parent=self)
            return
        if not chan_doan:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập chẩn đoán bệnh!", parent=self)
            return
        if not self.dich_vu_da_chon:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một dịch vụ!", parent=self)
            return

        ma_bn, ten_bn = _split_label(bn)
        ma_bs, ten_bs = _split_label(bs)
        ten_bs = ten_bs.rsplit(" (", 1)[0]          # bỏ phần "(Chuyên khoa)"
        phieu = PhieuKhamBenh(
            ma_pk=self.ql.tao_ma_phieu(), ma_bn=ma_bn, ten_bn=ten_bn, ma_bs=ma_bs, ten_bs=ten_bs,
            ngay_kham=today_str(), trieu_chung=self.txt_noidung.get("1.0", tk.END).strip(),
            chan_doan=chan_doan, dich_vu=[dict(d) for d in self.dich_vu_da_chon],
            trang_thai="Chờ duyệt", nguoi_tao=self.username,
        )
        try:
            self.ql.them_phieu_kham(phieu)        # LƯU RA FILE
        except OSError as e:
            messagebox.showerror("Lỗi", f"Không thể lưu phiếu khám: {e}", parent=self)
            return

        log_action(self.username, f"Tạo phiếu khám {phieu.ma_pk} cho {ten_bn} (Tổng: {phieu.tong_tien:,} VNĐ)")
        path = os.path.join(EXPORT_DIR, f"hoadon_{phieu.ma_pk}.txt")
        ok = export_invoice_txt(path, phieu.to_invoice_text())   # XUẤT HÓA ĐƠN TXT
        msg = f"Đã lưu phiếu khám {phieu.ma_pk}."
        msg += f"\nHóa đơn: {path}" if ok else "\n(Không xuất được file hóa đơn TXT.)"
        messagebox.showinfo("Thành công", msg, parent=self)

        self.ent_chan_doan.delete(0, tk.END)
        self.txt_noidung.delete("1.0", tk.END)
        self.dich_vu_da_chon.clear()
        self._refresh_services()
        self.load_phieu_list()

    def approve_payment(self):
        if not self.admin:
            return
        sel = self.tree_admin.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phiếu khám cần duyệt!", parent=self)
            return
        ma_pk = sel[0]
        if self.tree_admin.item(sel[0], "values")[5] == "Đã thanh toán":
            messagebox.showinfo("Thông báo", f"Phiếu {ma_pk} đã thanh toán rồi.", parent=self)
            return
        if self.ql.duyet_thanh_toan(ma_pk):
            log_action(self.username, f"Admin duyệt thanh toán cho phiếu {ma_pk}")
            messagebox.showinfo("Thành công", f"Đã duyệt thanh toán cho phiếu {ma_pk}!", parent=self)
            self.load_phieu_list()

    def export_selected_invoice(self):
        sel = self.tree_admin.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phiếu khám cần xuất hóa đơn!", parent=self)
            return
        data = next((p for p in self.ql.ds_phieu_kham() if p.get("MaPK") == sel[0]), None)
        if not data:
            return
        path = os.path.join(EXPORT_DIR, f"hoadon_{sel[0]}.txt")
        if export_invoice_txt(path, PhieuKhamBenh.from_dict(data).to_invoice_text()):
            messagebox.showinfo("Thành công", f"Đã xuất hóa đơn:\n{path}", parent=self)
        else:
            messagebox.showerror("Lỗi", "Không thể ghi file hóa đơn.", parent=self)

# ui/components.py  -- Quản lý bệnh nhân
import tkinter as tk
from tkinter import messagebox, ttk

from db.models import BenhNhan, QuanLyPhongKham
from ui.widgets import PastelButton
from utils import is_admin, log_action, validate_bhyt, validate_phone

COLS = [
    ("MaBN", "Mã BN", 80, "center"),
    ("HoTen", "Họ và Tên", 170, "w"),
    ("Tuoi", "Tuổi", 50, "center"),
    ("GioiTinh", "Giới Tính", 80, "center"),
    ("SoDienThoai", "Số Điện Thoại", 110, "center"),
    ("BHYT", "Thẻ BHYT", 140, "center"),
    ("DiaChi", "Địa Chỉ", 200, "w"),
]


class DataView(tk.Frame):
    def __init__(self, parent, role="admin", username=""):
        super().__init__(parent, bg="#FFFFFF")
        self.role = role
        self.username = username or str(role)
        self.can_edit = is_admin(role)   # chỉ admin được thêm/sửa/xóa
        self.ql = QuanLyPhongKham()
        self.data_list = []

        self.setup_ui()
        self.load_data()

    # ------------------------------------------------------------ UI
    def setup_ui(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="👤 QUẢN LÝ HỒ SƠ BỆNH NHÂN", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        if not self.can_edit:
            tk.Label(header, text="(Chỉ xem)", bg="#FFFFFF", fg="#78716C",
                     font=("Segoe UI", 9, "italic")).pack(side="left", padx=10)

        search = tk.LabelFrame(self, text=" 🔍 Tìm kiếm & Lọc dữ liệu ", bg="#FFFFFF", fg="#1C1917",
                               font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        search.pack(fill="x", pady=(0, 10), ipadx=10, ipady=5)

        tk.Label(search, text="Tìm kiếm:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, pady=5)
        self.ent_search = ttk.Entry(search, width=25)
        self.ent_search.grid(row=0, column=1, padx=5, pady=5)
        self.ent_search.bind("<Return>", lambda e: self.search_data())

        tk.Label(search, text="Tiêu chí:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5, pady=5)
        self.cbo_criterion = ttk.Combobox(search, values=["Mã BN / Tên", "Số điện thoại", "Thẻ BHYT"],
                                          state="readonly", width=15)
        self.cbo_criterion.set("Mã BN / Tên")
        self.cbo_criterion.grid(row=0, column=3, padx=5, pady=5)

        PastelButton(search, text="🔍 Tìm kiếm", variant="soft", command=self.search_data).grid(row=0, column=4, padx=5)
        PastelButton(search, text="🔄 Làm mới", variant="plain", command=self.load_data).grid(row=0, column=5, padx=5)

        table = tk.Frame(self, bg="#FFFFFF")
        table.pack(fill="both", expand=True, pady=(0, 10))
        self.tree = ttk.Treeview(table, columns=[c[0] for c in COLS], show="headings", height=8)
        for key, text, width, anchor in COLS:
            self.tree.heading(key, text=text)
            self.tree.column(key, anchor=anchor, width=width)
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        if not self.can_edit:
            return  # nhân viên chỉ xem: không dựng form

        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        form = tk.LabelFrame(self, text=" 📝 Thông tin bệnh nhân ", bg="#FFFFFF", fg="#1C1917",
                             font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        form.pack(fill="x", ipadx=10, ipady=5)

        def lbl(text, r, c):
            tk.Label(form, text=text, bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=r, column=c, sticky="w", padx=5, pady=3)

        lbl("Mã Bệnh Nhân:*", 0, 0)
        self.ent_mabn = ttk.Entry(form, width=20)
        self.ent_mabn.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        lbl("Họ và Tên:*", 0, 2)
        self.ent_hoten = ttk.Entry(form, width=35)
        self.ent_hoten.grid(row=0, column=3, sticky="w", padx=5, pady=3)

        lbl("Số Điện Thoại:*", 1, 0)
        self.ent_sdt = ttk.Entry(form, width=20)
        self.ent_sdt.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        lbl("Giới Tính:", 1, 2)
        self.cbo_gioitinh = ttk.Combobox(form, values=["Nam", "Nữ", "Khác"], state="readonly", width=12)
        self.cbo_gioitinh.set("Nam")
        self.cbo_gioitinh.grid(row=1, column=3, sticky="w", padx=5, pady=3)

        lbl("Tuổi:", 2, 0)
        self.ent_tuoi = ttk.Entry(form, width=20)
        self.ent_tuoi.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        lbl("Thẻ BHYT:", 2, 2)
        self.ent_bhyt = ttk.Entry(form, width=35)
        self.ent_bhyt.grid(row=2, column=3, sticky="w", padx=5, pady=3)

        lbl("Địa Chỉ:", 3, 0)
        self.ent_diachi = ttk.Entry(form, width=65)
        self.ent_diachi.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=3)

        lbl("Tiền sử bệnh:", 4, 0)
        self.ent_tiensu = ttk.Entry(form, width=65)
        self.ent_tiensu.grid(row=4, column=1, columnspan=3, sticky="w", padx=5, pady=3)

        box = tk.Frame(form, bg="#FFFFFF")
        box.grid(row=5, column=0, columnspan=4, pady=8, sticky="e")
        PastelButton(box, text="🧹 Nhập lại", variant="plain", command=self.clear_form).pack(side="left", padx=5)
        PastelButton(box, text="➕ Thêm mới", variant="primary", command=self.create_record).pack(side="left", padx=5)
        PastelButton(box, text="✏️ Cập nhật", variant="info", command=self.update_record).pack(side="left", padx=5)
        PastelButton(box, text="🗑️ Xóa", variant="danger", command=self.delete_record).pack(side="left", padx=5)

    # ------------------------------------------------------------ dữ liệu
    def load_data(self):
        self.data_list = self.ql.ds_benh_nhan()
        self._fill_tree(self.data_list)
        self.clear_form()

    def _fill_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for item in rows:
            self.tree.insert("", "end", iid=item["MaBN"],
                             values=tuple(item.get(k, "") for k, *_ in COLS))

    def _commit(self, action, ok_msg):
        """Ghi file + log + thông báo + nạp lại."""
        try:
            self.ql.luu_benh_nhan(self.data_list)
        except OSError as e:
            messagebox.showerror("Lỗi Lưu File", f"Không thể lưu dữ liệu: {e}", parent=self)
            self.load_data()
            return
        log_action(self.username, action)
        messagebox.showinfo("Thành công", ok_msg, parent=self)
        self.load_data()

    def _read_form(self):
        """Đọc + kiểm tra form. Trả về BenhNhan hoặc None."""
        ma = self.ent_mabn.get().strip().upper()
        ten = self.ent_hoten.get().strip()
        sdt = self.ent_sdt.get().strip()
        tuoi = self.ent_tuoi.get().strip()
        bhyt = self.ent_bhyt.get().strip().upper()

        if not ma or not ten or not sdt:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ các trường bắt buộc (*)", parent=self)
            return None
        if not validate_phone(sdt):
            messagebox.showerror("Lỗi định dạng",
                                 "Số điện thoại không hợp lệ (đúng 10 số, đầu 03/05/07/08/09)!", parent=self)
            return None
        if tuoi and not (tuoi.isascii() and tuoi.isdigit() and 0 <= int(tuoi) <= 150):
            messagebox.showerror("Lỗi định dạng", "Tuổi phải là số nguyên từ 0 đến 150!", parent=self)
            return None
        if not validate_bhyt(bhyt):
            messagebox.showerror("Lỗi định dạng",
                                 "Thẻ BHYT không hợp lệ!\nĐịnh dạng: 2 chữ cái + 13 chữ số (VD: HS4010123456789)",
                                 parent=self)
            return None

        return BenhNhan(
            ma_bn=ma, ho_ten=ten, sdt=sdt, gioi_tinh=self.cbo_gioitinh.get(),
            tuoi=int(tuoi) if tuoi else "", bhyt=bhyt,
            dia_chi=self.ent_diachi.get().strip() or "Chưa cập nhật",
            tien_su=self.ent_tiensu.get().strip() or "Không",
        )

    # ------------------------------------------------------------ CRUD
    def create_record(self):
        bn = self._read_form()
        if not bn:
            return
        if any(x["MaBN"] == bn.ma_bn for x in self.data_list):
            messagebox.showerror("Lỗi trùng mã",
                                 f"Mã bệnh nhân '{bn.ma_bn}' đã tồn tại!\n(Bấm 'Nhập lại' nếu đang chọn dòng cũ.)",
                                 parent=self)
            return
        self.data_list.append(bn.to_dict())
        self._commit(f"Thêm mới bệnh nhân: {bn.ma_bn} - {bn.ho_ten}", f"Đã thêm bệnh nhân {bn.ma_bn} thành công!")

    def update_record(self):
        if not self.ent_mabn.get().strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bệnh nhân từ bảng để chỉnh sửa!", parent=self)
            return
        bn = self._read_form()
        if not bn:
            return
        item = next((x for x in self.data_list if x["MaBN"] == bn.ma_bn), None)
        if item is None:
            messagebox.showerror("Lỗi", "Không tìm thấy bệnh nhân này!", parent=self)
            return
        item.update(bn.to_dict())
        self._commit(f"Cập nhật bệnh nhân: {bn.ma_bn}", f"Đã cập nhật dữ liệu bệnh nhân {bn.ma_bn}!")

    def delete_record(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bệnh nhân cần xóa!", parent=self)
            return
        ma = sel[0]
        item = next((x for x in self.data_list if x["MaBN"] == ma), None)
        if item is None:
            return
        if self.ql.benh_nhan_co_du_lieu(ma):
            messagebox.showerror("Không thể xóa",
                                 f"Bệnh nhân {ma} đã có lịch khám hoặc phiếu khám nên không thể xóa.", parent=self)
            return
        if messagebox.askyesno("Xác nhận xóa", f"Xóa bệnh nhân '{item['HoTen']}' ({ma})?", parent=self):
            self.data_list = [x for x in self.data_list if x["MaBN"] != ma]
            self._commit(f"Xóa bệnh nhân: {ma} - {item['HoTen']}", f"Đã xóa bệnh nhân {ma}!")

    def search_data(self):
        q = self.ent_search.get().strip().lower()
        fields = {"Mã BN / Tên": ("MaBN", "HoTen"),
                  "Số điện thoại": ("SoDienThoai",),
                  "Thẻ BHYT": ("BHYT",)}[self.cbo_criterion.get()]
        rows = [x for x in self.data_list
                if not q or any(q in str(x.get(f, "")).lower() for f in fields)]
        self._fill_tree(rows)

    # ------------------------------------------------------------ form
    def on_select_record(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = next((x for x in self.data_list if x["MaBN"] == sel[0]), None)
        if not item:
            return
        self.ent_mabn.config(state="normal")
        for e in (self.ent_mabn, self.ent_hoten, self.ent_sdt, self.ent_tuoi,
                  self.ent_bhyt, self.ent_diachi, self.ent_tiensu):
            e.delete(0, tk.END)
        self.ent_mabn.insert(0, item["MaBN"])
        self.ent_mabn.config(state="readonly")
        self.ent_hoten.insert(0, item["HoTen"])
        self.ent_sdt.insert(0, item["SoDienThoai"])
        self.ent_tuoi.insert(0, item.get("Tuoi", ""))
        self.ent_bhyt.insert(0, item.get("BHYT", ""))
        self.ent_diachi.insert(0, item.get("DiaChi", ""))
        self.ent_tiensu.insert(0, item.get("TienSu", ""))
        self.cbo_gioitinh.set(item.get("GioiTinh", "Nam"))

    def clear_form(self):
        if not self.can_edit:
            return
        self.ent_mabn.config(state="normal")
        for e in (self.ent_mabn, self.ent_hoten, self.ent_sdt, self.ent_tuoi,
                  self.ent_bhyt, self.ent_diachi, self.ent_tiensu):
            e.delete(0, tk.END)
        self.cbo_gioitinh.set("Nam")
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(sel)

# ui/quanlybacsi.py  -- Quản lý bác sĩ
import tkinter as tk
from tkinter import messagebox, ttk

from db.models import BacSi, QuanLyPhongKham
from ui.widgets import PastelButton
from utils import is_admin, log_action, validate_email, validate_phone

COLS = [
    ("MaBS", "Mã BS", 80, "center"),
    ("HoTen", "Họ và Tên", 180, "w"),
    ("ChuyenKhoa", "Chuyên Khoa", 140, "w"),
    ("SoDienThoai", "Số Điện Thoại", 120, "center"),
    ("Email", "Email", 200, "w"),
]


class DoctorManagementView(tk.Frame):
    def __init__(self, parent, role="admin", username=""):
        super().__init__(parent, bg="#FFFFFF")
        self.role = role
        self.username = username or str(role)
        self.can_edit = is_admin(role)   # chỉ admin được thêm/sửa/xóa
        self.ql = QuanLyPhongKham()
        self.data_list = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="👨‍⚕️ QUẢN LÝ DANH SÁCH BÁC SĨ", bg="#FFFFFF", fg="#1C1917",
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        if not self.can_edit:
            tk.Label(header, text="(Chỉ xem)", bg="#FFFFFF", fg="#78716C",
                     font=("Segoe UI", 9, "italic")).pack(side="left", padx=10)

        search = tk.LabelFrame(self, text=" Tìm kiếm bác sĩ (theo mã, tên hoặc chuyên khoa) ", bg="#FFFFFF",
                               fg="#1C1917", font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        search.pack(fill="x", pady=(0, 10), ipadx=10, ipady=5)
        tk.Label(search, text="Tìm kiếm:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, pady=5)
        self.ent_search = ttk.Entry(search, width=30)
        self.ent_search.grid(row=0, column=1, padx=5, pady=5)
        self.ent_search.bind("<Return>", lambda e: self.search_data())
        PastelButton(search, text="🔍 Tìm kiếm", variant="soft", command=self.search_data).grid(row=0, column=2, padx=5)
        PastelButton(search, text="🔄 Làm mới", variant="plain", command=self.load_data).grid(row=0, column=3, padx=5)

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
            return

        self.tree.bind("<<TreeviewSelect>>", self.on_select_record)

        form = tk.LabelFrame(self, text=" 📝 Thông tin bác sĩ ", bg="#FFFFFF", fg="#1C1917",
                             font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        form.pack(fill="x", ipadx=10, ipady=5)

        def lbl(text, r, c):
            tk.Label(form, text=text, bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=r, column=c, sticky="w", padx=5, pady=3)

        lbl("Mã Bác Sĩ:*", 0, 0)
        self.ent_mabs = ttk.Entry(form, width=20)
        self.ent_mabs.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        lbl("Họ và Tên:*", 0, 2)
        self.ent_hoten = ttk.Entry(form, width=35)
        self.ent_hoten.grid(row=0, column=3, sticky="w", padx=5, pady=3)
        lbl("Chuyên Khoa:*", 1, 0)
        self.ent_ck = ttk.Entry(form, width=20)
        self.ent_ck.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        lbl("Số Điện Thoại:*", 1, 2)
        self.ent_sdt = ttk.Entry(form, width=35)
        self.ent_sdt.grid(row=1, column=3, sticky="w", padx=5, pady=3)
        lbl("Email:", 2, 0)
        self.ent_email = ttk.Entry(form, width=60)
        self.ent_email.grid(row=2, column=1, columnspan=3, sticky="w", padx=5, pady=3)

        box = tk.Frame(form, bg="#FFFFFF")
        box.grid(row=3, column=0, columnspan=4, pady=8, sticky="e")
        PastelButton(box, text="🧹 Nhập lại", variant="plain", command=self.clear_form).pack(side="left", padx=5)
        PastelButton(box, text="➕ Thêm mới", variant="primary", command=self.create_record).pack(side="left", padx=5)
        PastelButton(box, text="✏️ Cập nhật", variant="info", command=self.update_record).pack(side="left", padx=5)
        PastelButton(box, text="🗑️ Xóa", variant="danger", command=self.delete_record).pack(side="left", padx=5)

    # ------------------------------------------------------------ dữ liệu
    def load_data(self):
        self.data_list = self.ql.ds_bac_si()
        self._fill_tree(self.data_list)
        self.clear_form()

    def _fill_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for item in rows:
            self.tree.insert("", "end", iid=item["MaBS"],
                             values=tuple(item.get(k, "") for k, *_ in COLS))

    def _commit(self, action, ok_msg):
        try:
            self.ql.luu_bac_si(self.data_list)
        except OSError as e:
            messagebox.showerror("Lỗi Lưu File", f"Không thể lưu dữ liệu: {e}", parent=self)
            self.load_data()
            return
        log_action(self.username, action)
        messagebox.showinfo("Thành công", ok_msg, parent=self)
        self.load_data()

    def _read_form(self):
        ma = self.ent_mabs.get().strip().upper()
        ten = self.ent_hoten.get().strip()
        ck = self.ent_ck.get().strip()
        sdt = self.ent_sdt.get().strip()
        email = self.ent_email.get().strip()

        if not ma or not ten or not ck or not sdt:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ các trường bắt buộc (*)", parent=self)
            return None
        if not validate_phone(sdt):
            messagebox.showerror("Lỗi định dạng",
                                 "Số điện thoại không hợp lệ (đúng 10 số, đầu 03/05/07/08/09)!", parent=self)
            return None
        if not validate_email(email):
            messagebox.showerror("Lỗi định dạng", "Email không hợp lệ (VD: ten@phongkham.vn)!", parent=self)
            return None
        return BacSi(ma, ten, ck, sdt, email)

    # ------------------------------------------------------------ CRUD
    def create_record(self):
        bs = self._read_form()
        if not bs:
            return
        if any(x["MaBS"] == bs.ma_bs for x in self.data_list):
            messagebox.showerror("Lỗi trùng mã",
                                 f"Mã bác sĩ '{bs.ma_bs}' đã tồn tại!\n(Bấm 'Nhập lại' nếu đang chọn dòng cũ.)",
                                 parent=self)
            return
        self.data_list.append(bs.to_dict())
        self._commit(f"Thêm bác sĩ: {bs.ma_bs} - {bs.ho_ten}", f"Đã thêm bác sĩ {bs.ma_bs} thành công!")

    def update_record(self):
        if not self.ent_mabs.get().strip():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bác sĩ từ bảng để chỉnh sửa!", parent=self)
            return
        bs = self._read_form()
        if not bs:
            return
        item = next((x for x in self.data_list if x["MaBS"] == bs.ma_bs), None)
        if item is None:
            messagebox.showerror("Lỗi", "Không tìm thấy bác sĩ này!", parent=self)
            return
        item.update(bs.to_dict())
        self._commit(f"Cập nhật bác sĩ: {bs.ma_bs}", f"Đã cập nhật dữ liệu bác sĩ {bs.ma_bs}!")

    def delete_record(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bác sĩ cần xóa!", parent=self)
            return
        ma = sel[0]
        item = next((x for x in self.data_list if x["MaBS"] == ma), None)
        if item is None:
            return
        if self.ql.bac_si_con_lich(ma):
            messagebox.showerror("Không thể xóa",
                                 f"Bác sĩ {ma} vẫn còn lịch hẹn từ hôm nay trở đi.\nHãy xử lý các lịch này trước.",
                                 parent=self)
            return
        if messagebox.askyesno("Xác nhận xóa", f"Xóa bác sĩ '{item['HoTen']}' ({ma})?", parent=self):
            self.data_list = [x for x in self.data_list if x["MaBS"] != ma]
            self._commit(f"Xóa bác sĩ: {ma} - {item['HoTen']}", f"Đã xóa bác sĩ {ma}!")

    def search_data(self):
        q = self.ent_search.get().strip().lower()
        rows = [x for x in self.data_list
                if not q or any(q in str(x.get(f, "")).lower() for f in ("MaBS", "HoTen", "ChuyenKhoa"))]
        self._fill_tree(rows)

    # ------------------------------------------------------------ form
    def _entries(self):
        return (self.ent_mabs, self.ent_hoten, self.ent_ck, self.ent_sdt, self.ent_email)

    def on_select_record(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = next((x for x in self.data_list if x["MaBS"] == sel[0]), None)
        if not item:
            return
        self.ent_mabs.config(state="normal")
        for e in self._entries():
            e.delete(0, tk.END)
        self.ent_mabs.insert(0, item["MaBS"])
        self.ent_mabs.config(state="readonly")
        self.ent_hoten.insert(0, item["HoTen"])
        self.ent_ck.insert(0, item["ChuyenKhoa"])
        self.ent_sdt.insert(0, item["SoDienThoai"])
        self.ent_email.insert(0, item.get("Email", ""))

    def clear_form(self):
        if not self.can_edit:
            return
        self.ent_mabs.config(state="normal")
        for e in self._entries():
            e.delete(0, tk.END)
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(sel)

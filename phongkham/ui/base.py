import tkinter as tk
from tkinter import messagebox
from .dashboard import DashboardView
from services.auth import AuthService
from utils import is_admin


class AppShell(tk.Frame):

    def __init__(self, parent, username="admin", role="admin", **kwargs):
        super().__init__(parent, bg="#FAF8F5")
        self.parent = parent
        self.username = username
        self.role = role
        self.pack(fill="both", expand=True)

        self.setup_sidebar()

        self.content = tk.Frame(self, bg="#FAF8F5")
        self.content.pack(
            side="right", fill="both", expand=True, padx=20, pady=15
        )

        # Mặc định hiển thị Bảng điều khiển (Dashboard)
        self.show_dashboard()

    def setup_sidebar(self):
        sidebar = tk.Frame(self, bg="#FEF9C3", width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        header_frame = tk.Frame(sidebar, bg="#FEF9C3", pady=20, padx=15)
        header_frame.pack(fill="x")

        lbl_icon = tk.Label(
            header_frame,
            text="🏥 PHÒNG KHÁM",
            bg="#FEF9C3",
            fg="#854D0E",
            font=("Segoe UI", 14, "bold"),
        )
        lbl_icon.pack(anchor="w")

        tk.Frame(header_frame, bg="#EAB308", height=1).pack(
            fill="x", pady=(10, 0)
        )

        tk.Label(
            sidebar,
            text="MENU QUẢN LÝ",
            bg="#FEF9C3",
            fg="#A16207",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 10))

        btn_style = {
            "bg": "#FEF9C3",
            "fg": "#713F12",
            "activebackground": "#FEF08A",
            "activeforeground": "#854D0E",
            "font": ("Segoe UI", 10, "bold"),
            "anchor": "w",
            "relief": "flat",
            "bd": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2",
        }

        self.btn_dash = tk.Button(
            sidebar,
            text="📊 Tổng Quan",
            command=self.show_dashboard,
            **btn_style,
        )
        self.btn_dash.pack(fill="x", pady=2)

        self.btn_app = tk.Button(
            sidebar,
            text="📑 Đăng ký & Đặt lịch",
            command=self.show_appointments,
            **btn_style,
        )
        self.btn_app.pack(fill="x", pady=2)

        self.btn_med = tk.Button(
            sidebar,
            text="🩺 Khám bệnh & Dịch vụ",
            command=self.show_medical_records,
            **btn_style,
        )
        self.btn_med.pack(fill="x", pady=2)

        self.btn_pat = tk.Button(
            sidebar,
            text="👤 Quản lý Bệnh nhân",
            command=self.show_patients,
            **btn_style,
        )
        self.btn_pat.pack(fill="x", pady=2)

        self.btn_doc = tk.Button(
            sidebar,
            text="👨 Quản lý Bác sĩ",
            command=self.show_doctors,
            **btn_style,
        )
        self.btn_doc.pack(fill="x", pady=2)

        self.btn_shifts = tk.Button(
            sidebar,
            text="📅 Đăng ký & Xếp lịch làm",
            command=self.show_shifts,
            **btn_style,
        )
        self.btn_shifts.pack(fill="x", pady=2)

        # Chỉ quản trị viên: duyệt tài khoản đăng ký mới
        self.btn_accounts = None
        if is_admin(self.role):
            self.btn_accounts = tk.Button(
                sidebar,
                text="🔑 Duyệt tài khoản",
                command=self.show_accounts,
                **btn_style,
            )
            self.btn_accounts.pack(fill="x", pady=2)
            self.refresh_pending_badge()

        # Thông tin user ở góc dưới
        bottom_frame = tk.Frame(sidebar, bg="#FEF9C3", pady=15, padx=15)
        bottom_frame.pack(side="bottom", fill="x")

        user_box = tk.Frame(bottom_frame, bg="#FEF9C3", cursor="hand2")
        user_box.pack(fill="x", pady=(0, 10))
        icon = tk.Label(
            user_box, text="👤", bg="#FEF9C3", fg="#854D0E",
            font=("Segoe UI Emoji", 16), cursor="hand2",
        )
        icon.pack(side="left", padx=(0, 8))
        info = tk.Frame(user_box, bg="#FEF9C3", cursor="hand2")
        info.pack(side="left")
        name_lbl = tk.Label(
            info, text=self.username, bg="#FEF9C3", fg="#854D0E",
            font=("Segoe UI", 10, "bold"), anchor="w", cursor="hand2",
        )
        name_lbl.pack(anchor="w")
        role_lbl = tk.Label(
            info, text=str(self.role).upper() + "  ›", bg="#FEF9C3", fg="#A16207",
            font=("Segoe UI", 8, "bold"), anchor="w", cursor="hand2",
        )
        role_lbl.pack(anchor="w")
        self._user_widgets = [user_box, icon, info, name_lbl, role_lbl]
        for w in self._user_widgets:
            w.bind("<Button-1>", lambda e: self.show_account_info())
            w.bind("<Enter>", lambda e: self._tint_user("#FEF08A"))
            w.bind("<Leave>", lambda e: self._tint_user("#FEF9C3"))

        btn_logout = tk.Button(
            bottom_frame,
            text="🚪 Đăng xuất",
            command=self.handle_logout,
            bg="#FEF08A",
            fg="#854D0E",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            pady=6,
            cursor="hand2",
        )
        btn_logout.pack(fill="x")

    def _tint_user(self, color):
        for w in self._user_widgets:
            w.config(bg=color)

    def show_account_info(self):
        from .quanlytaikhoan import show_account_info

        show_account_info(self, self.username)

    def refresh_pending_badge(self):
        """Hiện số tài khoản đang chờ duyệt trên nút menu (chỉ admin)."""
        if not self.btn_accounts:
            return
        n = AuthService().count_pending()
        self.btn_accounts.config(
            text="🔑 Duyệt tài khoản" + (f"  ({n})" if n else "")
        )

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def show_dashboard(self):
        self.clear_content()
        view = DashboardView(self.content)
        view.pack(fill="both", expand=True)

    def show_appointments(self):
        self.clear_content()
        from .dangkylichkham import AppointmentRegistrationView

        view = AppointmentRegistrationView(
            self.content, role=self.role, username=self.username
        )
        view.pack(fill="both", expand=True)

    def show_medical_records(self):
        self.clear_content()
        from .khambenh_dichvu import MedicalServiceView

        view = MedicalServiceView(
            self.content, role=self.role, username=self.username
        )
        view.pack(fill="both", expand=True)

    def show_patients(self):
        self.clear_content()
        from .components import DataView

        view = DataView(self.content, role=self.role, username=self.username)
        view.pack(fill="both", expand=True)

    def show_doctors(self):
        self.clear_content()
        from .quanlybacsi import DoctorManagementView

        view = DoctorManagementView(
            self.content, role=self.role, username=self.username
        )
        view.pack(fill="both", expand=True)

    def show_shifts(self):
        self.clear_content()
        from .phanlichlam import ShiftManagementView

        view = ShiftManagementView(
            self.content, username=self.username, role=self.role
        )
        view.pack(fill="both", expand=True)

    def show_accounts(self):
        self.clear_content()
        from .quanlytaikhoan import AccountApprovalView

        view = AccountApprovalView(
            self.content, role=self.role, username=self.username,
            on_change=self.refresh_pending_badge,
        )
        view.pack(fill="both", expand=True)

    def handle_logout(self):
        if messagebox.askyesno(
            "Đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất không?",
            parent=self.parent,
        ):
            for widget in self.parent.winfo_children():
                widget.destroy()
            from .login import LoginPage

            LoginPage(self.parent)


BaseLayout = AppShell
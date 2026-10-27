# ui/dashboard.py  -- Thống kê bằng Canvas, số liệu thật từ dữ liệu phòng khám
import tkinter as tk
from tkinter import messagebox

from db.models import QuanLyPhongKham
from ui.widgets import PastelButton
from utils import is_admin
from ui.theme import ACCENT, BG, BORDER, DANGER, MUTED, PANEL, SUCCESS, TEXT, WARNING


class DashboardView(tk.Frame):
    def __init__(self, parent, role="user", on_refresh=None):
        super().__init__(parent, bg=BG)
        self.on_refresh = on_refresh
        tk_ke = QuanLyPhongKham().thong_ke()

        if is_admin(role):      # chỉ admin: nạp / xóa số liệu mẫu cho biểu đồ
            from services.sample_data import co_so_lieu_mau
            bar = tk.Frame(self, bg=BG)
            bar.pack(fill="x", pady=(0, 8))
            if co_so_lieu_mau():
                PastelButton(bar, text="🗑️ Xóa số liệu mẫu", variant="plain",
                             command=self.clear_sample).pack(side="right")
            else:
                PastelButton(bar, text="🧪 Nạp số liệu mẫu", variant="soft",
                             command=self.load_sample).pack(side="right")

        stats = tk.Frame(self, bg=BG)
        stats.pack(fill="x", pady=(0, 15))
        cards = [
            ("👤 TỔNG BỆNH NHÂN", f"{tk_ke['tong_benh_nhan']:,}", "Hồ sơ", ACCENT),
            ("📅 LỊCH KHÁM HÔM NAY", f"{tk_ke['lich_hom_nay']:,}", "Lượt hẹn", WARNING),
            ("✅ ĐÃ KHÁM HÔM NAY", f"{tk_ke['da_kham_hom_nay']:,}", "Phiếu khám", SUCCESS),
            ("💰 DOANH THU THÁNG NÀY", f"{tk_ke['doanh_thu_thang']:,}", "VNĐ", DANGER),
        ]
        for i, (title, val, unit, color) in enumerate(cards):
            card = tk.Frame(stats, bg=PANEL, highlightbackground=BORDER, highlightthickness=1, height=85)
            card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 5, 0))
            card.pack_propagate(False)
            tk.Frame(card, bg=color, width=5).pack(side="left", fill="y")
            tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
            row = tk.Frame(card, bg=PANEL)
            row.pack(anchor="w", padx=12)
            tk.Label(row, text=val, bg=PANEL, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(side="left")
            tk.Label(row, text=f" {unit}", bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(side="left", pady=(5, 0))

        charts = tk.Frame(self, bg=BG)
        charts.pack(fill="both", expand=True)
        self.create_bar_chart(charts, "📈 LƯỢT KHÁM 6 THÁNG GẦN NHẤT", tk_ke["luot_kham"], ACCENT, col=0)
        self.create_bar_chart(charts, "💵 DOANH THU ĐÃ THU 6 THÁNG (Triệu VNĐ)", tk_ke["doanh_thu"], SUCCESS, col=1)

    def load_sample(self):
        from services.sample_data import them_mau
        ok, msg = them_mau()
        (messagebox.showinfo if ok else messagebox.showwarning)("Số liệu mẫu", msg, parent=self)
        if ok and self.on_refresh:
            self.on_refresh()

    def clear_sample(self):
        from services.sample_data import xoa_mau
        if messagebox.askyesno("Xóa số liệu mẫu", "Xóa toàn bộ phiếu khám mẫu (mã PKM...)?\nPhiếu thật không bị ảnh hưởng.", parent=self):
            xoa_mau()
            if self.on_refresh:
                self.on_refresh()

    def create_bar_chart(self, parent, title, chart_data, bar_color, col):
        box = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        box.pack(side="left", fill="both", expand=True, padx=(0 if col == 0 else 8, 0))
        tk.Label(box, text=title, bg=PANEL, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=15, pady=12)

        canvas = tk.Canvas(box, bg=PANEL, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        def draw(event):
            canvas.delete("all")
            w, h = event.width, event.height
            pad_b, pad_t = 30, 25
            chart_h = max(h - pad_b - pad_t, 1)
            max_val = max((v for _, v in chart_data), default=0) * 1.2 or 1
            n = len(chart_data)
            spacing = w / n
            bar_w = spacing * 0.45

            canvas.create_line(10, h - pad_b, w - 10, h - pad_b, fill=BORDER, width=2)
            for i, (label, val) in enumerate(chart_data):
                x0 = i * spacing + (spacing - bar_w) / 2
                x1 = x0 + bar_w
                y1 = h - pad_b
                y0 = y1 - val / max_val * chart_h
                canvas.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline="")
                canvas.create_text((x0 + x1) / 2, y0 - 10, text=f"{val:g}", fill=TEXT, font=("Segoe UI", 8, "bold"))
                canvas.create_text((x0 + x1) / 2, h - 12, text=label, fill=MUTED, font=("Segoe UI", 9))

        canvas.bind("<Configure>", draw)

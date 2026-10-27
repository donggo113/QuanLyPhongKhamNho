# Custom widget kế thừa tk.Button, có hiệu ứng hover
import tkinter as tk

# variant: (màu nền, màu khi hover, màu chữ)
_VARIANTS = {
    "primary": ("#EAB308", "#CA8A04", "#FFFFFF"),
    "success": ("#22C55E", "#16A34A", "#FFFFFF"),
    "danger": ("#EF4444", "#DC2626", "#FFFFFF"),
    "info": ("#3B82F6", "#2563EB", "#FFFFFF"),
    "soft": ("#FEF08A", "#FDE047", "#854D0E"),
    "plain": ("#F3F4F6", "#E5E7EB", "#1F2937"),
}


class PastelButton(tk.Button):
    def __init__(self, master=None, variant="primary", **kw):
        bg, hover, fg = _VARIANTS[variant]
        kw.setdefault("bg", bg)
        kw.setdefault("fg", fg)
        kw.setdefault("activebackground", hover)
        kw.setdefault("activeforeground", fg)
        kw.setdefault("relief", "flat")
        kw.setdefault("bd", 0)
        kw.setdefault("font", ("Segoe UI", 9, "bold"))
        kw.setdefault("cursor", "hand2")
        kw.setdefault("padx", 10)
        kw.setdefault("pady", 3)
        super().__init__(master, **kw)
        self._normal_bg = kw["bg"]
        self._hover_bg = hover
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e):
        if str(self["state"]) != "disabled":
            self.config(bg=self._hover_bg)

    def _on_leave(self, _e):
        self.config(bg=self._normal_bg)

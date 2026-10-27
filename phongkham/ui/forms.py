import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from .theme import BG, PANEL, TEXT, MUTED

class FormDialog(tk.Toplevel):
    def __init__(self, parent, title, fields, values=None, on_submit=None, submit_text="Lưu", optional_fields=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.geometry("520x650")
        self.minsize(480, 520)
        self.transient(parent)
        self.grab_set()

        self.on_submit = on_submit
        self.vars = {}
        self.optional_fields = set(optional_fields or [])
        self.readonly_fields = {f[1] for f in fields if len(f) > 2 and f[2] == "readonly"}
        values = values or {}

        outer = tk.Frame(self, bg=PANEL, highlightbackground="#CBD5E1", highlightthickness=1)
        outer.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(outer, text="📝 " + title, bg=PANEL, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=22, pady=(18, 2))
        tk.Label(outer, text="Vui lòng điền đầy đủ thông tin bên dưới.", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=22, pady=(0, 10))

        actions = tk.Frame(outer, bg=PANEL)
        actions.pack(side="bottom", fill="x", padx=22, pady=(12, 18))

        canvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=PANEL)
        window_id = canvas.create_window((0, 0), window=body, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(22, 0), pady=2)
        scrollbar.pack(side="right", fill="y", padx=(0, 18), pady=2)

        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

        for field in fields:
            label, key, kind = field[:3]
            tk.Label(body, text=label, bg=PANEL, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(7, 4))

            var = tk.StringVar(value=str(values.get(key, "")))
            self.vars[key] = var

            if kind == "readonly":
                widget = ttk.Entry(body, textvariable=var, state="readonly")
            elif kind == "combo":
                options = field[3] if len(field) > 3 else []
                widget = ttk.Combobox(body, textvariable=var, values=options, state="readonly")
                if not var.get() and options:
                    widget.set(options[0])
            elif kind == "date":
                widget = DateEntry(body, textvariable=var, date_pattern="yyyy-mm-dd", background="#0284C7", foreground="white", borderwidth=1)
            else:
                widget = ttk.Entry(body, textvariable=var)

            widget.pack(fill="x", ipady=4, padx=(0, 8))

        ttk.Button(actions, text="Hủy", command=self.destroy).pack(side="right")
        ttk.Button(actions, text=submit_text, style="Primary.TButton", command=self.submit).pack(side="right", padx=8)

    def submit(self):
        data = {key: var.get().strip() for key, var in self.vars.items()}
        missing = [key for key, val in data.items() if not val and key not in self.optional_fields and key not in self.readonly_fields]
        if missing:
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin bắt buộc!", parent=self)
            return
        if self.on_submit:
            try:
                self.on_submit(data)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu: {e}", parent=self)
                return
        self.destroy()
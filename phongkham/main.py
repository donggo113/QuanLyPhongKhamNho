import tkinter as tk

from ui.login import LoginPage
from ui.theme import setup_theme

if __name__ == "__main__":
    root = tk.Tk()
    setup_theme(root)   # áp dụng style ttk (Primary.TButton, Treeview, ...)
    LoginPage(root)
    root.mainloop()

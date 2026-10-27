# MỘT file cấu hình duy nhất
import os

#  Đường dẫn (luôn tính từ thư mục chứa config.py) 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
LOG_FILE = os.path.join(BASE_DIR, "app.log")

FILE_BENHNHAN = os.path.join(DB_DIR, "data_phongkham.json")   # danh sách bệnh nhân
FILE_BACSI = os.path.join(DB_DIR, "data_bacsi.json")
FILE_LICHKHAM = os.path.join(DB_DIR, "data_lichkham.json")
FILE_LICHLAM = os.path.join(DB_DIR, "data_lichlam.json")
FILE_PHIEUKHAM = os.path.join(DB_DIR, "data_phieukham.json")
FILE_DICHVU_API = os.path.join(DB_DIR, "data_dichvu_crawled.json")
USERS_FILE = os.path.join(DB_DIR, "users.json")

#  Regex 
REGEX_PHONE = r"^0[35789][0-9]{8}$"        # SĐT Việt Nam 10 số
REGEX_BHYT = r"^[A-Z]{2}[0-9]{13}$"        # 2 chữ cái + 13 chữ số
REGEX_EMAIL = r"^[\w\.-]+@[\w\.-]+\.\w+$"

#  Màu Vàng Chanh Pastel 
COLOR_BG = "#FDFBF7"
COLOR_SIDEBAR = "#FEF9C3"
COLOR_PANEL = "#FFFFFF"
COLOR_TEXT = "#1C1917"
COLOR_MUTED = "#713F12"
COLOR_BORDER = "#FEF08A"
COLOR_ACCENT = "#EAB308"
COLOR_ACCENT_PASTEL = "#FEF08A"
COLOR_ACCENT_HOVER = "#CA8A04"

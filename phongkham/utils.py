# utils.py
import csv
import hashlib
import hmac
import logging
import os
import re
import secrets
from datetime import datetime

from config import LOG_FILE, REGEX_BHYT, REGEX_EMAIL, REGEX_PHONE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    encoding="utf-8",
)

_ROUNDS = 120_000


# ---------------- Mật khẩu (PBKDF2 + salt ngẫu nhiên) ----------------
def hash_password(password: str, salt: str = None) -> str:
    """Trả về chuỗi 'salt$hash'. Mỗi mật khẩu có salt riêng."""
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _ROUNDS
    )
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
        return hmac.compare_digest(hash_password(password, salt), stored)
    except (ValueError, AttributeError):
        return False


# ---------------- Nhật ký / phân quyền ----------------
def log_action(username: str, action: str):
    msg = f"Tài khoản '{username}' thực hiện: {action}"
    logging.info(msg)
    print(f"[LOG]: {msg}")


def is_admin(role) -> bool:
    return str(role).lower() == "admin"


# ---------------- Kiểm tra dữ liệu (Regex) ----------------
def validate_phone(phone: str) -> bool:
    return bool(phone) and bool(re.match(REGEX_PHONE, phone.strip()))


def validate_bhyt(bhyt: str) -> bool:
    """BHYT có thể để trống; nếu nhập thì phải đúng định dạng."""
    if not bhyt:
        return True
    return bool(re.match(REGEX_BHYT, bhyt.strip().upper()))


def validate_email(email: str) -> bool:
    """Email có thể để trống; nếu nhập thì phải đúng định dạng."""
    if not email:
        return True
    return bool(re.match(REGEX_EMAIL, email.strip()))


def validate_date(text: str) -> bool:
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ---------------- Xuất file ----------------
def export_to_csv(filename: str, headers: list, data: list, delimiter: str = ";") -> bool:
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(headers)
            writer.writerows(data)
        return True
    except OSError as e:
        logging.error("EXPORT CSV: %s", e)
        return False


def export_invoice_txt(filename: str, content: str) -> bool:
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w", encoding="utf-8") as f:
            f.write(content)
        return True
    except OSError as e:
        logging.error("EXPORT TXT: %s", e)
        return False

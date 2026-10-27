import re
from datetime import datetime

from config import USERS_FILE
from db.storage import read_json, write_json
from utils import hash_password, validate_email, validate_phone, verify_password

MIN_PASSWORD = 6
DEFAULT_DOCTOR_PASSWORD = "123456"      # mật khẩu mặc định cho tài khoản bác sĩ cấp sẵn
REGEX_USERNAME = r"^[A-Za-z0-9_.]{3,20}$"

PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"
STATUS_TEXT = {PENDING: "⏳ Chờ duyệt", APPROVED: "✅ Đã duyệt", REJECTED: "❌ Từ chối"}


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def role_label(info):
    """Nhãn quyền hiển thị: Quản trị viên / Bác sĩ / Người dùng."""
    if str(info.get("role", "")).lower() == "admin":
        return "Quản trị viên"
    if info.get("ma_bs"):
        return "Bác sĩ"
    return "Người dùng"


class AuthService:
    def __init__(self):
        self.users = {}
        self.reload()

    # nạp / lưu
    def reload(self):
        users = read_json(USERS_FILE, None)
        if not isinstance(users, dict) or not users:
            users = {
                "admin": {"password_hash": hash_password("admin123"), "role": "admin",
                          "status": APPROVED, "ho_ten": "Quản trị viên", "ngay_tao": _now()},
            }
            self.users = users
            self._seed_doctor_accounts()
            self._save()
        else:
            self.users = users
            if self._seed_doctor_accounts():
                self._save()

    def _save(self):
        write_json(USERS_FILE, self.users)

    def _seed_doctor_accounts(self):
        """Lần đầu (chưa có tài khoản bác sĩ nào): cấp tài khoản cho các bác sĩ đang có.
        Tên đăng nhập = mã bác sĩ viết thường (bs001...), mật khẩu mặc định DEFAULT_DOCTOR_PASSWORD."""
        if any(u.get("ma_bs") for u in self.users.values()):
            return False
        from db.models import QuanLyPhongKham
        changed = False
        for bs in QuanLyPhongKham().ds_bac_si():
            username = bs["MaBS"].lower()
            if not username or username in self.users:
                continue
            self.users[username] = {
                "password_hash": hash_password(DEFAULT_DOCTOR_PASSWORD),
                "role": "user", "status": APPROVED,
                "ho_ten": bs["HoTen"], "sdt": bs["SoDienThoai"], "email": bs["Email"],
                "ma_bs": bs["MaBS"], "chuyen_khoa": bs["ChuyenKhoa"],
                "ngay_tao": _now(), "nguoi_duyet": "hệ thống",
            }
            changed = True
        return changed

    #  tra cứu
    @staticmethod
    def status_of(info):
        return info.get("status", APPROVED)      # tài khoản cũ chưa có status = đã duyệt

    def get_user(self, username):
        return self.users.get(username)

    def list_users(self):
        """[(username, info)] — chờ duyệt lên đầu, sau đó theo tên."""
        order = {PENDING: 0, APPROVED: 1, REJECTED: 2}
        return sorted(self.users.items(),
                      key=lambda kv: (order.get(self.status_of(kv[1]), 3), kv[0]))

    def count_pending(self):
        return sum(1 for u in self.users.values() if self.status_of(u) == PENDING)

    #  đăng nhập
    def login(self, username, password):
        """Trả về (kết quả, role): kết quả là 'ok' | 'pending' | 'rejected' | 'fail'."""
        info = self.users.get(username)
        if not info or not verify_password(password, info.get("password_hash", "")):
            return "fail", None
        status = self.status_of(info)
        if status == PENDING:
            return "pending", None
        if status == REJECTED:
            return "rejected", None
        return "ok", info.get("role", "user")

    def authenticate(self, username, password):
        """Giữ tương thích: trả về role nếu đăng nhập được, ngược lại None."""
        result, role = self.login(username, password)
        return role if result == "ok" else None

    #  đăng ký / duyệt
    def register(self, username, password, ho_ten, gioi_tinh, sdt, email):
        """Tạo tài khoản ở trạng thái CHỜ DUYỆT. Bắt buộc nhập đầy đủ thông tin."""
        username, ho_ten, sdt, email = (username or "").strip(), (ho_ten or "").strip(), \
            (sdt or "").strip(), (email or "").strip()
        if not all([username, password, ho_ten, gioi_tinh, sdt, email]):
            return False, "Vui lòng nhập đầy đủ tất cả thông tin!"
        if not re.match(REGEX_USERNAME, username):
            return False, "Tên đăng nhập 3-20 ký tự, chỉ gồm chữ, số, dấu _ hoặc ."
        old = self.users.get(username)
        if old and self.status_of(old) != REJECTED:
            return False, "Tài khoản này đã tồn tại!"
        if len(password) < MIN_PASSWORD:
            return False, f"Mật khẩu tối thiểu {MIN_PASSWORD} ký tự!"
        if not validate_phone(sdt):
            return False, "Số điện thoại không hợp lệ (10 số, bắt đầu 03/05/07/08/09)!"
        if not validate_email(email):
            return False, "Email không đúng định dạng!"
        self.users[username] = {
            "password_hash": hash_password(password), "role": "user", "status": PENDING,
            "ho_ten": ho_ten, "gioi_tinh": gioi_tinh, "sdt": sdt, "email": email,
            "ngay_tao": _now(),
        }
        self._save()
        return True, "OK"

    def set_status(self, username, status, admin_name):
        info = self.users.get(username)
        if not info:
            return False, "Không tìm thấy tài khoản!"
        if str(info.get("role")).lower() == "admin":
            return False, "Không thể thay đổi trạng thái tài khoản quản trị!"
        info["status"] = status
        info["nguoi_duyet"] = admin_name
        info["ngay_duyet"] = _now()
        self._save()
        return True, "OK"

    def delete_user(self, username, admin_name):
        """Xóa tài khoản (không xóa được tài khoản quản trị hoặc chính mình)."""
        info = self.users.get(username)
        if not info:
            return False, "Không tìm thấy tài khoản!"
        if str(info.get("role")).lower() == "admin":
            return False, "Không thể xóa tài khoản quản trị!"
        if username == admin_name:
            return False, "Không thể tự xóa tài khoản đang đăng nhập!"
        del self.users[username]
        self._save()
        return True, "OK"

    def change_password(self, username, old_password, new_password):
        if self.authenticate(username, old_password) is None:
            return False, "Tên tài khoản hoặc mật khẩu cũ không đúng!"
        if len(new_password) < MIN_PASSWORD:
            return False, f"Mật khẩu mới tối thiểu {MIN_PASSWORD} ký tự!"
        self.users[username]["password_hash"] = hash_password(new_password)
        self._save()
        return True, "OK"

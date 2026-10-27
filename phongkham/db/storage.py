# db/storage.py  -- đọc/ghi JSON an toàn (một nơi duy nhất)
import json
import os
import shutil
import tempfile
from datetime import datetime

MAX_BACKUPS = 10   # số bản sao lưu giữ lại cho mỗi file


def read_json(path, default=None):
    """Đọc JSON. File chưa có -> default. File hỏng -> đổi tên .corrupt rồi trả default."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except (json.JSONDecodeError, OSError) as e:
        print(f"[STORAGE] File lỗi {path}: {e}")
        try:
            os.replace(path, path + ".corrupt")
        except OSError:
            pass
        return default


def _backup(path):
    """Chép file hiện tại vào <thư mục>/backup/ trước khi bị ghi đè, giữ MAX_BACKUPS bản mới nhất."""
    if not os.path.exists(path):
        return
    try:
        folder = os.path.join(os.path.dirname(path), "backup")
        os.makedirs(folder, exist_ok=True)
        name = os.path.basename(path)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shutil.copy2(path, os.path.join(folder, f"{name}.{stamp}.bak"))
        olds = sorted(f for f in os.listdir(folder) if f.startswith(name + "."))
        for f in olds[:-MAX_BACKUPS]:
            os.remove(os.path.join(folder, f))
    except OSError as e:           # sao lưu lỗi thì không được làm hỏng thao tác lưu chính
        print(f"[STORAGE] Không sao lưu được {path}: {e}")


def write_json(path, data):
    """Sao lưu bản cũ, rồi ghi qua file tạm và thay thế để tránh hỏng file khi bị tắt giữa chừng."""
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    _backup(path)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

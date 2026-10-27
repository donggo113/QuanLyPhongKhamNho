import requests

from config import FILE_DICHVU_API
from db.storage import write_json


class DataCrawler:
    URL = "https://jsonplaceholder.typicode.com/posts"

    def __init__(self, db_path=FILE_DICHVU_API):
        self.db_path = db_path

    def crawl_or_fetch_api_data(self):
        """Lấy dữ liệu từ API công khai, làm sạch rồi lưu JSON. Trả về (ok, thông báo)."""
        try:
            response = requests.get(self.URL, timeout=5)
            if response.status_code != 200:
                return False, f"Máy chủ phản hồi mã lỗi: {response.status_code}"

            cleaned = []
            for idx, item in enumerate(response.json()[:10]):
                cleaned.append({
                    "ma_dv": f"DV_API_{idx + 1:02d}",
                    "ten_dich_vu": f"Dịch vụ Y tế {item['title'][:20].title()}",
                    "don_gia": (idx + 1) * 50000 + 100000,
                    "nguon": "API External Database",
                })
            write_json(self.db_path, cleaned)
            return True, f"Đã đồng bộ {len(cleaned)} dịch vụ từ API!"
        except requests.exceptions.Timeout:
            return False, "Lỗi: Kết nối API vượt quá thời gian chờ (Timeout)."
        except requests.exceptions.RequestException as e:
            return False, f"Lỗi kết nối mạng hoặc không thể gọi API: {e}"
        except (KeyError, ValueError, OSError) as e:
            return False, f"Lỗi xử lý dữ liệu: {e}"

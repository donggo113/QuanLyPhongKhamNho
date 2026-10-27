# seed_sample.py  -- python seed_sample.py  (thêm mẫu) | python seed_sample.py --xoa
# (Có thể dùng nút "Nạp số liệu mẫu" ngay trên Dashboard thay cho lệnh này.)
import sys

from services.sample_data import them_mau, xoa_mau

if "--xoa" in sys.argv:
    print(f"Đã xóa {xoa_mau()} phiếu mẫu.")
else:
    print(them_mau()[1])

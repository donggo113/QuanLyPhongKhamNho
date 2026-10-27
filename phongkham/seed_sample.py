import sys

from services.sample_data import them_mau, xoa_mau

if "--xoa" in sys.argv:
    print(f"Đã xóa {xoa_mau()} phiếu mẫu.")
else:
    print(them_mau()[1])

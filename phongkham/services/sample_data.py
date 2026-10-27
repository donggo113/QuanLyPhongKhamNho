import random
from datetime import date

from config import FILE_PHIEUKHAM
from db.models import PhieuKhamBenh, QuanLyPhongKham
from db.storage import write_json

PREFIX = "PKM"
DICH_VU = [   # giống danh sách dịch vụ mặc định trong app
    ("Khám Nội Tổng Quát", 150000), ("Xét Nghiệm Máu", 100000),
    ("Siêu Âm Tổng Quát", 200000), ("Chụp X-Quang", 180000),
]
CHAN_DOAN = [
    ("Ho, sốt nhẹ", "Viêm họng cấp"), ("Đau đầu, mệt mỏi", "Thiếu ngủ"),
    ("Đau bụng", "Viêm dạ dày"), ("Khám định kỳ", "Sức khỏe bình thường"),
    ("Đau lưng", "Thoái hóa cột sống"),
]
# số phiếu mẫu 
SO_PHIEU = [6, 9, 8, 12, 15, 11]


def thang_gan_nhat(n=6):
    today = date.today()
    y, m = today.year, today.month
    out = []
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return out[::-1]



def co_so_lieu_mau():
    return any(str(x.get("MaPK", "")).startswith(PREFIX)
               for x in QuanLyPhongKham().ds_phieu_kham())


def xoa_mau():
    ql = QuanLyPhongKham()
    hien_co = ql.ds_phieu_kham()
    giu_lai = [x for x in hien_co if not str(x.get("MaPK", "")).startswith(PREFIX)]
    write_json(FILE_PHIEUKHAM, giu_lai)
    return len(hien_co) - len(giu_lai)


def them_mau():
    """Thay số liệu mẫu cũ bằng bộ mới. Trả về (ok, thông báo)."""
    ql = QuanLyPhongKham()
    benh_nhan, bac_si = ql.ds_benh_nhan(), ql.ds_bac_si()
    if not benh_nhan or not bac_si:
        return False, "Cần có ít nhất 1 bệnh nhân và 1 bác sĩ trước khi thêm số liệu mẫu."
    xoa_mau()
    giu_lai = ql.ds_phieu_kham()

    rnd = random.Random(2026)
    today = date.today()
    moi, stt = [], 1
    for (y, m), so in zip(thang_gan_nhat(), SO_PHIEU):
        ngay_toi_da = today.day if (y, m) == (today.year, today.month) else 28
        for _ in range(so):
            bn, bs = rnd.choice(benh_nhan), rnd.choice(bac_si)
            tc, cd = rnd.choice(CHAN_DOAN)
            dich_vu = [{"ten_dv": t, "gia": g, "so_luong": 1}
                       for t, g in rnd.sample(DICH_VU, rnd.randint(1, 3))]
            ngay = date(y, m, rnd.randint(1, max(ngay_toi_da, 1)))
            da_tt = not ((y, m) == (today.year, today.month) and rnd.random() < 0.3)
            moi.append(PhieuKhamBenh(
                f"{PREFIX}{stt:03d}", bn["MaBN"], bn["HoTen"], bs["MaBS"], bs["HoTen"],
                ngay.isoformat(), tc, cd, dich_vu,
                "Đã thanh toán" if da_tt else "Chờ duyệt", "admin").to_dict())
            stt += 1
    write_json(FILE_PHIEUKHAM, giu_lai + moi)
    return True, f"Đã thêm {len(moi)} phiếu khám mẫu (6 tháng gần nhất)."

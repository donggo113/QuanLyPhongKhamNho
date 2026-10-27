# db/models.py  -- lớp dữ liệu + QuanLyPhongKham (nguồn dữ liệu duy nhất cho mọi màn hình)
from datetime import date

from config import (
    FILE_BACSI, FILE_BENHNHAN, FILE_LICHKHAM, FILE_LICHLAM, FILE_PHIEUKHAM,
)
from db.storage import read_json, write_json


def _get(d, *keys, default=""):
    """Lấy giá trị theo nhiều tên khóa (hỗ trợ cả khóa cũ dạng snake_case)."""
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return default


# =====================================================================
#  CÁC LỚP ĐỐI TƯỢNG
# =====================================================================
class BenhNhan:
    def __init__(self, ma_bn, ho_ten, sdt, gioi_tinh="Nam", tuoi="",
                 bhyt="", dia_chi="Chưa cập nhật", tien_su="Không"):
        self.ma_bn = ma_bn
        self.ho_ten = ho_ten
        self.sdt = sdt
        self.gioi_tinh = gioi_tinh
        self.tuoi = tuoi
        self.bhyt = bhyt
        self.dia_chi = dia_chi
        self.tien_su = tien_su

    def to_dict(self):
        return {
            "MaBN": self.ma_bn, "HoTen": self.ho_ten, "Tuoi": self.tuoi,
            "GioiTinh": self.gioi_tinh, "SoDienThoai": self.sdt,
            "BHYT": self.bhyt, "DiaChi": self.dia_chi, "TienSu": self.tien_su,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ma_bn=_get(d, "MaBN", "ma_id"),
            ho_ten=_get(d, "HoTen", "ho_ten"),
            sdt=_get(d, "SoDienThoai", "sdt"),
            gioi_tinh=_get(d, "GioiTinh", "gioi_tinh", default="Nam"),
            tuoi=_get(d, "Tuoi", "tuoi"),
            bhyt=_get(d, "BHYT", "bhyt"),
            dia_chi=_get(d, "DiaChi", "dia_chi", default="Chưa cập nhật"),
            tien_su=_get(d, "TienSu", "tien_su", default="Không"),
        )


class BacSi:
    def __init__(self, ma_bs, ho_ten, chuyen_khoa, sdt, email=""):
        self.ma_bs = ma_bs
        self.ho_ten = ho_ten
        self.chuyen_khoa = chuyen_khoa
        self.sdt = sdt
        self.email = email

    def to_dict(self):
        return {
            "MaBS": self.ma_bs, "HoTen": self.ho_ten,
            "ChuyenKhoa": self.chuyen_khoa, "SoDienThoai": self.sdt,
            "Email": self.email,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ma_bs=_get(d, "MaBS", "ma_bs"),
            ho_ten=_get(d, "HoTen", "ho_ten"),
            chuyen_khoa=_get(d, "ChuyenKhoa", "chuyen_khoa"),
            sdt=_get(d, "SoDienThoai", "sdt"),
            email=_get(d, "Email", "email"),
        )


class LichKham:
    def __init__(self, ma_bs, ten_bs, ma_bn, ten_bn, ngay, gio):
        self.ma_bs, self.ten_bs = ma_bs, ten_bs
        self.ma_bn, self.ten_bn = ma_bn, ten_bn
        self.ngay, self.gio = ngay, gio

    def to_dict(self):
        return {
            "MaBS": self.ma_bs, "BacSi": self.ten_bs,
            "MaBN": self.ma_bn, "BenhNhan": self.ten_bn,
            "NgayKham": self.ngay, "GioKham": self.gio,
        }


class PhieuKhamBenh:
    """dich_vu: list các dict {"ten_dv", "gia", "so_luong"}"""

    def __init__(self, ma_pk, ma_bn, ten_bn, ma_bs, ten_bs, ngay_kham,
                 trieu_chung, chan_doan, dich_vu=None,
                 trang_thai="Chờ duyệt", nguoi_tao=""):
        self.ma_pk = ma_pk
        self.ma_bn, self.ten_bn = ma_bn, ten_bn
        self.ma_bs, self.ten_bs = ma_bs, ten_bs
        self.ngay_kham = ngay_kham
        self.trieu_chung = trieu_chung
        self.chan_doan = chan_doan
        self.dich_vu = dich_vu or []
        self.trang_thai = trang_thai
        self.nguoi_tao = nguoi_tao

    @property
    def tong_tien(self):
        return sum(dv["gia"] * dv["so_luong"] for dv in self.dich_vu)

    def to_dict(self):
        return {
            "MaPK": self.ma_pk, "MaBN": self.ma_bn, "BenhNhan": self.ten_bn,
            "MaBS": self.ma_bs, "BacSi": self.ten_bs,
            "NgayKham": self.ngay_kham, "TrieuChung": self.trieu_chung,
            "ChanDoan": self.chan_doan, "DichVu": self.dich_vu,
            "TongTien": self.tong_tien, "TrangThai": self.trang_thai,
            "NguoiTao": self.nguoi_tao,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            ma_pk=d.get("MaPK", ""), ma_bn=d.get("MaBN", ""),
            ten_bn=d.get("BenhNhan", ""), ma_bs=d.get("MaBS", ""),
            ten_bs=d.get("BacSi", ""), ngay_kham=d.get("NgayKham", ""),
            trieu_chung=d.get("TrieuChung", ""), chan_doan=d.get("ChanDoan", ""),
            dich_vu=d.get("DichVu", []), trang_thai=d.get("TrangThai", "Chờ duyệt"),
            nguoi_tao=d.get("NguoiTao", ""),
        )

    def to_invoice_text(self):
        w = 66
        out = ["=" * w, "HÓA ĐƠN KHÁM BỆNH".center(w), "=" * w,
               f"Mã phiếu  : {self.ma_pk}",
               f"Ngày khám : {self.ngay_kham}",
               f"Bệnh nhân : {self.ma_bn} - {self.ten_bn}",
               f"Bác sĩ    : {self.ma_bs} - {self.ten_bs}",
               f"Chẩn đoán : {self.chan_doan}",
               f"Nội dung  : {self.trieu_chung or '(không có)'}",
               "-" * w,
               f"{'STT':<4}{'Dịch vụ':<32}{'SL':>4}{'Đơn giá':>12}{'Thành tiền':>14}",
               "-" * w]
        for i, dv in enumerate(self.dich_vu, 1):
            tt = dv["gia"] * dv["so_luong"]
            out.append(
                f"{i:<4}{dv['ten_dv'][:30]:<32}{dv['so_luong']:>4}{dv['gia']:>12,}{tt:>14,}"
            )
        out += ["-" * w, f"TỔNG CỘNG: {self.tong_tien:,} VNĐ".rjust(w),
                f"Trạng thái: {self.trang_thai}", f"Người lập : {self.nguoi_tao}",
                "=" * w]
        return "\n".join(out) + "\n"


# =====================================================================
#  DỮ LIỆU MẪU (chỉ nạp khi file CHƯA TỒN TẠI)
# =====================================================================
SEED_BENH_NHAN = [
    BenhNhan("BN001", "Nguyễn Văn An", "0912345678", "Nam", 35, "", "Hà Nội"),
    BenhNhan("BN002", "Trần Thị Bích", "0987654321", "Nữ", 28, "", "TP.HCM"),
]
SEED_BAC_SI = [
    BacSi("BS001", "PGS.TS Nguyễn Văn Bình", "Nội Tổng Quát", "0901234567", "binh.nguyen@phongkham.vn"),
    BacSi("BS002", "ThS.BS Trần Thị Mai", "Tai Mũi Họng", "0902345678", "mai.tran@phongkham.vn"),
    BacSi("BS003", "BS.CKII Lê Hoàng Nam", "Chẩn Đoán Hình Ảnh", "0903456789", "nam.le@phongkham.vn"),
    BacSi("BS004", "BS.CKI Phạm Thanh Hà", "Nhi Khoa", "0904567890", "ha.pham@phongkham.vn"),
    BacSi("BS005", "ThS.BS Đỗ Văn Khoa", "Tim Mạch", "0905678901", "khoa.do@phongkham.vn"),
    BacSi("BS006", "BS.CKI Nguyễn Thị Lan", "Da Liễu", "0906789012", "lan.nguyen@phongkham.vn"),
]


# =====================================================================
#  QUẢN LÝ PHÒNG KHÁM -- mọi màn hình đọc/ghi qua lớp này
# =====================================================================
class QuanLyPhongKham:
    # ---------- Bệnh nhân ----------
    def ds_benh_nhan(self):
        raw = read_json(FILE_BENHNHAN, None)
        if raw is None:  # chưa có file -> nạp mẫu
            ds = [b.to_dict() for b in SEED_BENH_NHAN]
            write_json(FILE_BENHNHAN, ds)
            return ds
        if isinstance(raw, dict):  # tương thích file cũ do models.py ghi
            raw = raw.get("benh_nhan") or raw.get("danh_sach_benh_nhan") or []
        if not isinstance(raw, list):
            raw = []
        return [BenhNhan.from_dict(x).to_dict() for x in raw if isinstance(x, dict)]

    def luu_benh_nhan(self, ds):
        write_json(FILE_BENHNHAN, ds)

    def benh_nhan_co_du_lieu(self, ma_bn):
        """True nếu bệnh nhân đã có lịch khám hoặc phiếu khám (không nên xóa)."""
        return any(x.get("MaBN") == ma_bn for x in self.ds_lich_kham()) or any(
            x.get("MaBN") == ma_bn for x in self.ds_phieu_kham()
        )

    # ---------- Bác sĩ ----------
    def ds_bac_si(self):
        raw = read_json(FILE_BACSI, None)
        if raw is None:
            ds = [b.to_dict() for b in SEED_BAC_SI]
            write_json(FILE_BACSI, ds)
            return ds
        if not isinstance(raw, list):
            raw = []
        return [BacSi.from_dict(x).to_dict() for x in raw if isinstance(x, dict)]

    def luu_bac_si(self, ds):
        write_json(FILE_BACSI, ds)

    def bac_si_con_lich(self, ma_bs):
        """True nếu bác sĩ còn lịch hẹn từ hôm nay trở đi."""
        hom_nay = date.today().isoformat()
        return any(
            x.get("MaBS") == ma_bs and x.get("NgayKham", "") >= hom_nay
            for x in self.ds_lich_kham()
        )

    # ---------- Lịch khám ----------
    def ds_lich_kham(self):
        raw = read_json(FILE_LICHKHAM, [])
        return [x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []

    def kiem_tra_trung_lich_bac_si(self, ma_bs, ngay, gio):
        return any(
            x.get("MaBS") == ma_bs and x.get("NgayKham") == ngay and x.get("GioKham") == gio
            for x in self.ds_lich_kham()
        )

    def dat_lich(self, lich: LichKham):
        """Thêm lịch hẹn. Ném ValueError nếu trùng lịch bác sĩ / bệnh nhân."""
        ds = self.ds_lich_kham()
        for x in ds:
            if x.get("NgayKham") == lich.ngay and x.get("GioKham") == lich.gio:
                if x.get("MaBS") == lich.ma_bs:
                    raise ValueError(
                        f"Bác sĩ {lich.ten_bs} đã có lịch lúc {lich.gio} ngày {lich.ngay}.\n"
                        "Vui lòng chọn giờ hoặc bác sĩ khác."
                    )
                if lich.ma_bn and x.get("MaBN") == lich.ma_bn:
                    raise ValueError(
                        f"Bệnh nhân {lich.ten_bn} đã có lịch khác lúc {lich.gio} ngày {lich.ngay}."
                    )
        ds.append(lich.to_dict())
        write_json(FILE_LICHKHAM, ds)

    # ---------- Phiếu khám ----------
    def ds_phieu_kham(self):
        raw = read_json(FILE_PHIEUKHAM, [])
        return [x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []

    def tao_ma_phieu(self):
        so = [int(x["MaPK"][2:]) for x in self.ds_phieu_kham()
              if str(x.get("MaPK", "")).startswith("PK") and str(x["MaPK"][2:]).isdigit()]
        return f"PK{max(so, default=0) + 1:03d}"

    def them_phieu_kham(self, phieu: PhieuKhamBenh):
        ds = self.ds_phieu_kham()
        ds.append(phieu.to_dict())
        write_json(FILE_PHIEUKHAM, ds)

    def duyet_thanh_toan(self, ma_pk):
        ds = self.ds_phieu_kham()
        for x in ds:
            if x.get("MaPK") == ma_pk:
                x["TrangThai"] = "Đã thanh toán"
                write_json(FILE_PHIEUKHAM, ds)
                return True
        return False

    # ---------- Lịch làm việc ----------
    def ds_lich_lam(self):
        raw = read_json(FILE_LICHLAM, [])
        return [x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []

    def luu_lich_lam(self, ds):
        write_json(FILE_LICHLAM, ds)

    # ---------- Thống kê thật cho Dashboard ----------
    def thong_ke(self):
        today = date.today()
        hom_nay = today.isoformat()
        phieu = self.ds_phieu_kham()

        thang = []  # 6 tháng gần nhất (cũ -> mới)
        y, m = today.year, today.month
        for _ in range(6):
            thang.append((y, m))
            m -= 1
            if m == 0:
                m, y = 12, y - 1
        thang.reverse()

        luot = {f"{y:04d}-{m:02d}": 0 for y, m in thang}
        thu = {k: 0 for k in luot}
        for pk in phieu:
            key = str(pk.get("NgayKham", ""))[:7]
            if key in luot:
                luot[key] += 1
                if pk.get("TrangThai") == "Đã thanh toán":
                    thu[key] += int(pk.get("TongTien", 0) or 0)

        key_now = f"{today.year:04d}-{today.month:02d}"
        return {
            "tong_benh_nhan": len(self.ds_benh_nhan()),
            "lich_hom_nay": sum(1 for x in self.ds_lich_kham() if x.get("NgayKham") == hom_nay),
            "da_kham_hom_nay": sum(1 for x in phieu if x.get("NgayKham") == hom_nay),
            "doanh_thu_thang": thu[key_now],
            "luot_kham": [(f"T{m}", luot[f"{y:04d}-{m:02d}"]) for y, m in thang],
            "doanh_thu": [(f"T{m}", round(thu[f"{y:04d}-{m:02d}"] / 1_000_000, 2)) for y, m in thang],
        }

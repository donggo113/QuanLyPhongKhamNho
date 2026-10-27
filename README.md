## 🏥 Hệ Thống Quản Lý Phòng Khám

Ứng dụng desktop hỗ trợ quản lý phòng khám tư nhân toàn diện, được viết bằng ngôn ngữ **Python** kết hợp với giao diện **Tkinter (GUI)** chuẩn phong cách thiết kế **Soft Pastel Lemon** (Vàng Chanh Pastel).


## 🌟 Các Tính năng chính

1. **🔒 Đăng nhập & Mã hóa hệ thống:**
   - Phân quyền tài khoản Quản trị (Admin) và Nhân viên (User).
   - Bảo mật mật khẩu người dùng theo chuẩn thuật toán mã hóa SHA-256.
   - Ghi lại vết hoạt động (Action Logging) tự động vào file `app.log`.

2. **📊 Bảng điều khiển (Dashboard):**
   - Thống kê tổng quan lượt khám, bệnh nhân và doanh thu.
   - Trực quan hóa dữ liệu bằng biểu đồ cột Canvas tùy chỉnh linh hoạt.

3. **👤 Quản lý Hồ sơ Bệnh nhân & Bác sĩ:**
   - Thêm, sửa, xóa, tìm kiếm bệnh nhân và danh sách bác sĩ chuyên khoa.
   - Kiểm tra định dạng dữ liệu đầu vào (Regex Số điện thoại Việt Nam, thẻ BHYT).

4. **📑 Đăng ký & Đặt lịch khám:**
   - Đặt lịch hẹn khám bệnh tránh trùng lặp.
   - Xuất danh sách báo cáo lịch hẹn ra định dạng file CSV chuẩn (mã hóa UTF-8-sig chống lỗi font Excel).

5. **🩺 Chẩn đoán & Chỉ định Dịch vụ y tế:**
   - Ghi nhận chẩn đoán bệnh, kê dịch vụ khám và tự động tính tổng tiền.
   - Duyệt thanh toán và quản lý phiếu khám cho bệnh nhân.
   - Đồng bộ danh mục dịch vụ y tế mẫu từ API bên ngoài (`DataCrawler`).

6. **📅 Quản lý Lịch làm việc (Shift Schedule):**
   - Nhân viên đăng ký ca làm (Sáng, Chiều, Tối).
   - Admin duyệt/từ chối lịch làm của từng nhân viên.

---

## 📁 Cấu trúc thư mục dự án

```text
├── db/                         # Thư mục lưu trữ dữ liệu JSON & Báo cáo
│   ├── data_phongkham.json     # Dữ liệu chính (bệnh nhân, bác sĩ, dịch vụ...)
│   ├── data_bacsi.json         # Danh sách bác sĩ
│   ├── data_lichkham.json      # Lịch hẹn khám bệnh
│   ├── data_lichlam.json       # Lịch ca làm việc
│   └── data_dichvu_crawled.json# Dữ liệu dịch vụ lấy từ API
├── ui/                         # Các màn hình giao diện người dùng (GUI)
│   ├── __init__.py
│   ├── login.py                # Màn hình Đăng nhập / Đăng ký
│   ├── base.py                 # Màn hình khung AppShell & Thanh Menu
│   ├── dashboard.py            # Bảng tổng quan & Biểu đồ
│   ├── components.py           # Quản lý bệnh nhân (DataView)
│   ├── quanlybacsi.py          # Quản lý bác sĩ
│   ├── dangkylichkham.py       # Đặt lịch khám & Xuất CSV
│   ├── khambenh_dichvu.py      # Kê phiếu khám & Duyệt thanh toán
│   ├── phanlichlam.py          # Đăng ký & Duyệt ca làm
│   ├── forms.py                # Form Dialog hỗ trợ nhập liệu
│   ├── theme.py                # Định dạng Style màu sắc Pastel
│   └── widgets.py              # Các tùy biến Button/Widget
├── api_crawler.py              # Module cào/đồng bộ dữ liệu từ API
├── config.py                   # Cấu hình hằng số, màu sắc, Regex
├── models.py                   # Lớp đối tượng (BenhNhan, BacSi, PhieuKham...)
├── utils.py                    # Ghi Log, Validation Regex, SHA-256, Export
├── main.py                     # File chạy chính của ứng dụng
├── app.log                     # Nhật ký hoạt động hệ thống
└── README.md                   # Tài liệu hướng dẫn sử dụng

```

---

## ⚙️ Hướng dẫn Cài đặt & Chạy ứng dụng

### Bước 1: Cài đặt thư viện trực tiếp bằng Command Prompt (CMD)

1. Mở cửa sổ **Command Prompt (CMD)** trên laptop.
2. Chạy lệnh cài đặt các thư viện phụ thuộc trực tiếp vào hệ thống:
```cmd
pip install requests tkcalendar spyder

```
hoặc chạy lệnh này nếu trên không được
```cmd
pip install tkcalendar requests pyinstaller streamlit pandas matplotlib seaborn statsmodels pyfim
```

### Bước 2: Cấu hình Trình biên dịch Python (Python Interpreter) trong Spyder
Để Spyder nhận diện đúng phiên bản Python hệ thống và các thư viện vừa cài đặt qua CMD:

1. Mở phần mềm Spyder.

2. Chọn thanh menu Tools ➔ Preferences (hoặc nhấn Ctrl + Shift + P).

3. Chọn mục Python interpreter ở danh sách bên trái.

4. Tích chọn vào mục Selected interpreter:

5. Bấm vào biểu tượng thư mục (folder) bên cạnh đường dẫn và chọn đến file python.exe của máy (Ví dụ: C:\Program Files\Python313\python.exe hoặc đường dẫn cài Python tương ứng trên máy bạn).

6. Nhấn Apply ➔ OK.

7. Khởi động lại Console bằng cách nhấn tổ hợp phím Ctrl + . (hoặc nhấp chuột vào biểu tượng 3 dấu gạch ở khung IPython Console ➔ chọn Restart kernel).
8. Ảnh Minh Họa
<img width="901" height="693" alt="image" src="https://github.com/user-attachments/assets/c6b3b1c6-a0bb-4b09-a40a-d879f0e0df96" />

---

### Bước 3: Mở dự án & Chạy phần mềm

1. Trong cửa sổ Spyder, chọn menu **Projects** ➔ **New Project...**
2. Chọn tùy chọn **Existing directory**, bấm **Browse...** tìm đến thư mục code dự án của bạn ➔ Bấm **Create**.
3. Tại ô quản lý file phía bên trái, nhấp đôi chuột vào file **`main.py`** để mở file.
4. Nhấn phím **`F5`** (hoặc bấm nút Play màu xanh lá trên thanh công cụ) để chạy chương trình.

---

## 🚀 Tài khoản đăng nhập mẫu

Hệ thống có sẵn 2 tài khoản thử nghiệm để bạn kiểm tra các phân quyền:

| Quyền hạn | Tên đăng nhập | Mật khẩu | Tính năng chính |
| --- | --- | --- | --- |
| **Quản trị viên (Admin)** | `admin` | `admin123` | Toàn quyền: Duyệt thanh toán, xóa hồ sơ, duyệt ca làm. |
| **Bác sĩ / Nhân viên** | `bac` | `123456` | Quyền giới hạn: Xem dữ liệu, đăng ký ca làm, tạo phiếu khám. |

*(Bạn cũng có thể bấm vào nút **"TẠO TÀI KHOẢN"** ngay tại giao diện Đăng nhập để tạo thêm tài khoản mới).*

---

## 🛠️ Công nghệ sử dụng

* **Môi trường phát triển (IDE):** Spyder
* **Ngôn ngữ:** Python 3.x
* **Giao diện:** Tkinter & `ttk` (Custom Soft Pastel Lemon Theme)
* **Cơ sở dữ liệu:** Lưu trữ dạng file JSON (`db/*.json`)
* **Mã hóa:** SHA-256 (`hashlib`)
* **Công cụ bổ trợ:** Python Logging (`logging`), Regular Expressions (`re`), REST API (`requests`).

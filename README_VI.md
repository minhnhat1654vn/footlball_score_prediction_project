# Hệ Thống Dự Đoán Kết Quả Bóng Đá

Ứng dụng web dự đoán kết quả trận đấu bóng đá sử dụng machine learning, với các tính năng thống kê đội bóng, dự đoán trận đấu và quản lý đội bóng yêu thích.

## Tính Năng

### Tính Năng Chính
- **Dự Đoán Trận Đấu**: Dự đoán kết quả các trận đấu sắp tới sử dụng mô hình machine learning
- **Thống Kê Đội Bóng**: Xem thống kê chi tiết của các đội bóng bao gồm:
  - Số trận thắng, hòa, thua
  - Vị trí trên bảng xếp hạng
  - Điểm số
  - Số bàn thắng/bàn thua
  - Hiệu số bàn thắng
- **Đội Bóng Yêu Thích**: 
  - Lưu đội bóng yêu thích để truy cập nhanh
  - Xem thống kê chi tiết của đội bóng yêu thích
  - Điều hướng nhanh giữa trang chủ và phần yêu thích

### Giao Diện Người Dùng
- **Thiết Kế Hiện Đại**: Giao diện sạch sẽ và trực quan
- **Hỗ Trợ Chế Độ Tối**: Tích hợp đầy đủ chế độ tối để trải nghiệm tốt hơn
- **Giao Diện Đáp Ứng**: Hoạt động tốt trên cả máy tính và thiết bị di động
- **Phần Tử Tương Tác**: 
  - Card đội bóng có thể click
  - Điều hướng tab mượt mà
  - Tải nội dung động

### Tính Năng Kỹ Thuật
- **Hệ Thống Cache**: Cache dữ liệu hiệu quả để giảm số lần gọi API
- **Cập Nhật Thời Gian Thực**: Dữ liệu trận đấu và thống kê trực tiếp
- **Lưu Trữ Bền Vững**: Lưu đội bóng yêu thích qua các phiên
- **Tích Hợp API**: Kết nối mượt mà với các API dữ liệu bóng đá

## Cài Đặt

1. Clone repository:
```bash
git clone https://github.com/yourusername/football-prediction-system.git
cd football-prediction-system
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Thiết lập biến môi trường:
Tạo file `.env` trong thư mục gốc với các biến sau:
```
API_KEY=your_api_key_here
FLASK_ENV=development
```

5. Chạy ứng dụng:
```bash
python app.py
```

6. Giải nén dữ liệu trận đấu:
- Tải xuống và giải nén file `data.rar` để lấy dữ liệu trận đấu
- Đặt các file đã giải nén vào thư mục gốc của dự án:
  - `database.sqlite`: Chứa lịch sử trận đấu và dữ liệu đội bóng
  - `Datasets/`: Chứa thống kê chi tiết các trận đấu từ mùa 2000-2016

## Cấu Trúc Dự Án

```
football-prediction-system/
├── app.py                 # File ứng dụng chính
├── requirements.txt       # Danh sách thư viện
├── .env                  # Biến môi trường
├── static/              # File tĩnh
│   ├── css/            # File CSS
│   ├── js/             # File JavaScript
│   └── images/         # Hình ảnh
├── templates/          # Template HTML
│   ├── matches/       # Template liên quan đến trận đấu
│   └── components/    # Component tái sử dụng
├── models/            # Mô hình machine learning
├── utils/            # Hàm tiện ích
└── cache/            # Bộ nhớ cache
```

## Hướng Dẫn Sử Dụng

1. **Trang Chủ**
   - Xem các đội bóng nổi bật
   - Truy cập dự đoán nhanh
   - Điều hướng đến các phần khác nhau

2. **Yêu Thích**
   - Thêm/xóa đội bóng yêu thích
   - Xem thống kê chi tiết đội bóng
   - Truy cập nhanh thông tin đội bóng

3. **Trận Đấu**
   - Xem các trận đấu sắp tới
   - Xem dự đoán trận đấu
   - Truy cập dữ liệu lịch sử

4. **Bảng Xếp Hạng**
   - Xem bảng xếp hạng giải đấu
   - Theo dõi thành tích đội bóng
   - So sánh thống kê đội bóng

## Chi Tiết Kỹ Thuật

### Backend
- Framework web Flask
- Tích hợp API RESTful
- Hệ thống cache để tối ưu hiệu suất
- Tích hợp mô hình machine learning

### Frontend
- HTML5/CSS3
- JavaScript cho nội dung động
- Thiết kế đáp ứng
- Hỗ trợ chế độ tối

### Quản Lý Dữ Liệu
- Lưu trữ bền vững cho đội bóng yêu thích
- Hệ thống cache hiệu quả
- Cập nhật dữ liệu thời gian thực

## Đóng Góp

1. Fork repository
2. Tạo nhánh tính năng của bạn (`git checkout -b feature/TinhNangMoi`)
3. Commit các thay đổi (`git commit -m 'Thêm tính năng mới'`)
4. Push lên nhánh (`git push origin feature/TinhNangMoi`)
5. Tạo Pull Request

## Giấy Phép

Dự án này được cấp phép theo MIT License - xem file LICENSE để biết thêm chi tiết.

## Lời Cảm Ơn

- Các nhà cung cấp API dữ liệu bóng đá
- Cộng đồng mã nguồn mở
- Các nhà đóng góp và bảo trì 
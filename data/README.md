# Bộ ảnh Ngày 2

`day2-cvat-input.zip` chứa bốn ảnh giao thông 640 × 640 điểm ảnh. Đây là tệp được cấp sẵn để tải trực tiếp lên
CVAT; sổ thực hành không tạo hoặc tải ảnh.

Các bản ảnh rời trong `cvat-input/` được lưu để kiểm mã SHA-256. Tệp `image-manifest.csv` ghi tên ảnh, kích
thước, phân chia huấn luyện/thẩm định và nguồn dữ liệu. Kho mã không chứa nhãn tham chiếu hoặc số lượng vật thể theo
từng ảnh.

## Nguồn

Kho nguồn của giảng viên cho biết ảnh bắt nguồn từ UA-DETRAC qua bản tái xuất
`SQiFeng/traffic-vehicle-detection`, với thẻ dữ liệu từng công bố giấy phép CC BY 4.0. Kho nguồn đã đổi tên ảnh,
không giữ mã bản ghi gốc và liên kết bản tái xuất hiện không còn truy cập được. `image-manifest.csv` vì vậy ghi
đúng mã phiên bản Git của kho nguồn, mã SHA-256 của từng ảnh và giới hạn truy nguyên này; không suy đoán một mã
nguồn không thể kiểm chứng.

Kho đang ở chế độ riêng tư. Chỉ phát hành rộng sau khi chủ sở hữu chương trình xác nhận quyền phân phối bộ ảnh.

## Phân chia dùng trong sổ thực hành

- ba ảnh dùng để huấn luyện thử;
- một ảnh dùng để xem kết quả dự đoán;
- cả bốn ảnh dùng trong bước đối chiếu nhãn.

Phân chia nhỏ này chỉ giúp kiểm tra đường ống dữ liệu. Nó không phải tập chuẩn để đánh giá khả năng dùng thực tế
của mô hình. Bốn ảnh có thể liên quan về thời gian.

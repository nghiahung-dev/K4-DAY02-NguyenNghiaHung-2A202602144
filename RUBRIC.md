# Tiêu chí đánh giá — Ngày 2

Đây là tiêu chí phản hồi quá trình học, không có một ngưỡng IoU hoặc mAP duy nhất để quyết định đạt hay không đạt.

| Năng lực | Minh chứng rõ | Cần bổ sung | Chưa chứng minh |
| --- | --- | --- | --- |
| Áp dụng bốn lớp | phân biệt `car/truck/bus/van` bằng dấu hiệu nhìn thấy và quy tắc | lớp hợp lý nhưng giải thích còn mơ hồ | đoán theo màu/kích thước hoặc tự đổi mã lớp |
| Phạm vi và độ đầy đủ | rà cả bốn ảnh, có kiểm vật thể thiếu/trùng | còn điểm chưa kiểm | bỏ bước tự kiểm tra hoặc gộp nhiều xe |
| Hình học và thuộc tính | hộp sát phần nhìn thấy, đủ ba thuộc tính trong gói CVAT | còn hộp/thuộc tính cần sửa | hộp lỏng, đoán phần khuất hoặc cho rằng YOLO giữ thuộc tính |
| Tình huống mơ hồ | ba tình huống có vật thể, minh chứng, quy tắc và quyết định | đủ tình huống nhưng thiếu minh chứng | chép đáp án hoặc quyết định không có quy tắc |
| Dòng nhãn YOLO | đọc đúng năm trường và đổi được sang tọa độ điểm ảnh | đọc được nhưng chưa giải thích giới hạn | cho rằng đúng định dạng nghĩa là nhãn đúng |
| Huấn luyện thử | lưu cấu hình, ảnh dự đoán và diễn giải thận trọng | có kết quả nhưng chưa nối với câu hỏi dữ liệu | dùng mAP để chấm người hoặc tuyên bố khả năng dùng thực tế |
| Đối chiếu | báo riêng IoU, đồng thuận lớp, hộp không ghép và sửa một điểm khác biệt | có số đo nhưng chưa nối với quy tắc | dùng IoU trung bình để xếp hạng ai đúng |
| Khả năng tái lập và an toàn | đủ mã kiểm, hai gói xuất và tệp bắt buộc; không lộ dữ liệu cấm | thiếu tệp có thể bổ sung | thay ảnh, lớp hoặc phiên bản; hoặc đưa dữ liệu cấm vào kho mã |

## Minh chứng tối thiểu

- Bài CVAT gồm đúng bốn ảnh và số vật thể thực tế; 40–60 là mục tiêu khối lượng, không phải điểm cắt.
- Hai kết quả kiểm tra từ cùng một công việc: YOLO và CVAT gốc.
- Phiếu quy tắc có định nghĩa lớp và ba tình huống mơ hồ hoàn chỉnh.
- Thông tin lần huấn luyện và một ảnh dự đoán.
- Kết quả đối chiếu độc lập với bạn cùng cặp hoặc bộ tham chiếu.
- Báo cáo giải thích vì sao đồng thuận không đồng nghĩa với đúng và vì sao số đo mô hình không chấm người.

Nếu thiếu minh chứng do công cụ gặp lỗi, ghi đúng tình trạng và thông báo Lab Coach (người hướng dẫn thực hành).
Không tạo tệp rỗng, dòng
nhãn giả hoặc sửa trực tiếp gói xuất để vượt kiểm tra.

# Phiếu quy tắc gán nhãn — Ngày 2

**Họ và tên:** CHƯA ĐIỀN<br>
**MSSV:** CHƯA ĐIỀN<br>
**Hình thức:** CHƯA ĐIỀN — cá nhân hoặc theo cặp<br>
**Mã cặp:** CHƯA ĐIỀN — ghi `SOLO` nếu làm cá nhân

## 1. Phạm vi

- Chỉ gán phương tiện thuộc bốn lớp bên dưới.
- Mỗi phương tiện là một hộp; không gộp nhiều xe.
- Không gán người, xe máy, xe đạp, biển báo hoặc phần phản chiếu.
- Vật thể quá nhỏ hoặc mờ đến mức không thể phân lớp có căn cứ: không đoán; ghi lý do vào nhật ký quyết định.

## 2. Bốn lớp cố định

| Mã | Lớp | Gán khi nhìn thấy | Không gán vào lớp này |
| ---: | --- | --- | --- |
| 0 | `car` (ô tô con) | sedan, hatchback, SUV, taxi, xe bán tải dùng như xe con | xe có thùng/ben rõ; thân xe buýt; xe van thân hộp |
| 1 | `truck` (xe tải) | thùng, ben, sàn hàng hoặc thiết bị công vụ rõ ràng | ô tô con; thân xe buýt; xe van kín một khối |
| 2 | `bus` (xe buýt) | thân xe khách dài, nhiều cửa sổ hoặc hàng ghế | xe van nhỏ; xe tải; ô tô con |
| 3 | `van` (xe van) | thân hộp nhỏ, kín, dùng chở người hoặc hàng | thân xe buýt; khoang hàng tách biệt như xe tải |

Thứ tự lớp là cố định: `0 car, 1 truck, 2 bus, 3 van`.

## 3. Hộp giới hạn

- Vẽ sát phần vật thể nhìn thấy.
- Không ước lượng phần bị xe khác che.
- Vật thể chạm mép ảnh vẫn được gán nếu đủ bằng chứng phân lớp.
- Không để hộp chứa nhiều nền hoặc nhiều phương tiện.

## 4. Ba thuộc tính

| Thuộc tính | Giá trị | Ý nghĩa |
| --- | --- | --- |
| `visibility` (mức nhìn thấy) | `clear` (rõ), `occluded` (bị che), `unclear` (không rõ) | mức bằng chứng nhìn thấy |
| `boundary` (quan hệ mép ảnh) | `inside` (trong ảnh), `truncated` (bị cắt) | vật thể có bị mép ảnh cắt hay không |
| `review_state` (trạng thái xem lại) | `confident` (tự tin), `needs_review` (cần xem lại) | đánh dấu quyết định cần quay lại |

YOLO không lưu ba thuộc tính này. Vì vậy phải xuất thêm `CVAT for images 1.1` từ cùng công việc.

## 5. Ba tình huống mơ hồ

Hoàn thành trước khi xem bài của người khác hoặc bộ nhãn tham chiếu.

### Tình huống A — xe buýt hay xe van?

- Ảnh và mã vật thể: CHƯA ĐIỀN
- Dấu hiệu nhìn thấy: CHƯA ĐIỀN
- Quy tắc áp dụng: CHƯA ĐIỀN
- Quyết định: CHƯA ĐIỀN
- Nếu vẫn thiếu bằng chứng, bạn sẽ làm gì? CHƯA ĐIỀN

### Tình huống B — xe tải hay xe van/ô tô con?

- Ảnh và mã vật thể: CHƯA ĐIỀN
- Dấu hiệu nhìn thấy: CHƯA ĐIỀN
- Quy tắc áp dụng: CHƯA ĐIỀN
- Quyết định: CHƯA ĐIỀN
- Nếu vẫn thiếu bằng chứng, bạn sẽ làm gì? CHƯA ĐIỀN

### Tình huống C — bị che, bị mép ảnh cắt hay không đủ bằng chứng?

- Ảnh và mã vật thể: CHƯA ĐIỀN
- Dấu hiệu nhìn thấy khi phóng 100%: CHƯA ĐIỀN
- Giá trị `visibility`: CHƯA ĐIỀN
- Giá trị `boundary`: CHƯA ĐIỀN
- Trạng thái `review_state`: CHƯA ĐIỀN
- Lý do: CHƯA ĐIỀN

## 6. Xác nhận tự kiểm tra

- [ ] Đã rà đủ bốn ảnh.
- [ ] Đã kiểm vật thể thiếu và trùng.
- [ ] Đã kiểm lớp và hình học từng hộp.
- [ ] Mỗi hộp có đủ ba thuộc tính.
- [ ] Đã xử lý mọi hộp `needs_review`.
- [ ] Đã hoàn thành ba tình huống trước khi xem nguồn đối chiếu.
- [ ] Nếu làm theo cặp, hai người đã xuất bài độc lập trước khi trao đổi.
- [ ] Nếu làm cá nhân, bài riêng đã được kiểm trước khi nhận bộ tham chiếu.
- [ ] Số vật thể thực tế: CHƯA ĐIỀN — 40–60 là mục tiêu khối lượng, không phải điểm cắt.

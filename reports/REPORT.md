# Báo cáo — Ngày 2: phát hiện vật thể

**Họ và tên:** Nguyễn Nghĩa Hùng<br>
**MSSV:** 2A202602144<br>
**Hình thức:** theo cặp<br>
**Mã cặp:** 01

## 1. Bài độc lập và nguồn dữ liệu

- Mã SHA-256 của ZIP ảnh được cấp:
- Bốn mã ảnh:
- Số vật thể thực tế:
- Mã SHA-256 của gói YOLO của bạn: 4cd5de6389fd69afe7d528c7f522900dcaf75f8ac0507ad8cc2cc043af0de811
- Mã SHA-256 của gói CVAT gốc của bạn: 88beddfc0ee2054cc79345fdaddfa6d07731d3f9b6b51da529366e9a9294a00d
- Nguồn đối chiếu: bạn cùng cặp hoặc bộ tham chiếu do người hướng dẫn thực hành cấp:
- Mã SHA-256 của gói đối chiếu: 4cd5de6389fd69afe7d528c7f522900dcaf75f8ac0507ad8cc2cc043af0de811
- Nếu làm cá nhân, ghi mã lần phát và thời điểm nhận bộ tham chiếu:

Giải thích vì sao bài của bạn vẫn độc lập trước khi đối chiếu:

Vì bài của mình chưa đối chiếu nên nó vẫn độc lập.

## 2. Quyết định phân lớp

| Ảnh/vật thể | Lớp | Dấu hiệu nhìn thấy | Quy tắc áp dụng |
| --- | --- | --- | --- |
| drive_022.jpg | car | Trực tiếp | Trực tiếp |

Nêu một ví dụ cho thấy lớp và thuộc tính là hai loại thông tin khác nhau:

Ví dụ ở ảnh drive_022.jpg, có 1 ô tô thuộc lớp car và có thuộc tính là occluded.

## 3. Tự kiểm tra và sửa nhãn

| Trước khi sửa | Loại lỗi | Cách phát hiện | Sau khi sửa và quy tắc |
| --- | --- | --- | --- |
| Không chặt | Hình học | Nhìn bằng mắt | Sửa lại box và đã chặt hơn |

- Số hộp `needs_review` trước và sau khi kiểm: 0
- Một quyết định chưa đủ bằng chứng và cách bạn xin hỗ trợ: Một vài chỗ ảnh quá mờ, nên mình cố gắng nhìn và hỏi lab coach.

## 4. Một dòng nhãn YOLO

- Dòng `class x_center y_center width height`:
row: [3, 0.518602, 0.526141, 0.124047, 0.071969]
- Tên lớp và tọa độ điểm ảnh `xyxy`:
lớp=3 (van) | tâm=(0.5186, 0.5261) | kích thước=(0.1240, 0.0720)
pixel xyxy: [292.2, 313.7, 371.6, 359.8]
- Vì sao dòng đúng định dạng vẫn có thể sai lớp, phạm vi hoặc hình học?
Vì có thể có nhiều class bị occluded vì thế chúng có thể nằm cùng 1 hàng, nên có thể sai lớp và hình học.

## 5. Huấn luyện và dự đoán thử

- Ba mã ảnh huấn luyện: drive_022, drive_033, drive_038
- Mã ảnh thẩm định: drive_008
- Mô tả một dự đoán trong `detect_result.jpg`: Mô hình không dự đoán được vật thể nào, ảnh detect_result.jpg 
- Dự đoán đó gợi ý cần kiểm lại quy tắc hoặc dữ liệu nào? 
Mình nghĩ là cần kiểm tra lại dữ liệu train.
- Minh chứng nào có thể bác bỏ nhận định của bạn?
Hãy đọc kết quả dự đoán cụ thể; không dùng mAP của bốn ảnh để kết luận chất lượng người gán nhãn hay khả năng dùng trong thực tế.
- Vì sao kết quả trên bốn ảnh không phải phép đánh giá mô hình dùng thực tế?
Vì dữ liệu chưa đủ cho mô hình học.

## 6. Đối chiếu nhãn

- Số hộp ghép được: 88
- IoU trung bình và trung vị: 0.813868, 0.846275
- Mức đồng thuận lớp: 0.943182
- Số hộp phía bạn không ghép được: 32
- Số hộp phía đối chiếu không ghép được: 1
- Một điểm khác biệt cụ thể: Mình có nhiều objects hơn nên không ghép được với bạn cặp.
- Quy tắc hoặc hành động sửa phát sinh: Thảo thuận lại với nhau.
- Vì sao mức đồng thuận cao không chứng minh mọi nhãn đều đúng? Vì có thể cả 2 đều làm sai.

## 7. Kiểm tra kho GitHub cá nhân

- [x] Có phiếu quy tắc với ba tình huống mơ hồ.
- [x] Có kết quả kiểm hai gói xuất.
- [x] Có thông tin lần huấn luyện và ảnh dự đoán.
- [x] Có tóm tắt, bảng và ảnh phủ của bước đối chiếu.
- [x] Không có gói xuất thô, bộ nhãn tham chiếu hoặc trọng số mô hình.
- [x] Không có dữ liệu VinFast/khách hàng/ảnh cá nhân/mật khẩu/mã truy cập.

Minh chứng mạnh nhất trong bài và câu hỏi còn lại cho Lab Coach:

Kết quả so sánh với bạn cùng cặp:
```
{
  "matching": "ghép tối ưu theo IoU hình học, không dùng lớp khi ghép",
  "comparison_iou_floor": 0.01,
  "floor_is_official_pass_threshold": false,
  "calibration_image_ids": [
    "drive_022",
    "drive_033",
    "drive_038",
    "drive_008"
  ],
  "matched_boxes": 88,
  "mean_iou": 0.813868,
  "median_iou": 0.846275,
  "class_agreement": 0.943182,
  "unmatched_mine": 32,
  "unmatched_comparison": 1,
  "comparison_source": "peer",
  "interpretation_warning": "Mức đồng thuận giữa hai người đo khả năng tái lập quy tắc, không chứng minh cả hai đều đúng.",
  "comparison_export_sha256": "3d29e5c2e44aa71b41885a76b932fed0179f1147622f8fb2aa076b70f0ddd484"
}
```
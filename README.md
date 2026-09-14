# Ngày 2 — Dữ liệu cho bài toán phát hiện vật thể

**Đối tượng:** học viên Giai đoạn 1. **Trạng thái:** tài liệu học viên đang dùng thử trong lớp. **Phạm vi:** Ngày 2.

> **Lưu ý về Google Colab:** repo đang ở chế độ riêng tư và tổ chức chặn ứng dụng OAuth chưa được phê duyệt.
> Vì vậy, không mở sổ tay bằng liên kết nhập trực tiếp từ GitHub; hãy tải tệp xuống rồi đưa lên Colab theo hướng
> dẫn bên dưới.

Đây là kho mã dành cho học viên. Trong bốn giờ, bạn sẽ gán nhãn bốn ảnh giao thông bằng CVAT, xuất dữ liệu theo
định dạng YOLO (định dạng nhãn phát hiện vật thể), huấn luyện thử một bộ phát hiện vật thể bằng Ultralytics
(thư viện huấn luyện mô hình), đối chiếu kết quả và sửa nhãn dựa trên
minh chứng.

Tệp `data/day2-cvat-input.zip` đã chứa sẵn toàn bộ ảnh do thầy Dương lựa chọn cho bài trên lớp. Bạn không cần
chạy sổ thực hành để tạo hoặc tải ảnh.

## Sau bài thực hành, bạn có thể

1. Phân biệt bốn lớp `car` (ô tô con), `truck` (xe tải), `bus` (xe buýt) và `van` (xe van).
2. Vẽ hộp giới hạn sát phần vật thể nhìn thấy và ghi đủ thuộc tính kiểm tra.
3. Xuất cùng một bài gán nhãn theo hai định dạng: `Ultralytics YOLO Detection` và `CVAT for images 1.1`.
4. Đọc một dòng nhãn YOLO và đổi tọa độ chuẩn hóa về tọa độ điểm ảnh.
5. Huấn luyện thử, xem ảnh dự đoán và dùng kết quả để đặt câu hỏi về dữ liệu.
6. Đối chiếu với bài độc lập của bạn cùng cặp hoặc bộ nhãn tham chiếu do người hướng dẫn thực hành (Lab Coach)
   cung cấp.

## Dữ liệu và quy ước

| Thành phần | Quy ước của bài |
| --- | --- |
| Ảnh đầu vào | `data/day2-cvat-input.zip`, gồm bốn ảnh 640 × 640 điểm ảnh |
| Thứ tự lớp | `0 car`, `1 truck`, `2 bus`, `3 van` |
| Khối lượng mục tiêu | 40–60 phương tiện trên toàn bộ bốn ảnh |
| Thuộc tính | `visibility` (mức nhìn thấy), `boundary` (quan hệ với mép ảnh), `review_state` (trạng thái cần xem lại) |
| Đầu ra CVAT | một gói YOLO có ảnh và một gói CVAT gốc có thuộc tính |
| Huấn luyện thử | YOLO11n, Ultralytics 8.4.145, tám vòng lặp, hạt giống ngẫu nhiên 42 |
| Đối chiếu | chỉ thực hiện sau khi bài riêng đã lưu và xuất dữ liệu |

Không tự thay ảnh, đổi thứ tự lớp hoặc sửa trực tiếp tệp nhãn để làm kết quả đẹp hơn.

## Làm cá nhân hoặc theo cặp

Hai hình thức có cùng yêu cầu cốt lõi: mỗi học viên tự gán nhãn cả bốn ảnh, tự kiểm tra và xuất bài của mình trước
khi xem nguồn đối chiếu.

| Hình thức | Nguồn đối chiếu |
| --- | --- |
| Cá nhân | gói nhãn tham chiếu do người hướng dẫn thực hành cung cấp sau khi bài riêng đã khóa |
| Theo cặp | gói YOLO của bạn cùng cặp; chỉ trao đổi sau khi cả hai đã xuất bài |

Mức đồng thuận giữa hai người cho biết quy tắc có dễ tái lập hay không, không chứng minh cả hai đều đúng.

## Lịch thực hành 240 phút

| Phút | Hoạt động | Minh chứng |
| ---: | --- | --- |
| 0–15 | Kiểm tra CVAT, nhận ZIP và chọn hình thức làm bài | CVAT mở được, đúng tệp ảnh |
| 15–35 | Đọc quy tắc lớp và ba tình huống mơ hồ | giải thích được ít nhất một quyết định |
| 35–50 | Tạo dự án, tác vụ và hộp đầu tiên | hộp đầu có đủ thuộc tính |
| 50–95 | Gán nhãn tập trung trong 45 phút | hoàn thành bốn ảnh, hướng tới 40–60 vật thể |
| 95–105 | Lưu bài độc lập; chưa xem nguồn đối chiếu | trạng thái CVAT đã lưu |
| 105–115 | Nghỉ | — |
| 115–135 | Tự kiểm tra chất lượng và hoàn tất phiếu quy tắc | ba tình huống mơ hồ đã được xử lý |
| 135–155 | Xuất hai gói dữ liệu và kiểm tra | hai gói từ cùng một tác vụ |
| 155–160 | Khóa bản xuất của riêng mình | mã SHA-256 đã được ghi |
| 160–180 | Đọc dòng YOLO, huấn luyện và dự đoán thử | thông tin lần chạy và ảnh dự đoán |
| 180–205 | Đối chiếu với bạn cùng cặp hoặc bộ tham chiếu | IoU (mức giao trên hợp), mức đồng thuận lớp và vật thể không ghép được |
| 205–225 | Sửa một quyết định dựa trên minh chứng | ghi lại trước và sau khi sửa |
| 225–235 | Hoàn thiện báo cáo | đủ tệp bắt buộc |
| 235–240 | Kiểm tra và đưa minh chứng lên kho GitHub cá nhân | đường dẫn kho mở được và đủ tệp |

## Bắt đầu

1. Cài và kiểm tra CVAT theo [CVAT_SETUP.md](CVAT_SETUP.md) trước giờ học.
2. Tải trực tiếp [data/day2-cvat-input.zip](data/day2-cvat-input.zip).
3. Làm theo [GUIDE.md](GUIDE.md) để tạo dự án CVAT, gán nhãn và xuất hai gói dữ liệu.
4. Sau khi có hai gói xuất, mở sổ thực hành theo mục ngay bên dưới và chạy lần lượt từng ô lệnh.
5. Hoàn thành `REPORT.md` và `GUIDELINE_MINI_SHEET.md`, đưa các tệp đã kiểm tra lên kho GitHub cá nhân rồi nộp đường dẫn kho trên VLearn.

### Mở sổ tay trên Google Colab khi repo đang riêng tư

1. Mở tệp [notebooks/day2-detection-quality.ipynb](notebooks/day2-detection-quality.ipynb) trên GitHub.
2. Chọn **Download raw file (Tải tệp gốc xuống)** để lưu tệp `.ipynb` về máy.
3. Mở [Google Colab](https://colab.research.google.com/).
4. Chọn **File (Tệp) → Upload notebook (Tải sổ tay lên)**, rồi chọn tệp vừa tải.

Không chọn thẻ **GitHub** trong Colab cho repo này; yêu cầu đó sẽ bị tổ chức từ chối với mã lỗi 403.

## Bài nộp: kho GitHub cá nhân

Mỗi học viên tạo một kho GitHub mới, không dùng chung kho với bạn cùng cặp và đặt tên:

```text
KX-DAY02-HoVaTen-MSSV
```

Ví dụ: `K4-DAY02-Nguyen-Van-An-20231234`. Chế độ hiển thị của kho và tài khoản cần cấp quyền được thực hiện theo thông báo trên lớp. Không sao chép toàn bộ kho bài mẫu vào kho cá nhân.

Ở cấp đầu của kho cá nhân phải có trực tiếp:

```text
REPORT.md
GUIDELINE_MINI_SHEET.md
day2_lab_outputs/
├── IMAGE_ATTRIBUTION.md
├── input_pool_audit.json
├── my_export_audit.json
├── my_native_export_audit.json
├── training_run.json
├── detect_result.jpg
├── comparison_iou.csv
├── comparison_summary.json
└── comparison_overlay.png
```

Tên tệp được giữ bằng tiếng Anh để sổ thực hành có thể kiểm tra tự động. Nội dung báo cáo viết bằng tiếng Việt. Ô cuối của sổ thực hành tạo một ZIP chuyển tệp từ Colab về máy; ZIP này không phải bài nộp. Giải nén gói đó, đưa đúng ba mục ở trên vào kho cá nhân, rồi nộp đường dẫn kho trên VLearn.

Không đưa vào kho cá nhân: gói xuất thô, bộ nhãn tham chiếu, trọng số mô hình, mật khẩu, mã truy cập, dữ
liệu cá nhân hoặc dữ liệu nội bộ.

## Tài liệu chính

- [Hướng dẫn từng bước](GUIDE.md)
- [Hướng dẫn bằng ảnh chụp CVAT thật](docs/day2-e2e-guide.html)
- [Phiếu quy tắc gán nhãn](guideline-mini-sheet.md)
- [Tiêu chí đánh giá](RUBRIC.md)
- [Nguồn gốc dữ liệu](data/README.md)

## Hỗ trợ và phần mở rộng

- Nếu đây là lần đầu dùng CVAT, hãy mở hướng dẫn bằng ảnh chụp thật, làm từng bước và dừng kiểm tra sau hộp đầu
  tiên, sau khi nạp đủ bốn ảnh và sau mỗi lần xuất dữ liệu.
- Mọi học viên vẫn làm cùng bốn ảnh, cùng lớp, cùng thuộc tính và cùng bộ minh chứng. Hỗ trợ không thay đổi yêu
  cầu cốt lõi.
- Sau khi hoàn thành kho cá nhân, người muốn tìm hiểu thêm có thể chọn một trường hợp ghép hộp kém, giải thích nguyên
  nhân và đề xuất một câu quy tắc rõ hơn. Đây là phần mở rộng tự chọn, không yêu cầu gán thêm ảnh hoặc thêm hộp.

## Tài liệu kỹ thuật tham khảo

- [CVAT: định dạng Ultralytics YOLO](https://docs.cvat.ai/docs/dataset_management/formats/format-yolo-ultralytics/)
- [CVAT: định dạng CVAT for images](https://docs.cvat.ai/docs/manual/advanced/formats/format-cvat/)
- [Ultralytics: dữ liệu phát hiện vật thể](https://docs.ultralytics.com/datasets/detect/)
- [Bài báo UA-DETRAC](https://faculty.ucmerced.edu/mhyang/papers/cviu2020_detrac.pdf)

## Bài tập về nhà tự chọn

Bộ ảnh có các lớp người đi bộ, người đi xe đạp, ô tô con và xe tải sẽ được thông báo riêng nếu được phát hành.
Không dùng bộ đó trong dự án hoặc kho cá nhân của bài thực hành trên lớp này.

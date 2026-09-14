# Hướng dẫn học viên — Ngày 2: phát hiện vật thể

## Chuẩn bị trước giờ học

- Cài CVAT theo `CVAT_SETUP.md` và mở được `http://localhost:8080`.
- Tải trực tiếp `data/day2-cvat-input.zip`; không chạy sổ thực hành để tạo hoặc tải ảnh.
- Đọc `guideline-mini-sheet.md`; không tự đổi ảnh, thứ tự lớp hoặc phiên bản phần mềm.
- Chọn làm cá nhân hoặc theo cặp.
- Không dùng ảnh cá nhân, dữ liệu VinFast/khách hàng, mật khẩu hoặc mã truy cập làm minh chứng.

## 0–35 phút — kiểm tra sẵn sàng và hiểu bốn lớp

Xác nhận CVAT mở được và bạn có đúng tệp `day2-cvat-input.zip`. Chưa cần mở sổ thực hành.

Nếu đây là lần đầu bạn dùng CVAT, hãy mở đồng thời `docs/day2-e2e-guide.html` và tự dừng kiểm tra tại ba mốc:
đã nạp đúng bốn ảnh; hộp đầu tiên có đủ ba thuộc tính; hai gói xuất có cùng số hộp. Nếu một mốc chưa đạt, sửa
ngay trước khi đi tiếp.

Bốn lớp của bài:

- `car` (ô tô con): sedan, hatchback, SUV, taxi và xe bán tải dùng như xe con;
- `truck` (xe tải): có thùng, ben, sàn chở hàng hoặc thiết bị công vụ rõ ràng;
- `bus` (xe buýt): thân xe khách dài, nhiều cửa sổ hoặc nhiều hàng ghế;
- `van` (xe van): thân hộp nhỏ, kín, không có thân xe buýt hay khoang hàng tách biệt như xe tải.

Nếu chưa đủ bằng chứng để phân biệt, phóng ảnh lên 100%, đặt
`review_state=needs_review` (trạng thái: cần xem lại) và ghi lý do. Không đoán theo màu hoặc kích thước hộp.

## 35–50 phút — tạo dự án và tác vụ CVAT

Mở `docs/day2-e2e-guide.html` để xem ảnh chụp CVAT thật.

1. Chọn **Projects (Dự án) → + → Create a new project (Tạo dự án mới)**.
2. Đặt tên `DAY02-SOLO-<MSSV>` nếu làm cá nhân hoặc `DAY02-<PAIR_ID>-<MSSV>` nếu làm theo cặp.
3. Tạo đúng thứ tự: `car`, `truck`, `bus`, `van`.
4. Với mỗi lớp, thêm ba thuộc tính kiểu **Select (Danh sách chọn)**:
   - `visibility` (mức nhìn thấy): `clear` (rõ), `occluded` (bị che), `unclear` (không rõ);
   - `boundary` (quan hệ với mép ảnh): `inside` (nằm trong ảnh), `truncated` (bị mép ảnh cắt);
   - `review_state` (trạng thái xem lại): `confident` (tự tin), `needs_review` (cần xem lại).
5. Chọn **Submit & Open (Tạo và mở)**.
6. Tạo tác vụ `Day2-CCTV`, chọn đúng dự án và tải lên `day2-cvat-input.zip`.
7. Mở **Job #1 (Công việc số 1)** và xác nhận có bốn ảnh.

## 50–95 phút — gán nhãn tập trung

1. Chọn **Rectangle (Hình chữ nhật)** và chọn lớp.
2. Vẽ hộp sát phần phương tiện nhìn thấy; không đoán phần bị che.
3. Điền đủ ba thuộc tính cho mỗi hộp.
4. Dùng `D` để về ảnh trước, `F` để sang ảnh sau và `N` để lặp cách vẽ gần nhất.
5. Chọn **Save (Lưu)** thường xuyên.

Quy tắc phạm vi:

- mỗi phương tiện là một hộp;
- không gộp nhiều xe vào một hộp;
- không gán người, xe máy hoặc xe đạp;
- không dùng dự đoán tự động làm đáp án;
- người làm theo cặp vẫn phải tự gán cả bốn ảnh, không chia ảnh hoặc chia lớp.

Mục tiêu là 40–60 vật thể trên toàn bộ bốn ảnh. Nếu dưới 40 ở phút 95, giữ số liệu thật và chuyển sang tự kiểm
tra; không vẽ ẩu để đủ số lượng.

## 95–135 phút — lưu bài độc lập và tự kiểm tra

Trước khi xem bài khác:

1. Lưu toàn bộ tác vụ.
2. Rà lần lượt: phạm vi → vật thể thiếu/trùng → lớp → hình học → thuộc tính → nhật ký quyết định.
3. Lọc mọi hộp có `needs_review` (cần xem lại).
4. Hoàn thành ba tình huống mơ hồ trong `GUIDELINE_MINI_SHEET.md`.

## 135–155 phút — xuất hai gói dữ liệu

Từ cùng một công việc CVAT:

1. Chọn **Menu (Trình đơn) → Export job dataset (Xuất dữ liệu công việc)**.
2. Xuất **Ultralytics YOLO Detection** và chọn kèm ảnh.
3. Xuất lần hai theo **CVAT for images 1.1** để giữ thuộc tính.
4. Không sửa tệp TXT hoặc XML bên trong hai gói.

Sau khi có hai gói, mở sổ thực hành:

1. Chạy các ô lệnh từ đầu theo đúng thứ tự.
2. Ô lệnh 1 chỉ kiểm tệp ảnh đã được cấp; nó không tạo hoặc tải ảnh.
3. Tải gói YOLO của bạn ở ô 3a và gói CVAT gốc ở ô 3b.
4. Nếu kiểm tra báo lỗi, sửa trong CVAT rồi xuất lại.

Nếu nút tải tệp không hiện, đặt tệp trong bảng **Files (Tệp)** của Colab với tên
`/content/day2-cvat-input.zip`, `/content/day2-my-export.zip`, `/content/day2-native-export.zip` và
`/content/day2-comparison-export.zip`.

## 155–180 phút — khóa bài và huấn luyện thử

- Ghi mã SHA-256 của gói YOLO của riêng bạn. Đây là bản độc lập đã khóa.
- Nếu làm cá nhân, người hướng dẫn thực hành (Lab Coach) có thể gửi gói nhãn tham chiếu từ phút 160; chưa mở
  trước phút 180.
- Nếu làm theo cặp, chưa trao đổi gói YOLO trước phút 180.
- Ô 3c đọc một dòng `class x_center y_center width height` (lớp, tâm ngang, tâm dọc, rộng, cao) và đổi sang
  tọa độ điểm ảnh.
- Ô 4 huấn luyện thử YOLO11n bằng ba ảnh và dự đoán trên một ảnh.

Đây chỉ là phép kiểm tra đường ống dữ liệu. Kết quả mAP (độ chính xác trung bình theo nhiều ngưỡng) hoặc ảnh dự
đoán không phải điểm của người gán nhãn và
không chứng minh mô hình dùng được trong thực tế.

## 180–205 phút — đối chiếu

- Cá nhân: dùng gói YOLO tham chiếu do Lab Coach cung cấp.
- Theo cặp: hai người xác nhận đã khóa bài rồi trao đổi gói YOLO.

Ô lệnh so sánh báo riêng:

- IoU: mức chồng khít hình học;
- mức đồng thuận lớp;
- số hộp của bạn không ghép được;
- số hộp phía đối chiếu không ghép được.

IoU không phải ngưỡng đạt. Hai người có thể đồng thuận nhưng vẫn cùng sai.

## 205–240 phút — sửa, báo cáo và tạo kho GitHub cá nhân

1. Chọn một điểm khác biệt thuộc phạm vi, lớp, hình học hoặc thuộc tính.
2. Nêu minh chứng quan sát được và quy tắc áp dụng.
3. Nếu cần, sửa trong CVAT rồi xuất lại; không sửa trực tiếp tệp nhãn.
4. Ghi rõ trước khi sửa và sau khi sửa trong `REPORT.md`.
5. Hoàn thành `GUIDELINE_MINI_SHEET.md`.
6. Chạy ô lệnh cuối để kiểm tra và tạo ZIP chuyển tệp từ Colab về máy. ZIP này không phải bài nộp.
7. Tạo một kho GitHub cá nhân tên `KX-DAY02-HoVaTen-MSSV`. Không dùng chung kho với bạn cùng cặp và không sao chép toàn bộ kho bài mẫu.
8. Giải nén ZIP chuyển tệp. Trên GitHub, chọn **Add file (Thêm tệp) → Upload files (Tải tệp lên)**, rồi đưa trực tiếp `REPORT.md`, `GUIDELINE_MINI_SHEET.md` và thư mục `day2_lab_outputs/` vào cấp đầu của kho.
9. Chọn **Commit changes (Ghi nhận thay đổi)**, mở lại kho và kiểm đủ ba mục. Nộp đường dẫn kho trên VLearn. Chế độ hiển thị và tài khoản cần cấp quyền làm theo thông báo trên lớp.

## Xử lý sự cố nhanh

| Hiện tượng | Cách xử lý |
| --- | --- |
| CVAT không mở | khởi động lại một lần theo `CVAT_SETUP.md`; nếu vẫn lỗi, gửi ảnh lỗi cho Lab Coach |
| ZIP ảnh sai | tải lại đúng `data/day2-cvat-input.zip`; không thay ảnh |
| Sai thứ tự lớp | dừng ngay và sửa dự án hoặc tạo lại tác vụ |
| Gói YOLO thiếu ảnh hoặc nhãn | xuất lại và chọn kèm ảnh |
| Gói CVAT thiếu thuộc tính | bổ sung đủ ba thuộc tính trong CVAT rồi xuất lại |
| Hai gói có số hộp khác nhau | xuất lại cả hai từ cùng trạng thái công việc |
| Chưa có nguồn đối chiếu | giữ bản xuất độc lập và báo Lab Coach; không dùng lại bài của chính mình |
| Huấn luyện chậm hoặc lỗi | lưu thông báo lỗi đã che thông tin riêng tư và dùng phương án dự phòng do Lab Coach cung cấp |
| Colab bị ngắt kết nối | khởi động lại phiên và chạy lại từ ô đầu tiên |

## Ba câu cần nhớ

**IoU cao có nghĩa là đúng không?** Không. IoU chỉ mô tả độ chồng khít của hai hộp đã được ghép.

**Vì sao phải xuất hai định dạng?** YOLO giữ lớp và hộp nhưng không giữ ba thuộc tính kiểm tra; định dạng CVAT
gốc giữ các thuộc tính đó.

**Vì sao chỉ có bốn ảnh?** Bộ ảnh nhỏ giúp hoàn thành trọn đường ống trong lớp. Kết quả huấn luyện trên bốn ảnh
không phải phép đánh giá mô hình dùng trong thực tế.

## Phần mở rộng tự chọn sau khi đã hoàn thành kho cá nhân

Chọn một cặp hộp có IoU thấp hoặc một vật thể không ghép được. Dựa trên ảnh, phiếu quy tắc và hai bản xuất để
giải thích nguyên nhân. Sau đó đề xuất đúng một câu sửa cho quy tắc nhằm giúp người tiếp theo ra quyết định nhất
quán hơn. Không gán thêm ảnh, không sửa trực tiếp tệp nhãn và không thay đổi bộ minh chứng cốt lõi.

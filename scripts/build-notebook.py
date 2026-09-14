#!/usr/bin/env python3
"""Tạo sổ thực hành Ngày 2 từ các hàm hỗ trợ và mẫu đã kiểm thử."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "notebooks" / "day2-detection-quality.ipynb"


def markdown(cell_id, source):
    return {"cell_type": "markdown", "id": cell_id, "metadata": {}, "source": source.splitlines(keepends=True)}


def code(cell_id, source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


helper_source = (ROOT / "lab_utils.py").read_text(encoding="utf-8")
helper_source = helper_source.replace("from __future__ import annotations\n\n", "")
manifest_text = (ROOT / "data" / "image-manifest.csv").read_text(encoding="utf-8")
report_template = (ROOT / "reports" / "REPORT_TEMPLATE.md").read_text(encoding="utf-8")
guideline_template = (ROOT / "guideline-mini-sheet.md").read_text(encoding="utf-8")

cells = [
    markdown(
        "title-and-contract",
        """# Ngày 2 — từ gán nhãn đến bộ phát hiện vật thể

Bài thực hành 4 giờ triển khai đầy đủ yêu cầu trên bài giảng: áp dụng bốn lớp `car` (ô tô con), `truck` (xe tải),
`bus` (xe buýt), `van` (xe van); gán 40–60 vật thể trong CVAT; xuất YOLO (định dạng nhãn phát hiện vật thể);
huấn luyện thử bằng Ultralytics (thư viện huấn luyện mô hình); đối chiếu IoU (mức giao trên hợp của hai hộp) với
bạn cùng cặp hoặc bộ nhãn do Lab Coach (người hướng dẫn thực hành) cấp; rồi nộp phiếu quy
tắc và các minh chứng.
**Luồng chính không yêu cầu viết hoặc sửa mã nguồn.**

Mỗi người phải gán nhãn độc lập trước khi xem nguồn đối chiếu. IoU và mAP (độ chính xác trung bình theo nhiều
ngưỡng) là tín hiệu chẩn đoán, không phải điểm
đạt, không chứng minh nhãn đúng và không phải phép đánh giá mô hình dùng trong thực tế. Không đưa dữ liệu
VinFast, dữ liệu khách hàng, ảnh cá nhân hoặc mã truy cập vào sổ thực hành hay repo.
""",
    ),
    markdown(
        "cvat-independent-work",
        """## Trước khi chạy các ô lệnh — hoàn tất CVAT độc lập

Lấy trực tiếp `data/day2-cvat-input.zip` từ repo của lớp và làm theo `GUIDE.md`. Gói ZIP đã chứa đủ bốn ảnh;
sổ thực hành không tạo hoặc tải ảnh. Tạo dự án với đúng bốn lớp và ba thuộc tính, gán nhãn toàn bộ bốn ảnh,
tự kiểm tra chất lượng rồi xuất từ **cùng một tác vụ/công việc**:

1. `Ultralytics YOLO Detection` kèm ảnh để giữ lớp và hộp;
2. `CVAT for images 1.1` để giữ các thuộc tính.

Chỉ chạy các ô lệnh bên dưới sau khi đã có hai gói xuất của chính bạn. Người làm theo cặp không xem tác vụ hay
gói xuất của nhau trước khi cả hai hoàn thành. Người làm cá nhân chỉ nhận bộ nhãn đối chiếu sau khi đã kiểm bài mình.
""",
    ),
    code(
        "install-pinned-dependencies",
        """# 0a — Cài đúng phiên bản của bài thực hành; chờ ô lệnh chạy xong.
%pip -q install ultralytics==8.4.145 certifi==2026.6.17
""",
    ),
    code("embedded-tested-helpers", helper_source),
    code(
        "preflight-and-workspace",
        f'''# 0b — Kiểm tra môi trường và tạo thư mục làm việc.
# Chạy lại ô này sẽ xóa đầu ra tạm của phiên hiện tại, không xóa tệp trên Google Drive.
import io
import os
import re
import shutil
import time
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import torch
import ultralytics
from PIL import Image
from ultralytics import YOLO

ULTRALYTICS_VERSION_PIN = "8.4.145"
INPUT_ZIP_SHA256 = "f7d99888f21440fb0374d84962b93213bd8c14e665d093cc8d37f4c61b71ed33"
assert ultralytics.__version__ == ULTRALYTICS_VERSION_PIN, (
    f"Sai Ultralytics {{ultralytics.__version__}}; cần {{ULTRALYTICS_VERSION_PIN}}"
)
WORK_DIR = Path("/content/day2_lab") if Path("/content").exists() else Path("day2_lab")
OUTPUT_DIR = Path("day2_lab_outputs")
UPLOAD_DIR = WORK_DIR / "uploads"
MANIFEST_PATH = WORK_DIR / "image-manifest.csv"
REPORT_PATH = Path("REPORT.md")
GUIDELINE_PATH = Path("GUIDELINE_MINI_SHEET.md")
for path in (WORK_DIR, OUTPUT_DIR):
    if path.exists():
        shutil.rmtree(path)
for path in (UPLOAD_DIR, OUTPUT_DIR):
    path.mkdir(parents=True, exist_ok=True)

MANIFEST_CSV = {manifest_text!r}
REPORT_TEMPLATE = {report_template!r}
GUIDELINE_TEMPLATE = {guideline_template!r}
MANIFEST_PATH.write_text(MANIFEST_CSV, encoding="utf-8")
if not REPORT_PATH.exists():
    REPORT_PATH.write_text(REPORT_TEMPLATE, encoding="utf-8")
if not GUIDELINE_PATH.exists():
    GUIDELINE_PATH.write_text(GUIDELINE_TEMPLATE, encoding="utf-8")
manifest_rows = read_manifest(MANIFEST_PATH)

try:
    from google.colab import files
except ImportError:
    files = None

def read_one_upload(fallback_path, prompt):
    fallback_path = Path(fallback_path)
    if fallback_path.is_file():
        print(f"Dùng tệp trong bảng Files (Tệp): {{fallback_path}}")
        return fallback_path.name, fallback_path.read_bytes()
    if files is None:
        raise RuntimeError(f"Không ở Colab. Hãy đặt tệp tại {{fallback_path}} rồi chạy lại ô lệnh.")
    print(prompt)
    uploaded = files.upload()
    if len(uploaded) != 1:
        raise ValueError(f"Cần đúng 1 file, nhận {{len(uploaded)}}")
    return next(iter(uploaded.items()))

print(f"ĐẠT kiểm tra môi trường | Ultralytics={{ultralytics.__version__}} | thiết bị={{'GPU' if torch.cuda.is_available() else 'CPU'}}")
print(f"Dữ liệu đầu vào: {{len(manifest_rows)}} ảnh")
print("Gói ZIP ảnh được cấp trực tiếp; ô 1 chỉ kiểm tính toàn vẹn, không tạo hoặc tải ảnh.")
''',
    ),
    code(
        "verify-cvat-input",
        '''# 1 — Kiểm gói day2-cvat-input.zip được cấp: phải có đúng bốn ảnh.
# Ô lệnh này không tạo hoặc tải ảnh từ Internet.
input_name, input_payload = read_one_upload(
    "/content/day2-cvat-input.zip",
    "Chọn file data/day2-cvat-input.zip vừa tải từ repository",
)
INPUT_ZIP = UPLOAD_DIR / "day2-cvat-input.zip"
INPUT_ZIP.write_bytes(input_payload)
if sha256_file(INPUT_ZIP) != INPUT_ZIP_SHA256:
    raise ValueError("Sai checksum day2-cvat-input.zip; tải lại từ repository, không tự thay ảnh.")
input_root = safe_extract_zip(INPUT_ZIP, WORK_DIR / "input-images")
expected_ids = [row["image_id"] for row in manifest_rows]
actual_images = sorted(path for path in input_root.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
if [path.stem for path in actual_images] != sorted(expected_ids):
    raise ValueError(f"ZIP phải có đúng {sorted(expected_ids)}, nhận {[p.stem for p in actual_images]}")
manifest_by_id = {row["image_id"]: row for row in manifest_rows}
for path in actual_images:
    row = manifest_by_id[path.stem]
    if sha256_file(path) != row["sha256"]:
        raise ValueError(f"Checksum ảnh sai: {path.name}")
    with Image.open(path) as image:
        if image.size != (row["width"], row["height"]):
            raise ValueError(f"Kích thước ảnh sai: {path.name}")
input_audit = {
    "archive_sha256": sha256_file(INPUT_ZIP),
    "image_ids": sorted(expected_ids),
    "image_count": len(actual_images),
    "provided_input_is_unchanged": True,
}
(OUTPUT_DIR / "input_pool_audit.json").write_text(json.dumps(input_audit, indent=2) + "\\n", encoding="utf-8")
write_attribution(manifest_rows, OUTPUT_DIR / "IMAGE_ATTRIBUTION.md")
fig, axes = plt.subplots(2, 2, figsize=(10, 10))
for axis, path in zip(axes.flat, actual_images):
    axis.imshow(Image.open(path)); axis.set_title(path.stem); axis.axis("off")
plt.tight_layout(); plt.show()
print("ĐẠT kiểm tra bộ ảnh. Đây phải là gói ZIP đã dùng trong CVAT; không thay ảnh hoặc tải bộ khác lên.")
''',
    ),
    code(
        "audit-own-yolo-export",
        '''# 3a — Tải lên và kiểm gói Ultralytics YOLO của chính bạn.
name, payload = read_one_upload(
    "/content/day2-my-export.zip",
    "Chọn đúng một Ultralytics YOLO Detection ZIP của bạn",
)
MY_YOLO_EXPORT = UPLOAD_DIR / "mine-yolo.zip"
MY_YOLO_EXPORT.write_bytes(payload)
my_audit, my_records = audit_yolo_export(
    MY_YOLO_EXPORT, WORK_DIR / "mine-yolo", manifest_rows, EXPECTED_CLASS_NAMES
)
write_audit_report(my_audit, OUTPUT_DIR / "my_export_audit.json")
print(json.dumps(public_audit_report(my_audit), ensure_ascii=False, indent=2))
if not my_audit["within_slide_workload_target"]:
    print("CẦN KIỂM TRA: số hộp ngoài khoảng 40–60. Ghi số thật và rà phạm vi; không vẽ ẩu để đủ số.")
''',
    ),
    code(
        "audit-own-native-export",
        '''# 3b — Tải lên gói CVAT gốc của cùng tác vụ để kiểm các thuộc tính.
native_name, native_payload = read_one_upload(
    "/content/day2-native-export.zip",
    "Chọn đúng một CVAT for images 1.1 ZIP của bạn",
)
MY_NATIVE_EXPORT = UPLOAD_DIR / "mine-native.zip"
MY_NATIVE_EXPORT.write_bytes(native_payload)
my_native_audit = audit_cvat_images_export(
    MY_NATIVE_EXPORT, WORK_DIR / "mine-native", manifest_rows, EXPECTED_CLASS_NAMES
)
same_state_audit = verify_same_annotation_state(
    my_records, my_native_audit["_records"], [row["image_id"] for row in manifest_rows]
)
my_native_audit["cross_format_consistency"] = same_state_audit
write_audit_report(my_native_audit, OUTPUT_DIR / "my_native_export_audit.json")
print(json.dumps(public_audit_report(my_native_audit), ensure_ascii=False, indent=2))
print("ĐẠT kiểm tra cùng trạng thái:", json.dumps(same_state_audit, ensure_ascii=False))
''',
    ),
    code(
        "read-real-yolo-row",
        '''# 3c — Đọc một dòng YOLO thật: lớp, tâm ngang, tâm dọc, chiều rộng, chiều cao.
if not my_records:
    print("CẦN KIỂM TRA: gói xuất không có hộp hợp lệ; quay lại CVAT, không tạo dòng giả để qua bước này.")
else:
    first_record = my_records[0]
    class_id = first_record["class_id"]
    x_center, y_center, width, height = first_record["bbox_xywh_normalized"]
    print("row:", [class_id, x_center, y_center, width, height])
    print(f"lớp={class_id} ({first_record['class_name']}) | tâm=({x_center:.4f}, {y_center:.4f}) | kích thước=({width:.4f}, {height:.4f})")
    print("pixel xyxy:", [round(v, 1) for v in first_record["bbox_xyxy_pixels"]])
    print("Câu hỏi cuối bước: vì sao dòng đúng định dạng vẫn có thể sai lớp, phạm vi hoặc hình học?")
''',
    ),
    code(
        "diagnostic-train-and-predict",
        '''# 4 — Huấn luyện và dự đoán thử trên ba ảnh huấn luyện, một ảnh kiểm tra.
# Đây không phải phép đánh giá chính thức và không phải điểm của người gán nhãn.
MODEL_ASSET = {
    "url": "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n.pt",
    "sha256": "0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1",
}
MODEL_PATH = download_with_sha256("yolo11n.pt", MODEL_ASSET["url"], WORK_DIR / "yolo11n.pt", MODEL_ASSET["sha256"])
DATA_YAML = build_training_dataset(my_audit, manifest_rows, EXPECTED_CLASS_NAMES, WORK_DIR / "dataset")
TRAIN_EPOCHS = 8
TRAIN_SEED = 42
DEVICE = 0 if torch.cuda.is_available() else "cpu"
started = time.time()
model = YOLO(str(MODEL_PATH))
train_result = model.train(
    data=str(DATA_YAML), epochs=TRAIN_EPOCHS, imgsz=640, batch=4, freeze=10,
    patience=3, seed=TRAIN_SEED, deterministic=True, device=DEVICE, workers=2,
    project=str(WORK_DIR / "runs"), name="day2-diagnostic", exist_ok=True, plots=True, verbose=False,
)
run_dir = Path(train_result.save_dir)
trained_model = YOLO(str(run_dir / "weights" / "best.pt"))
predict_image_id = next(row["image_id"] for row in manifest_rows if row["split"] == "val")
prediction = trained_model.predict(
    source=my_audit["images"][predict_image_id]["image_path"], conf=0.25, device=DEVICE, verbose=False
)[0]
prediction.save(filename=str(OUTPUT_DIR / "detect_result.jpg"))
training_run = {
    "purpose": "chỉ dùng để phản hồi và tìm lỗi dữ liệu",
    "not_production_benchmark": True,
    "ultralytics_version": ultralytics.__version__,
    "model_file": MODEL_PATH.name,
    "model_sha256": sha256_file(MODEL_PATH),
    "export_sha256": my_audit["archive_sha256"],
    "epochs": TRAIN_EPOCHS,
    "seed": TRAIN_SEED,
    "device": str(DEVICE),
    "train_image_ids": [r["image_id"] for r in manifest_rows if r["split"] == "train"],
    "val_image_ids": [r["image_id"] for r in manifest_rows if r["split"] == "val"],
    "elapsed_seconds": round(time.time() - started, 2),
}
(OUTPUT_DIR / "training_run.json").write_text(json.dumps(training_run, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(training_run, ensure_ascii=False, indent=2))
display(Image.open(OUTPUT_DIR / "detect_result.jpg"))
print("Hãy đọc kết quả dự đoán cụ thể; không dùng mAP của bốn ảnh để kết luận chất lượng người gán nhãn hay khả năng dùng trong thực tế.")
''',
    ),
    code(
        "choose-comparison-source",
        '''# 5a — Chọn nguồn đối chiếu sau khi bài riêng đã được kiểm và huấn luyện thử.
work_mode = input("Chọn 1 (cá nhân) hoặc 2 (theo cặp): ").strip()
if work_mode == "1":
    COMPARISON_ROLE = "teaching_reference"
    COMPARISON_LABEL = "bộ nhãn đối chiếu do Lab Coach cấp"
elif work_mode == "2":
    COMPARISON_ROLE = "peer"
    COMPARISON_LABEL = "gói YOLO độc lập của bạn cùng cặp"
else:
    raise ValueError("Chỉ nhập 1 hoặc 2. Chạy lại cell này.")
print("Nguồn đối chiếu:", COMPARISON_LABEL)
''',
    ),
    code(
        "audit-comparison-export",
        '''# 5b — Tải nguồn đối chiếu lên. Không dùng lại gói xuất của chính bạn.
comparison_name, comparison_payload = read_one_upload(
    "/content/day2-comparison-export.zip",
    f"Chọn ZIP của {COMPARISON_LABEL}",
)
COMPARISON_YOLO_EXPORT = UPLOAD_DIR / "comparison.zip"
COMPARISON_YOLO_EXPORT.write_bytes(comparison_payload)
if sha256_file(COMPARISON_YOLO_EXPORT) == my_audit["archive_sha256"]:
    raise ValueError("Nguồn đối chiếu trùng gói xuất của bạn; cần một nguồn độc lập.")
comparison_audit, comparison_records = audit_yolo_export(
    COMPARISON_YOLO_EXPORT, WORK_DIR / "comparison", manifest_rows, EXPECTED_CLASS_NAMES
)
print(f"ĐẠT kiểm tra nguồn đối chiếu | nguồn={COMPARISON_ROLE} | số vật thể={comparison_audit['object_count']}")
''',
    ),
    code(
        "cross-iou-comparison",
        '''# 5c — Đối chiếu IoU: ghép theo hình học, rồi báo riêng lớp và các hộp không ghép được.
comparison_ids = [row["image_id"] for row in manifest_rows if row["role"] == "comparison"]
COMPARISON_IOU_FLOOR = 0.01  # tham số ghép kỹ thuật, KHÔNG phải ngưỡng đạt
comparison_summary, comparison_rows = compare_annotation_records(
    my_records, comparison_records, comparison_ids, COMPARISON_ROLE, COMPARISON_IOU_FLOOR
)
comparison_summary["comparison_export_sha256"] = comparison_audit["archive_sha256"]
write_annotation_comparison(comparison_summary, comparison_rows, OUTPUT_DIR)
create_comparison_overlay(
    my_audit, my_records, comparison_records, comparison_ids,
    OUTPUT_DIR / "comparison_overlay.png", COMPARISON_ROLE,
)
print(json.dumps(comparison_summary, ensure_ascii=False, indent=2))
display(Image.open(OUTPUT_DIR / "comparison_overlay.png"))
print(comparison_summary["interpretation_warning"])
''',
    ),
    markdown(
        "rework-and-report",
        """## 6 — Sửa nhãn có căn cứ

Mở ảnh phủ hộp, các báo cáo JSON, ảnh dự đoán và hai tệp mẫu. Chọn một điểm khác biệt về phạm vi, lớp hoặc hình
học; dẫn quy tắc, sửa trong CVAT nếu cần, rồi mô tả trước và sau khi sửa. Không sửa TXT bằng tay để làm chỉ số
đẹp hơn. Cả hình thức cá nhân và theo cặp đều nộp cùng một bộ minh chứng.
""",
    ),
    code(
        "validate-and-package",
        '''# 7 — Kiểm tra và tạo ZIP chuyển tệp cho kho GitHub cá nhân.
# ZIP này chỉ giúp tải tệp từ Colab về máy, không phải bài nộp trên VLearn.
# Không đưa gói xuất thô, bộ nhãn đối chiếu hoặc trọng số mô hình vào kho cá nhân.
required_outputs = {
    "IMAGE_ATTRIBUTION.md", "input_pool_audit.json", "my_export_audit.json",
    "my_native_export_audit.json", "training_run.json", "detect_result.jpg",
    "comparison_iou.csv", "comparison_summary.json", "comparison_overlay.png",
}
actual_outputs = {path.name for path in OUTPUT_DIR.iterdir() if path.is_file()}
missing = required_outputs - actual_outputs
if missing:
    raise ValueError(f"Thiếu output: {sorted(missing)}")
for path in (REPORT_PATH, GUIDELINE_PATH):
    if not path.is_file():
        raise ValueError(f"Thiếu {path}")
    text = path.read_text(encoding="utf-8")
    if "CHƯA ĐIỀN" in text:
        raise ValueError(f"{path.name} còn placeholder; mở file và điền trước khi chạy lại.")

staging = Path("day2_repository_staging")
if staging.exists():
    shutil.rmtree(staging)
(staging / OUTPUT_DIR.name).mkdir(parents=True)
shutil.copy2(REPORT_PATH, staging / REPORT_PATH.name)
shutil.copy2(GUIDELINE_PATH, staging / GUIDELINE_PATH.name)
for filename in sorted(required_outputs):
    shutil.copy2(OUTPUT_DIR / filename, staging / OUTPUT_DIR.name / filename)
student_name = input("Nhập họ tên không dấu, nối các từ bằng dấu gạch ngang: ").strip()
student_id = input("Nhập MSSV: ").strip()
if not re.fullmatch(r"[A-Za-z]+(?:-[A-Za-z]+)+", student_name):
    raise ValueError("Họ tên phải không dấu và có dấu gạch ngang, ví dụ Nguyen-Van-An.")
if not re.fullmatch(r"[A-Za-z0-9_-]{4,24}", student_id):
    raise ValueError("MSSV chỉ dùng chữ, số, dấu gạch ngang hoặc gạch dưới; độ dài từ 4 đến 24 ký tự.")
repository_name = f"KX-DAY02-{student_name}-{student_id}"
transfer_archive = Path(f"{repository_name}-repo-files.zip")
with zipfile.ZipFile(transfer_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(staging.rglob("*")):
        if path.is_file():
            archive.write(path, path.relative_to(staging))
roots = {Path(name).parts[0] for name in zipfile.ZipFile(transfer_archive).namelist()}
assert roots == {"REPORT.md", "GUIDELINE_MINI_SHEET.md", "day2_lab_outputs"}
assert zipfile.ZipFile(transfer_archive).testzip() is None
print("ĐẠT kiểm tra tệp cho kho cá nhân:", repository_name)
print("Tải gói chuyển tệp về máy:", transfer_archive.resolve())
print("Giải nén, đưa ba mục ở cấp đầu lên kho GitHub cá nhân, rồi nộp đường dẫn kho trên VLearn.")
''',
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"name": "day2-detection-quality.ipynb", "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(TARGET)

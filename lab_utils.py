"""Các hàm hỗ trợ đã kiểm thử và được nhúng vào sổ thực hành Ngày 2."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import ssl
import stat
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path, PurePosixPath

import numpy as np
import yaml
import certifi
from PIL import Image, ImageDraw
from scipy.optimize import linear_sum_assignment


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
EXPECTED_CLASS_NAMES = ["car", "truck", "bus", "van"]
REQUIRED_ATTRIBUTE_VALUES = {
    "visibility": {"clear", "occluded", "unclear"},
    "boundary": {"inside", "truncated"},
    "review_state": {"confident", "needs_review"},
}


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_with_sha256(label: str, url: str, target: str | Path, expected: str) -> Path:
    """Tải tệp theo cách an toàn và từ chối nội dung sai mã SHA-256."""
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and sha256_file(target) == expected:
        return target
    if target.exists():
        target.unlink()
    temporary = target.with_name(f".{target.name}.download")
    if temporary.exists():
        temporary.unlink()
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "AI20K-Day2-Lab/1.0"})
        tls_context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=60, context=tls_context) as response, temporary.open("wb") as output:
            shutil.copyfileobj(response, output)
        actual = sha256_file(temporary)
        if actual != expected:
            raise ValueError(f"Checksum sai cho {label}: expected={expected}, actual={actual}")
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return target


def read_manifest(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("Image manifest rỗng")
    required = {
        "image_id",
        "local_path",
        "sha256",
        "width",
        "height",
        "split",
        "role",
        "origin_claim",
        "origin_record_status",
        "starter_repository",
        "starter_commit",
        "license_claim",
        "license_url",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"Manifest thiếu cột: {sorted(missing)}")
    seen = set()
    for row in rows:
        if row["image_id"] in seen:
            raise ValueError(f"Manifest lặp image_id: {row['image_id']}")
        seen.add(row["image_id"])
        row["width"] = int(row["width"])
        row["height"] = int(row["height"])
        if row["split"] not in {"train", "val"}:
            raise ValueError(f"Split không hợp lệ: {row['split']}")
        if len(row["sha256"]) != 64:
            raise ValueError(f"SHA-256 không hợp lệ: {row['image_id']}")
    return rows


def safe_extract_zip(archive_path: str | Path, destination: str | Path, max_bytes: int = 300_000_000) -> Path:
    """Giải nén an toàn, chặn đường dẫn thoát, liên kết mềm và gói ZIP quá lớn."""
    archive_path = Path(archive_path)
    destination = Path(destination)
    with zipfile.ZipFile(archive_path) as archive:
        total = 0
        for item in archive.infolist():
            parts = PurePosixPath(item.filename).parts
            if not parts or item.filename.startswith(("/", "\\")) or ".." in parts:
                raise ValueError(f"ZIP có đường dẫn không an toàn: {item.filename}")
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError(f"ZIP chứa symlink không được phép: {item.filename}")
            total += item.file_size
            if total > max_bytes:
                raise ValueError("ZIP vượt giới hạn 300 MB của lab")
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        archive.extractall(destination)
    return destination


def _normalize_names(raw_names) -> list[str]:
    if isinstance(raw_names, list):
        return [str(value) for value in raw_names]
    if isinstance(raw_names, dict):
        pairs = sorted((int(key), str(value)) for key, value in raw_names.items())
        if [key for key, _ in pairs] != list(range(len(pairs))):
            raise ValueError("Class IDs trong data.yaml phải liên tiếp từ 0")
        return [value for _, value in pairs]
    raise ValueError("data.yaml phải có names dạng list hoặc mapping")


def _find_yolo_root(extracted: Path) -> tuple[Path, list[str]]:
    candidates = sorted({*extracted.rglob("data.yaml"), *extracted.rglob("dataset.yaml")})
    for candidate in candidates:
        data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "names" in data:
            return candidate.parent, _normalize_names(data["names"])
    raise ValueError("Không tìm thấy data.yaml/dataset.yaml có class names trong YOLO export")


def _unique_stem_map(paths: list[Path], kind: str) -> dict[str, Path]:
    result = {}
    for path in paths:
        stem = path.stem
        if stem in result:
            raise ValueError(f"Có hai {kind} trùng stem `{stem}`")
        result[stem] = path
    return result


def _parse_label_file(path: Path, image_id: str, width: int, height: int, names: list[str]) -> list[dict]:
    records = []
    for row_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        values = line.split()
        if len(values) != 5:
            raise ValueError(f"{path.name}:{row_number} cần đúng 5 trường, nhận {len(values)}")
        try:
            class_id = int(values[0])
            x_center, y_center, box_width, box_height = map(float, values[1:])
        except ValueError as error:
            raise ValueError(f"{path.name}:{row_number} có giá trị không phải số") from error
        coords = (x_center, y_center, box_width, box_height)
        if not all(math.isfinite(value) for value in coords):
            raise ValueError(f"{path.name}:{row_number} có NaN/Infinity")
        if not 0 <= class_id < len(names):
            raise ValueError(f"{path.name}:{row_number} có class_id ngoài schema: {class_id}")
        if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
            raise ValueError(f"{path.name}:{row_number} có tâm ngoài [0,1]")
        if not (0 < box_width <= 1 and 0 < box_height <= 1):
            raise ValueError(f"{path.name}:{row_number} có width/height không hợp lệ")
        x1 = x_center - box_width / 2
        y1 = y_center - box_height / 2
        x2 = x_center + box_width / 2
        y2 = y_center + box_height / 2
        if min(x1, y1) < -1e-6 or max(x2, y2) > 1 + 1e-6:
            raise ValueError(f"{path.name}:{row_number} có box vượt biên ảnh")
        records.append(
            {
                "image_id": image_id,
                "row_number": row_number,
                "class_id": class_id,
                "class_name": names[class_id],
                "bbox_xywh_normalized": [x_center, y_center, box_width, box_height],
                "bbox_xyxy_normalized": [max(0, x1), max(0, y1), min(1, x2), min(1, y2)],
                "bbox_xyxy_pixels": [x1 * width, y1 * height, x2 * width, y2 * height],
            }
        )
    return records


def audit_yolo_export(
    archive_path: str | Path,
    destination: str | Path,
    manifest_rows: list[dict],
    expected_names: list[str] | None = None,
) -> tuple[dict, list[dict]]:
    expected_names = expected_names or EXPECTED_CLASS_NAMES
    extracted = safe_extract_zip(archive_path, destination)
    root, names = _find_yolo_root(extracted)
    if names != expected_names:
        raise ValueError(f"Schema export {names} không khớp schema lớp {expected_names}")

    image_paths = [path for path in root.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES]
    label_paths = [path for path in root.rglob("*.txt") if "labels" in path.parts]
    images = _unique_stem_map(image_paths, "ảnh")
    labels = _unique_stem_map(label_paths, "label")
    expected_ids = [row["image_id"] for row in manifest_rows]
    expected_id_set = set(expected_ids)
    extra_images = sorted(set(images) - expected_id_set)
    extra_labels = sorted(set(labels) - expected_id_set)
    if extra_images or extra_labels:
        raise ValueError(f"YOLO export có file ngoài pool; ảnh thừa={extra_images}, label thừa={extra_labels}")
    records = []
    image_details = {}
    manifest_by_id = {row["image_id"]: row for row in manifest_rows}
    for image_id in expected_ids:
        if image_id not in images:
            raise ValueError(f"YOLO export thiếu ảnh `{image_id}`; hãy bật export kèm ảnh")
        if image_id not in labels:
            raise ValueError(f"YOLO export thiếu label `{image_id}.txt`")
        with Image.open(images[image_id]) as image:
            image.verify()
        with Image.open(images[image_id]) as image:
            width, height = image.size
        expected = manifest_by_id[image_id]
        if (width, height) != (expected["width"], expected["height"]):
            raise ValueError(
                f"Kích thước `{image_id}` là {width}x{height}, cần {expected['width']}x{expected['height']}"
            )
        image_records = _parse_label_file(labels[image_id], image_id, width, height, names)
        records.extend(image_records)
        class_counts = {name: 0 for name in names}
        for record in image_records:
            class_counts[record["class_name"]] += 1
        image_details[image_id] = {
            "image_path": str(images[image_id]),
            "label_path": str(labels[image_id]),
            "width": width,
            "height": height,
            "object_count": len(image_records),
            "class_count": class_counts,
        }
    object_count = len(records)
    report = {
        "archive_name": Path(archive_path).name,
        "archive_sha256": sha256_file(archive_path),
        "class_names": names,
        "image_ids": expected_ids,
        "image_count": len(expected_ids),
        "object_count": object_count,
        "within_slide_workload_target": 40 <= object_count <= 60,
        "coordinate_format": "normalized xywh",
        "images": image_details,
    }
    return report, records


def public_audit_report(report: dict) -> dict:
    """Loại đường dẫn cục bộ khỏi báo cáo trước khi nộp."""
    clean = json.loads(json.dumps(report))
    clean.pop("_records", None)
    for details in clean.get("images", {}).values():
        details.pop("image_path", None)
        details.pop("label_path", None)
    return clean


def write_audit_report(report: dict, target: str | Path) -> Path:
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(public_audit_report(report), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def audit_cvat_images_export(
    archive_path: str | Path,
    destination: str | Path,
    manifest_rows: list[dict],
    expected_names: list[str] | None = None,
) -> dict:
    """Kiểm dữ liệu XML và thuộc tính mà định dạng YOLO không giữ lại."""
    expected_names = expected_names or EXPECTED_CLASS_NAMES
    extracted = safe_extract_zip(archive_path, destination)
    annotation_files = sorted(extracted.rglob("annotations.xml"))
    if len(annotation_files) != 1:
        raise ValueError("CVAT-native export cần đúng một file annotations.xml")
    try:
        root = ET.parse(annotation_files[0]).getroot()
    except ET.ParseError as error:
        raise ValueError("annotations.xml của CVAT không đọc được") from error

    manifest_by_id = {row["image_id"]: row for row in manifest_rows}
    images_by_id = {}
    for image in root.findall("image"):
        image_id = Path(image.attrib.get("name", "")).stem
        if image_id in images_by_id:
            raise ValueError(f"CVAT-native export có hai image trùng ID `{image_id}`")
        images_by_id[image_id] = image

    expected_ids = [row["image_id"] for row in manifest_rows]
    if set(images_by_id) != set(expected_ids):
        missing = sorted(set(expected_ids) - set(images_by_id))
        unexpected = sorted(set(images_by_id) - set(expected_ids))
        raise ValueError(f"CVAT-native export sai image IDs; thiếu={missing}, thừa={unexpected}")

    attribute_counts = {name: 0 for name in REQUIRED_ATTRIBUTE_VALUES}
    object_count = 0
    per_image = {}
    native_records = []
    for image_id in expected_ids:
        image = images_by_id[image_id]
        expected = manifest_by_id[image_id]
        try:
            width = int(image.attrib["width"])
            height = int(image.attrib["height"])
        except (KeyError, ValueError) as error:
            raise ValueError(f"CVAT-native image `{image_id}` thiếu width/height hợp lệ") from error
        if (width, height) != (expected["width"], expected["height"]):
            raise ValueError(
                f"Kích thước CVAT-native `{image_id}` là {width}x{height}, "
                f"cần {expected['width']}x{expected['height']}"
            )
        boxes = image.findall("box")
        non_boxes = [child.tag for child in image if child.tag != "box"]
        if non_boxes:
            raise ValueError(f"CVAT-native `{image_id}` có shape không phải rectangle: {non_boxes}")
        for row_number, box in enumerate(boxes, start=1):
            label = box.attrib.get("label")
            if label not in expected_names:
                raise ValueError(f"CVAT-native `{image_id}` box {row_number} có class lạ `{label}`")
            try:
                xtl, ytl, xbr, ybr = (float(box.attrib[key]) for key in ("xtl", "ytl", "xbr", "ybr"))
            except (KeyError, ValueError) as error:
                raise ValueError(f"CVAT-native `{image_id}` box {row_number} có tọa độ không hợp lệ") from error
            coords = (xtl, ytl, xbr, ybr)
            if not all(math.isfinite(value) for value in coords) or not (0 <= xtl < xbr <= width and 0 <= ytl < ybr <= height):
                raise ValueError(f"CVAT-native `{image_id}` box {row_number} vượt biên hoặc có diện tích không dương")
            attributes = {}
            for attribute in box.findall("attribute"):
                name = attribute.attrib.get("name")
                if name in attributes:
                    raise ValueError(f"CVAT-native `{image_id}` box {row_number} lặp attribute `{name}`")
                attributes[name] = (attribute.text or "").strip()
            if set(attributes) != set(REQUIRED_ATTRIBUTE_VALUES):
                raise ValueError(
                    f"CVAT-native `{image_id}` box {row_number} cần đúng attributes "
                    f"{sorted(REQUIRED_ATTRIBUTE_VALUES)}, nhận {sorted(attributes)}"
                )
            for name, allowed_values in REQUIRED_ATTRIBUTE_VALUES.items():
                if attributes[name] not in allowed_values:
                    raise ValueError(
                        f"CVAT-native `{image_id}` box {row_number} có {name}=`{attributes[name]}` không hợp lệ"
                    )
                attribute_counts[name] += 1
            native_records.append(
                {
                    "image_id": image_id,
                    "row_number": row_number,
                    "class_id": expected_names.index(label),
                    "class_name": label,
                    "bbox_xyxy_normalized": [xtl / width, ytl / height, xbr / width, ybr / height],
                }
            )
            object_count += 1
        class_counts = {name: 0 for name in expected_names}
        for record in native_records:
            if record["image_id"] == image_id:
                class_counts[record["class_name"]] += 1
        per_image[image_id] = {
            "width": width,
            "height": height,
            "object_count": len(boxes),
            "class_count": class_counts,
        }
    return {
        "archive_name": Path(archive_path).name,
        "archive_sha256": sha256_file(archive_path),
        "format": "CVAT for images XML",
        "class_names": expected_names,
        "image_ids": expected_ids,
        "image_count": len(expected_ids),
        "object_count": object_count,
        "within_slide_workload_target": 40 <= object_count <= 60,
        "required_attributes": sorted(REQUIRED_ATTRIBUTE_VALUES),
        "attribute_value_count_by_name": attribute_counts,
        "images": per_image,
        "_records": native_records,
    }


def verify_same_annotation_state(
    yolo_records: list[dict],
    native_records: list[dict],
    image_ids: list[str],
    minimum_iou: float = 0.995,
) -> dict:
    """Xác minh hai bản xuất giữ cùng lớp và hình học hộp, cho phép sai số làm tròn nhỏ."""
    if not 0 < minimum_iou <= 1:
        raise ValueError("minimum_iou phải nằm trong (0,1]")
    yolo_by_key = defaultdict(list)
    native_by_key = defaultdict(list)
    for record in yolo_records:
        yolo_by_key[(record["image_id"], record["class_name"])].append(record)
    for record in native_records:
        native_by_key[(record["image_id"], record["class_name"])].append(record)

    matched_ious = []
    for image_id in image_ids:
        for class_name in EXPECTED_CLASS_NAMES:
            left = yolo_by_key[(image_id, class_name)]
            right = native_by_key[(image_id, class_name)]
            if len(left) != len(right):
                raise AssertionError(
                    f"Hai gói xuất khác số hộp lớp `{class_name}` ở ảnh `{image_id}`: "
                    f"YOLO={len(left)}, CVAT={len(right)}. Xuất lại cả hai từ cùng trạng thái."
                )
            if not left:
                continue
            matrix = np.zeros((len(left), len(right)), dtype=float)
            for left_index, left_record in enumerate(left):
                for right_index, right_record in enumerate(right):
                    matrix[left_index, right_index] = box_iou(
                        left_record["bbox_xyxy_normalized"], right_record["bbox_xyxy_normalized"]
                    )
            left_indices, right_indices = linear_sum_assignment(-matrix)
            class_ious = [float(matrix[i, j]) for i, j in zip(left_indices, right_indices)]
            if class_ious and min(class_ious) < minimum_iou:
                raise AssertionError(
                    f"Hai gói xuất khác hình học hộp ở ảnh `{image_id}`, lớp `{class_name}`; "
                    f"IoU nhỏ nhất={min(class_ious):.6f}. Xuất lại cả hai từ cùng trạng thái."
                )
            matched_ious.extend(class_ious)
    if len(yolo_records) != len(native_records):
        raise AssertionError("Hai gói xuất khác tổng số hộp; xuất lại cả hai từ cùng trạng thái.")
    return {
        "same_annotation_state": True,
        "matched_box_count": len(matched_ious),
        "minimum_cross_format_iou": min(matched_ious) if matched_ious else None,
        "geometry_iou_floor": minimum_iou,
    }


def box_iou(left: list[float], right: list[float]) -> float:
    x1 = max(left[0], right[0])
    y1 = max(left[1], right[1])
    x2 = min(left[2], right[2])
    y2 = min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def compare_annotation_records(
    mine: list[dict],
    comparison: list[dict],
    calibration_ids: list[str],
    comparison_source: str,
    comparison_iou_floor: float = 0.01,
) -> tuple[dict, list[dict]]:
    """Đối chiếu bài độc lập với bạn cùng cặp hoặc bộ nhãn do Lab Coach cấp."""
    if not 0 <= comparison_iou_floor <= 1:
        raise ValueError("comparison_iou_floor phải nằm trong [0,1]")
    if comparison_source not in {"peer", "teaching_reference"}:
        raise ValueError("comparison_source phải là peer hoặc teaching_reference")
    mine_by_image = defaultdict(list)
    comparison_by_image = defaultdict(list)
    for record in mine:
        mine_by_image[record["image_id"]].append(record)
    for record in comparison:
        comparison_by_image[record["image_id"]].append(record)

    rows = []
    unmatched_mine = 0
    unmatched_comparison = 0
    for image_id in calibration_ids:
        left = mine_by_image[image_id]
        right = comparison_by_image[image_id]
        matrix = np.zeros((len(left), len(right)), dtype=float)
        for i, left_record in enumerate(left):
            for j, right_record in enumerate(right):
                matrix[i, j] = box_iou(
                    left_record["bbox_xyxy_normalized"], right_record["bbox_xyxy_normalized"]
                )
        candidates = []
        if matrix.size:
            left_indices, right_indices = linear_sum_assignment(-matrix)
            candidates = list(zip(left_indices.tolist(), right_indices.tolist()))
        matched_left = set()
        matched_right = set()
        for left_index, right_index in candidates:
            iou = float(matrix[left_index, right_index])
            if iou < comparison_iou_floor:
                continue
            matched_left.add(left_index)
            matched_right.add(right_index)
            left_record = left[left_index]
            right_record = right[right_index]
            rows.append(
                {
                    "image_id": image_id,
                    "mine_row": left_record["row_number"],
                    "comparison_row": right_record["row_number"],
                    "iou": round(iou, 6),
                    "mine_class": left_record["class_name"],
                    "comparison_class": right_record["class_name"],
                    "class_agree": left_record["class_id"] == right_record["class_id"],
                }
            )
        unmatched_mine += len(left) - len(matched_left)
        unmatched_comparison += len(right) - len(matched_right)

    ious = [row["iou"] for row in rows]
    class_agreements = [row["class_agree"] for row in rows]
    if comparison_source == "peer":
        interpretation_warning = (
            "Mức đồng thuận giữa hai người đo khả năng tái lập quy tắc, không chứng minh cả hai đều đúng."
        )
    else:
        interpretation_warning = (
            "Bộ nhãn đối chiếu hỗ trợ phản hồi sau bài làm độc lập; đây không phải kết luận chất lượng sản xuất."
        )
    summary = {
        "matching": "ghép tối ưu theo IoU hình học, không dùng lớp khi ghép",
        "comparison_iou_floor": comparison_iou_floor,
        "floor_is_official_pass_threshold": False,
        "calibration_image_ids": calibration_ids,
        "matched_boxes": len(rows),
        "mean_iou": round(float(np.mean(ious)), 6) if ious else None,
        "median_iou": round(float(np.median(ious)), 6) if ious else None,
        "class_agreement": round(sum(class_agreements) / len(class_agreements), 6) if class_agreements else None,
        "unmatched_mine": unmatched_mine,
        "unmatched_comparison": unmatched_comparison,
        "comparison_source": comparison_source,
        "interpretation_warning": interpretation_warning,
    }
    return summary, rows


def write_annotation_comparison(summary: dict, rows: list[dict], output_dir: str | Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "comparison_summary.json"
    csv_path = output_dir / "comparison_iou.csv"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = [
        "image_id", "mine_row", "comparison_row", "iou", "mine_class", "comparison_class", "class_agree"
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return summary_path, csv_path


def create_comparison_overlay(
    mine_report: dict,
    mine_records: list[dict],
    comparison_records: list[dict],
    calibration_ids: list[str],
    target: str | Path,
    comparison_source: str,
) -> Path:
    cards = []
    mine_by_image = defaultdict(list)
    comparison_by_image = defaultdict(list)
    for record in mine_records:
        mine_by_image[record["image_id"]].append(record)
    for record in comparison_records:
        comparison_by_image[record["image_id"]].append(record)
    for image_id in calibration_ids:
        image_path = mine_report["images"][image_id]["image_path"]
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        for record in mine_by_image[image_id]:
            draw.rectangle(record["bbox_xyxy_pixels"], outline="#ff304f", width=3)
        for record in comparison_by_image[image_id]:
            draw.rectangle(record["bbox_xyxy_pixels"], outline="#00a8ff", width=3)
        image.thumbnail((720, 480))
        card = Image.new("RGB", (740, 530), "white")
        card.paste(image, ((740 - image.width) // 2, 35))
        comparison_label = "bạn cùng cặp" if comparison_source == "peer" else "bộ nhãn đối chiếu"
        ImageDraw.Draw(card).text((12, 10), f"{image_id} | đỏ: tôi | xanh: {comparison_label}", fill="black")
        cards.append(card)
    canvas = Image.new("RGB", (740, 530 * len(cards)), "#dddddd")
    for index, card in enumerate(cards):
        canvas.paste(card, (0, index * 530))
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, quality=92)
    return target


def build_training_dataset(
    report: dict,
    manifest_rows: list[dict],
    class_names: list[str],
    destination: str | Path,
) -> Path:
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    for split in ("train", "val"):
        (destination / "images" / split).mkdir(parents=True, exist_ok=True)
        (destination / "labels" / split).mkdir(parents=True, exist_ok=True)
    for row in manifest_rows:
        image_id = row["image_id"]
        split = row["split"]
        details = report["images"][image_id]
        image_source = Path(details["image_path"])
        label_source = Path(details["label_path"])
        shutil.copy2(image_source, destination / "images" / split / image_source.name)
        shutil.copy2(label_source, destination / "labels" / split / f"{image_id}.txt")
    config = {
        "path": str(destination.resolve()),
        "train": "images/train",
        "val": "images/val",
        "names": {index: name for index, name in enumerate(class_names)},
    }
    yaml_path = destination / "data.yaml"
    yaml_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return yaml_path


def write_attribution(manifest_rows: list[dict], target: str | Path) -> Path:
    lines = [
        "# Nguồn gốc ảnh",
        "",
        "Bốn ảnh giao thông được lấy nguyên vẹn từ kho nguồn của giảng viên tại phiên bản Git đã ghi bên dưới.",
        "Kho nguồn cho biết ảnh bắt nguồn từ UA-DETRAC qua một bản tái xuất trên Hugging Face và thẻ dữ liệu khi đó công bố CC BY 4.0.",
        "Kho nguồn đã đổi tên ảnh và không giữ mã bản ghi gốc; liên kết bản tái xuất hiện không còn truy cập được. Đây là giới hạn truy nguyên được công bố rõ, không phải xác minh pháp lý độc lập.",
        "Ảnh phủ hộp và ảnh dự đoán là sản phẩm đã chỉnh sửa; các quyền khác vẫn có thể áp dụng.",
        "",
        "| Mã ảnh | Công bố nguồn / trạng thái bản ghi | Kho nguồn và phiên bản | Công bố giấy phép | SHA-256 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in manifest_rows:
        lines.append(
            f"| `{row['image_id']}` | {row['origin_claim']} / {row['origin_record_status']} | "
            f"[{row['starter_commit'][:7]}]({row['starter_repository']}/tree/{row['starter_commit']}) | "
            f"[{row['license_claim']}]({row['license_url']}) | "
            f"`{row['sha256']}` |"
        )
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target

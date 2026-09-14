import ast
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "day2-detection-quality.ipynb"
CLASS_NAMES = ["car", "truck", "bus", "van"]
INPUT_ZIP_SHA256 = "f7d99888f21440fb0374d84962b93213bd8c14e665d093cc8d37f4c61b71ed33"


def load_lab_utils():
    spec = importlib.util.spec_from_file_location("lab_utils", ROOT / "lab_utils.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


LAB = load_lab_utils()


class RepositoryContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        cls.code_source = "\n".join(
            "".join(cell.get("source", []))
            for cell in cls.notebook["cells"]
            if cell.get("cell_type") == "code"
        )
        cls.markdown_source = "\n".join(
            "".join(cell.get("source", []))
            for cell in cls.notebook["cells"]
            if cell.get("cell_type") == "markdown"
        )
        cls.cell_ids = [cell.get("id") for cell in cls.notebook["cells"]]

    def test_notebook_is_clean_valid_and_python_parses(self):
        self.assertEqual(self.notebook["nbformat"], 4)
        self.assertTrue(all(self.cell_ids))
        self.assertEqual(len(self.cell_ids), len(set(self.cell_ids)))
        code_cells = [cell for cell in self.notebook["cells"] if cell["cell_type"] == "code"]
        self.assertTrue(all(cell["execution_count"] is None for cell in code_cells))
        self.assertTrue(all(cell["outputs"] == [] for cell in code_cells))
        ast.parse("\n".join(line for line in self.code_source.splitlines() if not line.startswith("%")))

    def test_notebook_generator_is_reproducible(self):
        before = NOTEBOOK_PATH.read_bytes()
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build-notebook.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(before, NOTEBOOK_PATH.read_bytes())

    def test_four_hour_schedule_is_contiguous_and_contains_45_minute_sprint(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        ranges = [tuple(map(int, match)) for match in re.findall(r"^\| (\d+)[–-](\d+) \|", readme, re.M)]
        self.assertEqual(ranges[0], (0, 15))
        self.assertEqual(ranges[-1], (235, 240))
        self.assertEqual(sum(end - start for start, end in ranges), 240)
        self.assertTrue(all(left[1] == right[0] for left, right in zip(ranges, ranges[1:])))
        self.assertIn((50, 95), ranges)
        self.assertIn("45 phút", readme)

    def test_manifest_and_input_zip_are_fixed_without_answer_counts(self):
        manifest_path = ROOT / "data" / "image-manifest.csv"
        with manifest_path.open(encoding="utf-8", newline="") as stream:
            fieldnames = csv.DictReader(stream).fieldnames
        self.assertNotIn("reviewed_eligible_objects", fieldnames)
        self.assertNotIn("source_repository", fieldnames)
        self.assertIn("origin_record_status", fieldnames)
        self.assertIn("starter_repository", fieldnames)
        self.assertIn("starter_commit", fieldnames)

        rows = LAB.read_manifest(manifest_path)
        self.assertEqual(len(rows), 4)
        self.assertEqual({row["role"] for row in rows}, {"comparison"})
        self.assertEqual(sum(row["split"] == "train" for row in rows), 3)
        self.assertEqual(sum(row["split"] == "val" for row in rows), 1)
        for row in rows:
            image_path = ROOT / row["local_path"]
            self.assertTrue(image_path.is_file())
            self.assertEqual(file_sha256(image_path), row["sha256"])
            with Image.open(image_path) as image:
                self.assertEqual(image.size, (640, 640))

        archive_path = ROOT / "data" / "day2-cvat-input.zip"
        self.assertEqual(file_sha256(archive_path), INPUT_ZIP_SHA256)
        with zipfile.ZipFile(archive_path) as archive:
            names = sorted(archive.namelist())
        self.assertEqual(names, sorted(f"{row['image_id']}.jpg" for row in rows))
        self.assertFalse(any(Path(name).suffix.lower() in {".txt", ".xml", ".yaml", ".yml"} for name in names))

    def test_direct_zip_distribution_is_explicit(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "GUIDE.md").read_text(encoding="utf-8")
        html = (ROOT / "docs" / "day2-e2e-guide.html").read_text(encoding="utf-8")
        verify_cell = next(cell for cell in self.notebook["cells"] if cell.get("id") == "verify-cvat-input")
        verify_source = "".join(verify_cell["source"])
        self.assertIn("không cần chạy sổ thực hành để tạo hoặc tải ảnh", " ".join(readme.split()))
        self.assertIn("Chưa cần mở sổ thực hành", guide)
        self.assertIn("Chưa cần mở sổ thực hành để lấy ảnh", html)
        self.assertIn("không tạo hoặc tải ảnh", verify_source)
        self.assertLess(self.cell_ids.index("cvat-independent-work"), self.cell_ids.index("install-pinned-dependencies"))

    def test_private_repository_uses_colab_upload_instead_of_github_import(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("colab.research.google.com/github/", readme)
        self.assertIn("notebooks/day2-detection-quality.ipynb", readme)
        self.assertIn("Upload notebook (Tải sổ tay lên)", readme)
        self.assertIn("repo đang ở chế độ riêng tư", readme)

    def test_student_repository_excludes_internal_material(self):
        forbidden_paths = (
            "instructor",
            "gold_train_labels",
            "LAB_COACH_TEST_RUNBOOK.md",
            "DESIGN_RATIONALE.md",
            "scripts/build-teaching-reference.py",
        )
        for relative_path in forbidden_paths:
            self.assertFalse((ROOT / relative_path).exists(), relative_path)
        for archive in ROOT.rglob("*.zip"):
            self.assertNotIn("teaching-reference", archive.name)

    def test_learner_surfaces_do_not_disclose_reference_counts(self):
        learner_paths = [
            ROOT / "README.md",
            ROOT / "GUIDE.md",
            ROOT / "RUBRIC.md",
            ROOT / "data" / "README.md",
            ROOT / "docs" / "day2-e2e-guide.html",
            ROOT / "guideline-mini-sheet.md",
            NOTEBOOK_PATH,
        ]
        joined = "\n".join(path.read_text(encoding="utf-8") for path in learner_paths)
        self.assertNotIn("reviewed_eligible_objects", joined)
        self.assertNotIn("reviewed_workload_reference", joined)
        self.assertNotRegex(joined.casefold(), r"\b37\s+(?:car|cars)")
        self.assertNotIn("bốn ảnh được chọn để có khoảng", joined.casefold())

    def test_generated_attribution_uses_public_manifest_fields(self):
        rows = LAB.read_manifest(ROOT / "data" / "image-manifest.csv")
        with tempfile.TemporaryDirectory(prefix="day2-attribution-") as temporary:
            target = Path(temporary) / "IMAGE_ATTRIBUTION.md"
            LAB.write_attribution(rows, target)
            content = target.read_text(encoding="utf-8")
        self.assertIn("# Nguồn gốc ảnh", content)
        self.assertIn("UA-DETRAC", content)
        self.assertIn("CC BY 4.0", content)
        self.assertIn("không giữ mã bản ghi gốc", content)
        self.assertIn("710d2c157c5750f71271354d0d31b24457c64e7c", content)
        self.assertNotIn("instructor", content.casefold())

    def test_schema_attributes_and_vietnamese_explanations_are_consistent(self):
        self.assertEqual(LAB.EXPECTED_CLASS_NAMES, CLASS_NAMES)
        self.assertEqual(
            LAB.REQUIRED_ATTRIBUTE_VALUES,
            {
                "visibility": {"clear", "occluded", "unclear"},
                "boundary": {"inside", "truncated"},
                "review_state": {"confident", "needs_review"},
            },
        )
        documents = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("README.md", "GUIDE.md", "guideline-mini-sheet.md")
        )
        for phrase in (
            "`car` (ô tô con)",
            "`truck` (xe tải)",
            "`bus` (xe buýt)",
            "`van` (xe van)",
            "`visibility` (mức nhìn thấy)",
            "`boundary` (quan hệ với mép ảnh)",
            "`review_state` (trạng thái",
        ):
            self.assertIn(phrase, documents)

    def test_ultralytics_version_model_and_input_are_pinned(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(requirements, ["ultralytics==8.4.145", "certifi==2026.6.17"])
        self.assertIn("%pip -q install ultralytics==8.4.145 certifi==2026.6.17", self.code_source)
        self.assertIn("yolo11n.pt", self.code_source)
        self.assertIn("0ebbc80d4a7680d14987a577cd21342b65ecfd94632bd9a8da63ae6417644ee1", self.code_source)
        self.assertIn(INPUT_ZIP_SHA256, self.code_source)
        self.assertNotIn("install -U ultralytics", self.code_source)

    def test_notebook_order_matches_the_student_flow(self):
        expected_order = (
            "verify-cvat-input",
            "audit-own-yolo-export",
            "audit-own-native-export",
            "read-real-yolo-row",
            "diagnostic-train-and-predict",
            "choose-comparison-source",
            "audit-comparison-export",
            "cross-iou-comparison",
            "validate-and-package",
        )
        indices = [self.cell_ids.index(cell_id) for cell_id in expected_order]
        self.assertEqual(indices, sorted(indices))

    def test_real_yolo_row_cell_handles_empty_and_valid_records(self):
        cell = next(cell for cell in self.notebook["cells"] if cell.get("id") == "read-real-yolo-row")
        source = "".join(cell["source"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(source, {"my_records": []})
        self.assertIn("không có hộp hợp lệ", output.getvalue())

        output = io.StringIO()
        record = {
            "class_id": 2,
            "class_name": "bus",
            "bbox_xywh_normalized": [0.5, 0.4, 0.2, 0.3],
            "bbox_xyxy_pixels": [256.0, 160.0, 384.0, 352.0],
        }
        with contextlib.redirect_stdout(output):
            exec(source, {"my_records": [record]})
        self.assertIn("row: [2, 0.5, 0.4, 0.2, 0.3]", output.getvalue())
        self.assertIn("lớp=2", output.getvalue())

    def test_individual_and_pair_share_the_same_independent_core(self):
        documents = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("README.md", "GUIDE.md", "docs/day2-e2e-guide.html")
        ).casefold()
        for phrase in ("cá nhân", "theo cặp", "độc lập", "không chia ảnh"):
            self.assertIn(phrase, documents + self.code_source.casefold())
        self.assertIn('work_mode = input("Chọn 1 (cá nhân) hoặc 2 (theo cặp): ")', self.code_source)
        self.assertIn("comparison_export_sha256", self.code_source)
        self.assertIn("Nguồn đối chiếu trùng gói xuất của bạn", self.code_source)

    def test_metrics_are_formative_not_pass_thresholds(self):
        documents = "\n".join(
            (ROOT / name).read_text(encoding="utf-8")
            for name in ("README.md", "GUIDE.md", "RUBRIC.md", "docs/day2-e2e-guide.html")
        ).casefold()
        for phrase in ("không phải ngưỡng đạt", "không phải điểm", "không chứng minh cả hai đều đúng"):
            self.assertIn(phrase, documents + self.code_source.casefold())
        self.assertNotIn("iou ≥ 0.7", documents)

    def test_submission_contract_includes_evidence_and_excludes_raw_data(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        expected = {
            "IMAGE_ATTRIBUTION.md",
            "input_pool_audit.json",
            "my_export_audit.json",
            "my_native_export_audit.json",
            "training_run.json",
            "detect_result.jpg",
            "comparison_iou.csv",
            "comparison_summary.json",
            "comparison_overlay.png",
        }
        for filename in expected:
            self.assertIn(filename, readme)
            self.assertIn(filename, self.code_source)
        self.assertIn('roots == {"REPORT.md", "GUIDELINE_MINI_SHEET.md", "day2_lab_outputs"}', self.code_source)
        self.assertIn("Không đưa gói xuất thô", self.code_source)
        self.assertIn("bộ nhãn đối chiếu", self.code_source)
        self.assertIn("trọng số mô hình", self.code_source)

    def test_each_student_submits_a_personal_github_repository_url(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = (ROOT / "GUIDE.md").read_text(encoding="utf-8")
        learner_contract = "\n".join((readme, guide, self.markdown_source, self.code_source))
        self.assertIn("KX-DAY02-HoVaTen-MSSV", readme)
        self.assertIn("kho GitHub cá nhân", learner_contract)
        self.assertIn("nộp đường dẫn kho trên VLearn", learner_contract)
        self.assertIn('repository_name = f"KX-DAY02-{student_name}-{student_id}"', self.code_source)
        self.assertIn('transfer_archive = Path(f"{repository_name}-repo-files.zip")', self.code_source)
        self.assertIn("ZIP này chỉ giúp tải tệp từ Colab về máy, không phải bài nộp trên VLearn", self.code_source)
        self.assertNotIn("ZIP bài nộp", learner_contract)
        self.assertNotIn("ZIP nộp bài", learner_contract)

    def test_html_uses_four_real_cvat_screenshots(self):
        guide = (ROOT / "docs" / "day2-e2e-guide.html").read_text(encoding="utf-8")
        assets = (
            "cvat-project-schema-real.png",
            "cvat-task-upload-real.png",
            "cvat-rectangle-save-real.png",
            "cvat-export-controls-real.png",
        )
        self.assertEqual(len(re.findall(r"<img\s", guide)), 4)
        for filename in assets:
            self.assertIn(filename, guide)
            self.assertTrue((ROOT / "docs" / "assets" / "day2-e2e" / filename).is_file())
        for removed in ("cvat-annotation-attributes-real.png", "cvat-export-menu-real.png"):
            self.assertFalse((ROOT / "docs" / "assets" / "day2-e2e" / removed).exists())
        for stale in ("synthetic", "COCO", "pedestrian", "cyclist", "operation-map", "confidence-poc", "tight-box-poc"):
            self.assertNotIn(stale.casefold(), guide.casefold())
        self.assertIn("Ảnh chụp trực tiếp từ tác vụ Day 2", guide)
        self.assertNotIn("cvat-annotation-attributes-real.png", guide)
        self.assertNotIn("cvat-export-menu-real.png", guide)

    def test_native_audit_persists_cross_format_consistency(self):
        self.assertIn('my_native_audit["cross_format_consistency"] = same_state_audit', self.code_source)

    def test_cross_format_check_rejects_same_total_with_different_class_or_geometry(self):
        image_ids = ["drive_008"]
        yolo = [
            {
                "image_id": "drive_008",
                "class_name": "car",
                "bbox_xyxy_normalized": [0.1, 0.1, 0.2, 0.2],
            }
        ]
        same = [
            {
                "image_id": "drive_008",
                "class_name": "car",
                "bbox_xyxy_normalized": [0.1, 0.1, 0.2, 0.2],
            }
        ]
        self.assertTrue(LAB.verify_same_annotation_state(yolo, same, image_ids)["same_annotation_state"])

        wrong_class = [{**same[0], "class_name": "truck"}]
        with self.assertRaisesRegex(AssertionError, "khác số hộp lớp"):
            LAB.verify_same_annotation_state(yolo, wrong_class, image_ids)

        wrong_geometry = [{**same[0], "bbox_xyxy_normalized": [0.3, 0.3, 0.4, 0.4]}]
        with self.assertRaisesRegex(AssertionError, "khác hình học hộp"):
            LAB.verify_same_annotation_state(yolo, wrong_geometry, image_ids)

    def test_markdown_links_and_html_assets_resolve_locally(self):
        markdown_files = [ROOT / "README.md", ROOT / "GUIDE.md", ROOT / "data" / "README.md"]
        for source_path in markdown_files:
            content = source_path.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if target.startswith(("https://", "http://", "#")):
                    continue
                self.assertTrue((source_path.parent / target).resolve().exists(), f"{source_path}: {target}")

        html = (ROOT / "docs" / "day2-e2e-guide.html").read_text(encoding="utf-8")
        for target in re.findall(r'<img[^>]+src="([^"]+)"', html):
            self.assertTrue((ROOT / "docs" / target).is_file(), target)

    def test_safe_extract_rejects_path_traversal_without_deleting_prior_output(self):
        with tempfile.TemporaryDirectory(prefix="day2-unsafe-zip-") as temporary:
            root = Path(temporary)
            archive_path = root / "unsafe.zip"
            destination = root / "out"
            destination.mkdir()
            sentinel = destination / "previous-valid-export.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../escape.txt", "bad")
            with self.assertRaisesRegex(ValueError, "không an toàn"):
                LAB.safe_extract_zip(archive_path, destination)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_yolo_audit_and_cross_iou_on_controlled_exports(self):
        rows = LAB.read_manifest(ROOT / "data" / "image-manifest.csv")
        with tempfile.TemporaryDirectory(prefix="day2-export-test-") as temporary:
            root = Path(temporary)
            mine_zip = self._make_export(root / "mine", rows, x_offset=0.0, class_mismatch=False)
            peer_zip = self._make_export(root / "peer", rows, x_offset=0.01, class_mismatch=True)
            mine_report, mine_records = LAB.audit_yolo_export(mine_zip, root / "mine-out", rows)
            peer_report, peer_records = LAB.audit_yolo_export(peer_zip, root / "peer-out", rows)
            self.assertEqual(mine_report["object_count"], 40)
            self.assertTrue(mine_report["within_slide_workload_target"])
            self.assertEqual(peer_report["image_count"], 4)
            comparison_ids = [row["image_id"] for row in rows]
            summary, matches = LAB.compare_annotation_records(
                mine_records, peer_records, comparison_ids, comparison_source="peer"
            )
            self.assertEqual(summary["matched_boxes"], 40)
            self.assertEqual(summary["unmatched_mine"], 0)
            self.assertEqual(summary["unmatched_comparison"], 0)
            self.assertLess(summary["class_agreement"], 1.0)
            self.assertFalse(summary["floor_is_official_pass_threshold"])
            self.assertIn("không chứng minh", summary["interpretation_warning"])
            self.assertEqual(len(matches), 40)
            with self.assertRaisesRegex(ValueError, "comparison_source"):
                LAB.compare_annotation_records(mine_records, peer_records, comparison_ids, comparison_source="self")
            extra_zip = self._make_export(root / "extra", rows, x_offset=0.0, class_mismatch=False, extra=True)
            with self.assertRaisesRegex(ValueError, "file ngoài pool"):
                LAB.audit_yolo_export(extra_zip, root / "extra-out", rows)

    def test_native_export_audit_requires_every_attribute(self):
        rows = LAB.read_manifest(ROOT / "data" / "image-manifest.csv")
        with tempfile.TemporaryDirectory(prefix="day2-native-test-") as temporary:
            root = Path(temporary)
            archive = self._make_native_export(root, rows)
            report = LAB.audit_cvat_images_export(archive, root / "out", rows)
            self.assertEqual(report["image_count"], 4)
            self.assertEqual(report["object_count"], 4)
            self.assertEqual(
                report["attribute_value_count_by_name"],
                {name: 4 for name in LAB.REQUIRED_ATTRIBUTE_VALUES},
            )
            invalid = self._make_native_export(root, rows, omit_attribute=True)
            with self.assertRaisesRegex(ValueError, "cần đúng attributes"):
                LAB.audit_cvat_images_export(invalid, root / "invalid-out", rows)

    @staticmethod
    def _make_export(
        root: Path,
        rows: list[dict],
        x_offset: float,
        class_mismatch: bool,
        extra: bool = False,
    ) -> Path:
        dataset = root / "dataset"
        (dataset / "images" / "train").mkdir(parents=True)
        (dataset / "labels" / "train").mkdir(parents=True)
        (dataset / "data.yaml").write_text(
            "path: .\ntrain: images/train\nnames:\n  0: car\n  1: truck\n  2: bus\n  3: van\n",
            encoding="utf-8",
        )
        for row_index, row in enumerate(rows):
            image_id = row["image_id"]
            Image.new("RGB", (row["width"], row["height"]), "white").save(
                dataset / "images" / "train" / f"{image_id}.jpg"
            )
            labels = []
            for index in range(10):
                class_id = index % 4
                if class_mismatch and row_index >= 2 and index == 0:
                    class_id = (class_id + 1) % 4
                x_center = 0.08 + (index % 5) * 0.18 + x_offset
                y_center = 0.2 + (index // 5) * 0.4
                labels.append(f"{class_id} {x_center:.4f} {y_center:.4f} 0.1000 0.1200")
            (dataset / "labels" / "train" / f"{image_id}.txt").write_text(
                "\n".join(labels) + "\n", encoding="utf-8"
            )
        if extra:
            Image.new("RGB", (640, 640), "white").save(dataset / "images" / "train" / "outside-pool.jpg")
            (dataset / "labels" / "train" / "outside-pool.txt").write_text(
                "0 0.5000 0.5000 0.1000 0.1000\n", encoding="utf-8"
            )
        archive_path = root / "export.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in dataset.rglob("*"):
                if path.is_file():
                    archive.write(path, arcname=path.relative_to(dataset).as_posix())
        return archive_path

    @staticmethod
    def _make_native_export(root: Path, rows: list[dict], omit_attribute: bool = False) -> Path:
        suffix = "invalid" if omit_attribute else "valid"
        image_elements = []
        for index, row in enumerate(rows):
            attributes = [
                '<attribute name="visibility">clear</attribute>',
                '<attribute name="boundary">inside</attribute>',
                '<attribute name="review_state">confident</attribute>',
            ]
            if omit_attribute and index == 0:
                attributes.pop()
            image_elements.append(
                f'<image id="{index}" name="{row["image_id"]}.jpg" width="640" height="640">'
                f'<box label="car" xtl="10" ytl="10" xbr="20" ybr="20">'
                f'{"".join(attributes)}</box></image>'
            )
        xml_path = root / f"{suffix}-annotations.xml"
        xml_path.write_text(
            '<?xml version="1.0" encoding="utf-8"?><annotations>'
            + "".join(image_elements)
            + "</annotations>",
            encoding="utf-8",
        )
        archive_path = root / f"{suffix}-native.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(xml_path, arcname="annotations.xml")
        return archive_path


if __name__ == "__main__":
    unittest.main()

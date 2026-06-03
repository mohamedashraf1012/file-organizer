import os
import sys
import pytest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.organizer import get_category, scan_folder, organize_files, get_folder_stats  # noqa: E402


# ── get_category ──────────────────────────────────────────────────────────────

class TestGetCategory:
    def test_image_extensions(self):
        for ext in [".jpg", ".jpeg", ".png", ".gif"]:
            assert get_category(ext) == "Images"

    def test_video_extensions(self):
        for ext in [".mp4", ".avi", ".mov", ".mkv"]:
            assert get_category(ext) == "Videos"

    def test_audio_extensions(self):
        for ext in [".mp3", ".wav", ".flac"]:
            assert get_category(ext) == "Audio"

    def test_document_extensions(self):
        for ext in [".pdf", ".docx", ".txt", ".xlsx", ".csv"]:
            assert get_category(ext) == "Documents"

    def test_code_extensions(self):
        for ext in [".py", ".js", ".html", ".json", ".yaml"]:
            assert get_category(ext) == "Code"

    def test_archive_extensions(self):
        for ext in [".zip", ".rar", ".tar", ".gz"]:
            assert get_category(ext) == "Archives"

    def test_unknown_extension_returns_others(self):
        assert get_category(".xyz") == "Others"
        assert get_category(".unknown") == "Others"

    def test_no_extension_returns_others(self):
        assert get_category("") == "Others"

    def test_uppercase_extension(self):
        assert get_category(".JPG") == "Images"
        assert get_category(".PDF") == "Documents"
        assert get_category(".MP4") == "Videos"

    def test_mixed_case_extension(self):
        assert get_category(".Png") == "Images"
        assert get_category(".PyC") == "Others"


# ── scan_folder ───────────────────────────────────────────────────────────────

class TestScanFolder:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def _create_file(self, name, content="test"):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_scan_returns_list(self):
        self._create_file("test.txt")
        result = scan_folder(self.temp_dir)
        assert isinstance(result, list)

    def test_scan_finds_correct_number_of_files(self):
        self._create_file("a.txt")
        self._create_file("b.py")
        self._create_file("c.jpg")
        result = scan_folder(self.temp_dir)
        assert len(result) == 3

    def test_scan_file_info_structure(self):
        self._create_file("sample.py")
        result = scan_folder(self.temp_dir)
        assert len(result) == 1
        info = result[0]
        assert "name" in info
        assert "extension" in info
        assert "category" in info
        assert "full_path" in info
        assert "size_bytes" in info

    def test_scan_correct_extension(self):
        self._create_file("script.py")
        result = scan_folder(self.temp_dir)
        assert result[0]["extension"] == ".py"

    def test_scan_correct_category(self):
        self._create_file("photo.jpg")
        result = scan_folder(self.temp_dir)
        assert result[0]["category"] == "Images"

    def test_scan_empty_folder(self):
        result = scan_folder(self.temp_dir)
        assert result == []

    def test_scan_ignores_subdirectories(self):
        self._create_file("file.txt")
        os.makedirs(os.path.join(self.temp_dir, "subfolder"))
        result = scan_folder(self.temp_dir)
        assert len(result) == 1

    def test_scan_nonexistent_folder_raises(self):
        with pytest.raises(FileNotFoundError):
            scan_folder("/nonexistent/path/12345")

    def test_scan_file_path_raises_not_a_directory(self):
        file_path = self._create_file("notafolder.txt")
        with pytest.raises(NotADirectoryError):
            scan_folder(file_path)

    def test_scan_file_size(self):
        path = os.path.join(self.temp_dir, "sized.txt")
        content = "hello world"
        with open(path, "w") as f:
            f.write(content)
        result = scan_folder(self.temp_dir)
        assert result[0]["size_bytes"] > 0


# ── organize_files ────────────────────────────────────────────────────────────

class TestOrganizeFiles:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def _create_file(self, name, content="test"):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_organize_returns_summary_dict(self):
        self._create_file("doc.pdf")
        summary = organize_files(self.temp_dir)
        assert isinstance(summary, dict)

    def test_summary_has_required_keys(self):
        summary = organize_files(self.temp_dir)
        for key in ["total", "moved", "skipped", "errors", "details", "timestamp"]:
            assert key in summary

    def test_files_moved_to_correct_category(self):
        self._create_file("image.jpg")
        organize_files(self.temp_dir)
        assert os.path.exists(os.path.join(self.temp_dir, "Images", "image.jpg"))

    def test_multiple_categories(self):
        self._create_file("photo.jpg")
        self._create_file("script.py")
        self._create_file("doc.pdf")
        organize_files(self.temp_dir)
        assert os.path.exists(os.path.join(self.temp_dir, "Images", "photo.jpg"))
        assert os.path.exists(os.path.join(self.temp_dir, "Code", "script.py"))
        assert os.path.exists(os.path.join(self.temp_dir, "Documents", "doc.pdf"))

    def test_dry_run_does_not_move_files(self):
        self._create_file("file.mp3")
        organize_files(self.temp_dir, dry_run=True)
        assert not os.path.exists(os.path.join(self.temp_dir, "Audio", "file.mp3"))
        assert os.path.exists(os.path.join(self.temp_dir, "file.mp3"))

    def test_dry_run_summary_still_counts(self):
        self._create_file("a.jpg")
        self._create_file("b.zip")
        summary = organize_files(self.temp_dir, dry_run=True)
        assert summary["moved"] == 2

    def test_moved_count_matches_files(self):
        self._create_file("a.jpg")
        self._create_file("b.py")
        summary = organize_files(self.temp_dir)
        assert summary["moved"] == 2
        assert summary["errors"] == 0

    def test_empty_folder_summary(self):
        summary = organize_files(self.temp_dir)
        assert summary["total"] == 0
        assert summary["moved"] == 0


# ── get_folder_stats ──────────────────────────────────────────────────────────

class TestGetFolderStats:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def _create_file(self, name):
        path = os.path.join(self.temp_dir, name)
        with open(path, "w") as f:
            f.write("x")

    def test_returns_dict(self):
        result = get_folder_stats(self.temp_dir)
        assert isinstance(result, dict)

    def test_correct_category_counts(self):
        self._create_file("a.jpg")
        self._create_file("b.jpg")
        self._create_file("c.py")
        stats = get_folder_stats(self.temp_dir)
        assert stats.get("Images") == 2
        assert stats.get("Code") == 1

    def test_empty_folder_returns_empty_dict(self):
        stats = get_folder_stats(self.temp_dir)
        assert stats == {}

    def test_unknown_extension_goes_to_others(self):
        self._create_file("mystery.abc123")
        stats = get_folder_stats(self.temp_dir)
        assert stats.get("Others") == 1

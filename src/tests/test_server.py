import unittest
from unittest.mock import patch
from src.core.server import (
    get_updated_tracked_lists,
    compare_files,
    compare_timestamps,
    is_needed_to_reload,
    EXCLUDE_DIRS,
    EXCLUDE_FILES,
    FILETYPES_TO_MONITOR,
)


class TestServerFunctions(unittest.TestCase):
    def setUp(self):
        # Mocking the project root path and public directory
        self.root_path = "/mock/"

    @patch("src.core.server.find_file_timestamps")
    @patch("src.core.server.find_files_rec")
    def test_get_updated_tracked_lists(
        self, mock_find_files_rec, mock_find_file_timestamps
    ):
        mock_find_files_rec.return_value = [
            "/mock/content/file1.md",
            "/mock/content/subdir/file2.md",
        ]
        mock_find_file_timestamps.return_value = {
            "/mock/content/file1.md": 12345.0,
            "/mock/content/subdir/file2.md": 67890.0,
        }

        files, filestamps = get_updated_tracked_lists(self.root_path)

        self.assertEqual(
            files, ["/mock/content/file1.md", "/mock/content/subdir/file2.md"]
        )
        self.assertEqual(
            filestamps,
            {
                "/mock/content/file1.md": 12345.0,
                "/mock/content/subdir/file2.md": 67890.0,
            },
        )
        mock_find_files_rec.assert_called_once_with(
            path=self.root_path,
            exclude_dirs=EXCLUDE_DIRS,
            exclude_files=EXCLUDE_FILES,
            filetypes_to_monitor=FILETYPES_TO_MONITOR,
        )
        mock_find_file_timestamps.assert_called_once_with(
            ["/mock/content/file1.md", "/mock/content/subdir/file2.md"]
        )

    def test_compare_files_no_changes(self):
        tracked_files = ["/mock/file1.html", "/mock/file2.html"]
        u_tracked_files = ["/mock/file1.html", "/mock/file2.html"]

        added_files, deleted_files = compare_files(
            tracked_files=tracked_files, u_tracked_files=u_tracked_files
        )

        self.assertSetEqual(added_files, set())
        self.assertSetEqual(deleted_files, set())

    def test_compare_files_changes(self):
        tracked_files = ["/mock/file1.html", "/mock/file2.html"]
        u_tracked_files = ["/mock/file2.html", "/mock/file3.css"]

        added_files, deleted_files = compare_files(
            tracked_files=tracked_files, u_tracked_files=u_tracked_files
        )

        self.assertSetEqual(added_files, {"/mock/file3.css"})
        self.assertSetEqual(deleted_files, {"/mock/file1.html"})

    def test_compare_timestamps_no_changes(self):
        tracked_filestamps = {"/mock/file1.md": 12345.0, "/mock/file2.html": 67890.0}
        u_tracked_filestamps = {"/mock/file1.md": 12345.0, "/mock/file2.html": 67890.0}

        modified_files = compare_timestamps(
            tracked_filestamps=tracked_filestamps,
            u_tracked_filestamps=u_tracked_filestamps,
        )

        self.assertSetEqual(modified_files, set())

    def test_compare_timestamps_changes(self):
        tracked_filestamps = {"/mock/file1.md": 12345.0, "/mock/file2.html": 67890.0}
        u_tracked_filestamps = {"/mock/file1.md": 69420.0, "/mock/file2.html": 67890.0}

        modified_files = compare_timestamps(
            tracked_filestamps=tracked_filestamps,
            u_tracked_filestamps=u_tracked_filestamps,
        )

        self.assertSetEqual(modified_files, {"/mock/file1.md"})

    @patch("src.core.server.get_updated_tracked_lists")
    def test_is_needed_to_reload_no_changes(self, mock_get_updated_tracked_lists):
        tracked_files = ["/mock/file1.md", "/mock/file2.html"]
        tracked_filestamps = {"/mock/file1.md": 12345.0, "/mock/file2.html": 67890.0}
        mock_get_updated_tracked_lists.return_value = (
            ["/mock/file1.md", "/mock/file2.html"],
            {"/mock/file1.md": 12345.0, "/mock/file2.html": 67890.0},
        )

        self.assertFalse(
            is_needed_to_reload(
                root_path=self.root_path,
                tracked_files=tracked_files,
                tracked_filestamps=tracked_filestamps,
            )
        )
        mock_get_updated_tracked_lists.assert_called_once_with(self.root_path)

    @patch("src.core.server.get_updated_tracked_lists")
    def test_is_needed_to_reload_changes(self, mock_get_updated_tracked_lists):
        tracked_files = ["/mock/file1.md", "/mock/file2.html"]
        tracked_filestamps = {"/mock/file1.md": 12345.0, "/mock/file2.html": 67890.0}
        mock_get_updated_tracked_lists.return_value = (
            ["/mock/file1.md", "/mock/file2.html"],
            {"/mock/file1.md": 69420.0, "/mock/file2.html": 67890.0},
        )

        self.assertTrue(
            is_needed_to_reload(
                root_path=self.root_path,
                tracked_files=tracked_files,
                tracked_filestamps=tracked_filestamps,
            )
        )
        mock_get_updated_tracked_lists.assert_called_once_with(self.root_path)


if __name__ == "__main__":
    unittest.main()

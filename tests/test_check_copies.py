import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import check_copies  # noqa: E402

FILES = ["src/dock_layout.py", "src/herdr_api.py"]


class CheckCopiesTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.origin = self.root / "herdr-dock-grid"
        self.write(self.origin, "src/dock_layout.py", "print('origin')\n")
        self.write(self.origin, "src/herdr_api.py", "print('api')\n")

    def write(self, base, name, text):
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def run_main(self):
        """표 출력은 테스트 결과를 가리므로 버리고 종료 코드만 돌려준다."""
        with contextlib.redirect_stdout(io.StringIO()):
            return check_copies.main(["--origin", str(self.origin), "--root", str(self.root)])

    def make_copy(self, repo, dock_text=None, api_text=None):
        """복사본 저장소를 만든다. None 이면 그 파일을 만들지 않는다 (없음 상태)."""
        base = self.root / repo
        if dock_text is not None:
            self.write(base, "src/dock_layout.py", dock_text)
        if api_text is not None:
            self.write(base, "src/herdr_api.py", api_text)

    def test_all_same_gives_zero(self):
        for repo in check_copies.COPY_REPOS:
            self.make_copy(repo, "print('origin')\n", "print('api')\n")
        rows = check_copies.compare(self.origin, self.root)
        self.assertTrue(all(status == check_copies.SAME for _, _, status in rows))
        self.assertEqual(self.run_main(), 0)

    def test_one_different_byte_gives_one(self):
        for repo in check_copies.COPY_REPOS:
            self.make_copy(repo, "print('origin')\n", "print('api')\n")
        self.make_copy("herdr-talk", "print('origin') \n", "print('api')\n")  # 공백 한 칸 차이
        rows = check_copies.compare(self.origin, self.root)
        differing = [(repo, name) for repo, name, status in rows if status == check_copies.DIFFERENT]
        self.assertEqual(differing, [("herdr-talk", "src/dock_layout.py")])
        self.assertEqual(self.run_main(), 1)

    def test_missing_file_is_reported_and_gives_one(self):
        for repo in check_copies.COPY_REPOS:
            self.make_copy(repo, "print('origin')\n", "print('api')\n")
        (self.root / "herdr-radio" / "src" / "herdr_api.py").unlink()
        rows = check_copies.compare(self.origin, self.root)
        self.assertIn(("herdr-radio", "src/herdr_api.py", check_copies.MISSING), rows)
        self.assertEqual(self.run_main(), 1)

    def test_missing_repository_is_reported(self):
        for repo in check_copies.COPY_REPOS[1:]:  # 첫 저장소는 폴더 자체가 없다
            self.make_copy(repo, "print('origin')\n", "print('api')\n")
        rows = check_copies.compare(self.origin, self.root)
        self.assertIn(("herdr-simple-git", "src/dock_layout.py", check_copies.MISSING), rows)

    def test_table_lists_every_repository_and_file(self):
        rows = [("herdr-talk", "src/herdr_api.py", check_copies.SAME)]
        text = check_copies.format_table(rows)
        self.assertIn("herdr-talk", text)
        self.assertIn("src/herdr_api.py", text)
        self.assertIn(check_copies.SAME, text)

    def test_only_the_two_shared_files_are_checked(self):
        rows = check_copies.compare(self.origin, self.root, repos=["x"])
        self.assertEqual([name for _, name, _ in rows], FILES)


if __name__ == "__main__":
    unittest.main()

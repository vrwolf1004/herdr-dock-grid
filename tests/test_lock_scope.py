import os
import sys
import tempfile
import threading
import time
import unittest
from contextlib import contextmanager
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import dock_layout  # noqa: E402

REAL_REGISTRY_LOCK = dock_layout.registry_lock
HERDR_DELAY = 0.2  # 가짜 herdr 한 번 호출에 걸리는 시간


def fake_herdr(calls=None):
    """herdr CLI 대신 쓴다. 워크스페이스 w1 에 빈 pane 두 개 (p1, p2) 가 있다고 응답하고, 호출마다 HERDR_DELAY 만큼 기다린다."""
    layout = {
        "workspace_id": "w1",
        "tab_id": "t1",
        "focused_pane_id": "p1",
        "area": {"x": 0, "y": 0, "width": 100, "height": 50},
        "panes": [
            {"pane_id": "p1", "rect": {"x": 0, "y": 0, "width": 50, "height": 50}},
            {"pane_id": "p2", "rect": {"x": 50, "y": 0, "width": 50, "height": 50}},
        ],
        "splits": [],
    }
    answers = {
        ("workspace", "list"): {"workspaces": [{"workspace_id": "w1", "label": "herdr-dock"}]},
        ("pane", "list"): {"panes": [{"pane_id": "p1", "workspace_id": "w1"},
                                     {"pane_id": "p2", "workspace_id": "w1"}]},
        ("agent", "list"): {"agents": []},
        ("pane", "layout"): {"layout": layout},
    }

    def cli(*args, check=True):
        if calls is not None:
            calls.append(args)
        time.sleep(HERDR_DELAY)
        return answers.get(args[:2], {})

    return cli


class LockScopeTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        patch = mock.patch.object(dock_layout, "plugins_folder", return_value=self.folder.name)
        patch.start()
        self.addCleanup(patch.stop)
        self.held = []

    @contextmanager
    def timed_lock(self, folder):
        with REAL_REGISTRY_LOCK(folder):
            started = time.monotonic()
            try:
                yield
            finally:
                self.held.append(time.monotonic() - started)

    def measure(self, call):
        with mock.patch.object(dock_layout, "registry_lock", side_effect=self.timed_lock), \
                mock.patch.object(dock_layout.herdr_api, "cli", side_effect=fake_herdr()):
            result = call()
        return result, sum(self.held)

    def test_list_docks_keeps_herdr_calls_out_of_the_lock(self):
        _, held = self.measure(dock_layout.list_docks)
        self.assertLess(held, HERDR_DELAY / 2, f"잠금을 쥔 시간 {held:.2f}s (herdr 호출은 {HERDR_DELAY}s 씩)")

    def test_save_layout_snapshot_keeps_herdr_calls_out_of_the_lock(self):
        dock_layout.write_dock_marker(self.folder.name, "alpha", "p1")
        _, held = self.measure(dock_layout.save_layout_snapshot)
        self.assertLess(held, HERDR_DELAY / 2, f"잠금을 쥔 시간 {held:.2f}s")

    def test_get_layout_snapshot_keeps_herdr_calls_out_of_the_lock(self):
        with mock.patch.object(dock_layout.herdr_api, "cli", side_effect=fake_herdr()):
            dock_layout.save_layout_snapshot()
        _, held = self.measure(dock_layout.get_layout_snapshot)
        self.assertLess(held, HERDR_DELAY / 2, f"잠금을 쥔 시간 {held:.2f}s")

    def test_two_docks_allocated_at_the_same_time_get_different_panes(self):
        results = {}
        errors = []
        start = threading.Barrier(2)

        def allocate(key):
            try:
                start.wait()
                results[key] = dock_layout.ensure_dock_pane(key, self.folder.name)
            except Exception as error:  # noqa: BLE001 - 스레드 밖으로 보이게 한다
                errors.append(error)

        # 패치는 스레드 밖에서 한 번만 한다. 스레드마다 패치하면 한쪽이 끝나며 되돌릴 때 실제 herdr 가 불릴 수 있다.
        with mock.patch.object(dock_layout.herdr_api, "cli", side_effect=fake_herdr()):
            threads = [threading.Thread(target=allocate, args=(key,)) for key in ("alpha", "beta")]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=30)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        panes = [pane_id for _, pane_id in results.values()]
        self.assertEqual(sorted(panes), ["p1", "p2"])


if __name__ == "__main__":
    unittest.main()

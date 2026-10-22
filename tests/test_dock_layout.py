import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dock_layout


class DockLayoutTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = self.directory.name
        self.state_dir = os.path.join(self.folder, "plugin-state")
        self.environment = patch.dict(os.environ, {"HERDR_PLUGIN_STATE_DIR": self.state_dir})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_register_dock_persists_definition(self):
        definition = dock_layout.register_dock(
            "example",
            title="Example",
            default_position="top-left",
            min_size={"width": 200},
            entrypoint="example:start",
        )

        self.assertEqual(definition["title"], "Example")
        registry = dock_layout.load_registry(dock_layout.plugins_folder())
        self.assertEqual(registry["registrations"]["example"], definition)

    def test_layout_policy_is_persisted(self):
        self.assertEqual(dock_layout.get_layout_policy(), "grid-2x2")

        self.assertEqual(dock_layout.set_layout_policy("grid-2x2"), "grid-2x2")
        self.assertEqual(dock_layout.get_layout_policy(), "grid-2x2")

    def test_invalid_layout_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            dock_layout.set_layout_policy("unknown")

    def test_layout_snapshot_is_saved_and_returned(self):
        layout = {
            "workspace_id": "workspace",
            "tab_id": "workspace:tab",
            "area": {"x": 0, "y": 0, "width": 100, "height": 40},
            "panes": [{"pane_id": "pane", "rect": {"x": 0, "y": 0, "width": 100, "height": 40}}],
            "splits": [],
        }
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ), patch.object(dock_layout.herdr_api, "cli", return_value={"layout": layout}) as cli:
            snapshot = dock_layout.save_layout_snapshot()

        cli.assert_called_once_with("pane", "layout", "--pane", "pane")
        self.assertEqual(snapshot["panes"][0]["pane_id"], "pane")
        self.assertEqual(dock_layout.get_layout_snapshot("workspace"), snapshot)

    def test_ensure_reuses_a_live_registered_pane(self):
        folder = dock_layout.plugins_folder()
        os.makedirs(folder, exist_ok=True)
        dock_layout.write_registry(
            folder,
            {
                "version": dock_layout.REGISTRY_VERSION,
                "docks": {"example": {"workspace_id": "workspace", "pane_id": "pane", "updated_at": 1}},
                "registrations": {},
            },
        )
        dock_layout.write_dock_marker(folder, "example", "pane")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(
            dock_layout, "dock_workspaces", return_value=[{"workspace_id": "workspace", "label": "herdr-dock"}]
        ), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ), patch.object(dock_layout.herdr_api, "cli") as cli:
            self.assertEqual(dock_layout.ensure_dock_pane("example", "cwd"), ("workspace", "pane"))

        cli.assert_not_called()
        self.assertEqual(dock_layout.read_dock_pane(folder, "example"), "pane")

    def test_reconcile_removes_missing_and_duplicate_panes(self):
        folder = dock_layout.plugins_folder()
        os.makedirs(folder, exist_ok=True)
        dock_layout.write_registry(
            folder,
            {
                "version": dock_layout.REGISTRY_VERSION,
                "docks": {
                    "a": {"workspace_id": "workspace", "pane_id": "pane", "updated_at": 1},
                    "b": {"workspace_id": "workspace", "pane_id": "pane", "updated_at": 2},
                    "c": {"workspace_id": "workspace", "pane_id": "missing", "updated_at": 3},
                },
                "registrations": {},
            },
        )
        dock_layout.write_dock_marker(folder, "a", "pane")
        dock_layout.write_dock_marker(folder, "b", "pane")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            docks = dock_layout.reconcile_dock_state()

        self.assertEqual(set(docks), {"a"})

    def test_reconcile_removes_allocation_without_marker(self):
        folder = dock_layout.plugins_folder()
        os.makedirs(folder, exist_ok=True)
        dock_layout.write_registry(
            folder,
            {
                "version": dock_layout.REGISTRY_VERSION,
                "docks": {"example": {"workspace_id": "workspace", "pane_id": "pane", "updated_at": 1}},
                "registrations": {},
            },
        )
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            docks = dock_layout.reconcile_dock_state()

        self.assertEqual(docks, {})

    def test_reconcile_imports_live_legacy_markers(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "legacy", "pane")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            docks = dock_layout.reconcile_dock_state()

        self.assertEqual(docks["legacy"]["pane_id"], "pane")

    def test_reconcile_removes_stale_markers_of_dead_panes_only(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "dead", "missing")
        dock_layout.write_dock_marker(folder, "fresh", "missing-new")
        dock_layout.write_dock_marker(folder, "alive", "pane")
        old = os.path.getmtime(dock_layout.dock_marker(folder, "dead")) - 60
        os.utime(dock_layout.dock_marker(folder, "dead"), (old, old))
        os.utime(dock_layout.dock_marker(folder, "alive"), (old, old))
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            dock_layout.reconcile_dock_state()

        self.assertEqual(sorted(dock_layout.dock_marker_keys(folder)), ["alive", "fresh"])

    def test_claimed_panes_include_unknown_plugin_markers(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "new-plugin", "pane")

        self.assertEqual(dock_layout.claimed_dock_panes(folder, "example"), {"pane"})

    def test_release_removes_allocation_and_legacy_marker(self):
        folder = dock_layout.plugins_folder()
        os.makedirs(folder, exist_ok=True)
        dock_layout.write_registry(
            folder,
            {
                "version": dock_layout.REGISTRY_VERSION,
                "docks": {"example": {"workspace_id": "workspace", "pane_id": "pane", "updated_at": 1}},
                "registrations": {},
            },
        )
        dock_layout.write_dock_marker(folder, "example", "pane")

        released = dock_layout.release_dock_pane("example")

        self.assertEqual(released["pane_id"], "pane")
        self.assertFalse(os.path.exists(dock_layout.dock_marker(folder, "example")))
        with open(dock_layout.registry_path(folder), encoding="utf-8") as file:
            self.assertEqual(json.load(file)["docks"], {})


class LegacyApiTests(unittest.TestCase):
    # 설치본을 우선 로드하는 다른 플러그인이 호출하는 이름. 지우면 해당 플러그인이 시작 시 실패한다.
    LEGACY_NAMES = (
        "plugins_folder", "wait_for_earlier", "write_dock_marker", "remove_dock_marker",
        "read_dock_pane", "claimed_dock_panes", "grid_split", "dock_workspace_id",
        "workspace_panes", "is_sidebar", "ensure_dock_pane", "pick_pane", "dock_starting",
    )

    def test_legacy_names_exist(self):
        missing = [name for name in self.LEGACY_NAMES if not hasattr(dock_layout, name)]
        self.assertEqual(missing, [])

    def test_wait_for_earlier_returns_when_nothing_is_starting(self):
        with tempfile.TemporaryDirectory() as folder:
            dock_layout.write_dock_marker(folder, "a-plugin", "pane")
            dock_layout.wait_for_earlier(folder, "b-plugin")


class DockOperationTests(unittest.TestCase):
    setUp = DockLayoutTests.setUp

    def test_list_docks_reports_liveness(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "alive", "pane")
        dock_layout.write_dock_marker(folder, "gone", "missing")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            docks = {dock["key"]: dock for dock in dock_layout.list_docks()}

        self.assertTrue(docks["alive"]["live"])
        self.assertFalse(docks["gone"]["live"])

    def test_reset_removes_only_dead_markers(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "alive", "pane")
        dock_layout.write_dock_marker(folder, "gone", "missing")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_ids", return_value=["workspace"]), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            removed = dock_layout.reset_dock_state()

        self.assertEqual(removed, ["gone"])
        self.assertEqual(dock_layout.read_dock_pane(folder, "alive"), "pane")


class MultiDockTests(unittest.TestCase):
    setUp = DockLayoutTests.setUp

    @staticmethod
    def _full_workspace(workspace_id, count):
        return [
            {"workspace_id": workspace_id, "pane_id": f"{workspace_id}:p{i}", "label": f"busy{i}", "tokens": {}}
            for i in range(count)
        ]

    def test_workspaces_are_ordered_and_filtered(self):
        listing = {"workspaces": [
            {"workspace_id": "c", "label": "herdr-dock3"},
            {"workspace_id": "x", "label": "other"},
            {"workspace_id": "b", "label": "herdr-dock2"},
            {"workspace_id": "a", "label": "herdr-dock"},
            {"workspace_id": "y", "label": "herdr-dock-grid"},
        ]}
        with patch.object(dock_layout.herdr_api, "cli", return_value=listing):
            self.assertEqual(dock_layout.dock_workspace_ids(), ["a", "b", "c"])

    def test_ensure_creates_next_workspace_when_all_slots_are_used(self):
        folder = dock_layout.plugins_folder()
        os.makedirs(folder, exist_ok=True)
        docks = {}
        for index in range(4):
            key = f"plugin{index}"
            docks[key] = {"workspace_id": "w1", "pane_id": f"w1:p{index}", "updated_at": 1}
            dock_layout.write_dock_marker(folder, key, f"w1:p{index}")
        dock_layout.write_registry(
            folder, {"version": dock_layout.REGISTRY_VERSION, "docks": docks, "registrations": {}}
        )
        existing = self._full_workspace("w1", 4)
        fresh = [{"workspace_id": "w2", "pane_id": "w2:p0", "tokens": {}}]

        def fake_cli(*args):
            if args[:2] == ("workspace", "create"):
                self.assertIn("herdr-dock2", args)
                return {"workspace": {"workspace_id": "w2"}}
            if args[:2] == ("agent", "list"):
                return {"agents": []}
            raise AssertionError(args)

        def fake_panes(ids):
            return existing + fresh if "w2" in ids else list(existing)

        with patch.object(
            dock_layout, "dock_workspaces", return_value=[{"workspace_id": "w1", "label": "herdr-dock"}]
        ), patch.object(dock_layout, "_panes_in", side_effect=fake_panes), patch.object(
            dock_layout.herdr_api, "cli", side_effect=fake_cli
        ):
            self.assertEqual(dock_layout.ensure_dock_pane("plugin4", "cwd"), ("w2", "w2:p0"))

        self.assertEqual(dock_layout.read_dock_pane(folder, "plugin4"), "w2:p0")

    def test_reconcile_and_list_cover_every_workspace(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "first", "w1:p0")
        dock_layout.write_dock_marker(folder, "second", "w2:p0")
        panes = [
            {"workspace_id": "w1", "pane_id": "w1:p0", "tokens": {}},
            {"workspace_id": "w2", "pane_id": "w2:p0", "tokens": {}},
        ]
        workspaces = [
            {"workspace_id": "w1", "label": "herdr-dock"},
            {"workspace_id": "w2", "label": "herdr-dock2"},
        ]

        with patch.object(dock_layout, "dock_workspaces", return_value=workspaces), patch.object(
            dock_layout, "_panes_in", return_value=panes
        ):
            docks = dock_layout.reconcile_dock_state()
            listed = {dock["key"]: dock for dock in dock_layout.list_docks()}

        self.assertEqual(docks["second"]["workspace_id"], "w2")
        self.assertEqual(listed["second"]["workspace"], "herdr-dock2")
        self.assertTrue(listed["first"]["live"] and listed["second"]["live"])

    def test_reset_closes_only_empty_extra_workspaces(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "first", "w1:p0")
        panes = [
            {"workspace_id": "w1", "pane_id": "w1:p0", "tokens": {}},
            {"workspace_id": "w2", "pane_id": "w2:side", "label": "Sidebar", "tokens": {"herdr-sidebar": "x"}},
            {"workspace_id": "w3", "pane_id": "w3:p0", "tokens": {}},
            {"workspace_id": "w3", "pane_id": "w3:busy", "label": "busy", "tokens": {}},
        ]
        workspaces = [
            {"workspace_id": "w1", "label": "herdr-dock"},
            {"workspace_id": "w2", "label": "herdr-dock2"},
            {"workspace_id": "w3", "label": "herdr-dock3"},
        ]

        def fake_cli(*args):
            return {"agents": []}

        with patch.object(dock_layout, "dock_workspaces", return_value=workspaces), patch.object(
            dock_layout, "dock_workspace_ids", return_value=["w1", "w2", "w3"]
        ), patch.object(
            dock_layout, "_panes_in", side_effect=lambda ids: [p for p in panes if p["workspace_id"] in ids]
        ), patch.object(dock_layout.herdr_api, "cli", side_effect=fake_cli) as cli:
            dock_layout.reset_dock_state()

        cli.assert_any_call("workspace", "close", "w2")
        closed = [call.args for call in cli.call_args_list]
        self.assertNotIn(("workspace", "close", "w1"), closed)
        self.assertNotIn(("workspace", "close", "w3"), closed)


if __name__ == "__main__":
    unittest.main()

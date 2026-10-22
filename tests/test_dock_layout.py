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

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
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

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
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

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
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

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
        ):
            docks = dock_layout.reconcile_dock_state()

        self.assertEqual(docks, {})

    def test_reconcile_imports_live_legacy_markers(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "legacy", "pane")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
        ):
            docks = dock_layout.reconcile_dock_state()

        self.assertEqual(docks["legacy"]["pane_id"], "pane")

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


class DockOperationTests(unittest.TestCase):
    setUp = DockLayoutTests.setUp

    def test_list_docks_reports_liveness(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "alive", "pane")
        dock_layout.write_dock_marker(folder, "gone", "missing")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
        ):
            docks = {dock["key"]: dock for dock in dock_layout.list_docks()}

        self.assertTrue(docks["alive"]["live"])
        self.assertFalse(docks["gone"]["live"])

    def test_reset_removes_only_dead_markers(self):
        folder = dock_layout.plugins_folder()
        dock_layout.write_dock_marker(folder, "alive", "pane")
        dock_layout.write_dock_marker(folder, "gone", "missing")
        panes = [{"workspace_id": "workspace", "pane_id": "pane", "tokens": {}}]

        with patch.object(dock_layout, "dock_workspace_id", return_value="workspace"), patch.object(
            dock_layout, "workspace_panes", return_value=panes
        ):
            removed = dock_layout.reset_dock_state()

        self.assertEqual(removed, ["gone"])
        self.assertEqual(dock_layout.read_dock_pane(folder, "alive"), "pane")


if __name__ == "__main__":
    unittest.main()

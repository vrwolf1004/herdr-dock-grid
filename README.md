# herdr-dock-grid

[**English**](README.md) | [한국어](README.ko.md)

Shared pane allocation and state management for the `herdr-dock` workspace used by herdr plugins.
Dock plugins no longer need their own slot rules: this plugin keeps the layout policy, the
occupancy state, and the cleanup logic in one place.

## Structure

- `src/dock_layout.py`: `*.dock` markers (source of truth), the registry (`herdr-dock-grid.json`), atomic locking, layout policy, snapshots, and management API
- `src/dock_cli.py`: management commands (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: herdr CLI/socket calls and installed-plugin path lookup

## API (`dock_layout`)

| Function | Description |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | Get a dock pane and return `(workspace_id, pane_id)`. Returns the existing pane if already held |
| `release_dock_pane(key)` | Release the allocation and marker (the pane itself is left untouched) |
| `register_dock(key, ...)` | Declare title, default position, minimum size, and entrypoint |
| `reconcile_dock_state()` | Rebuild the registry from markers and live panes |
| `list_docks()` | Report each dock's pane liveness (read-only) |
| `reset_dock_state()` | Clean up markers and allocations whose pane is gone |
| `get_layout_policy()` / `set_layout_policy()` | Layout policy (currently `grid-2x2`, up to 4 slots) |
| `save_layout_snapshot()` / `get_layout_snapshot()` | Save and read the pane topology snapshot |

## Installation

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## Actions

| Action | What it does |
| --- | --- |
| `list` | List docks and whether their panes are alive |
| `reset` | Clean up stale docks |
| `snapshot` | Save the current layout snapshot |

On Windows, append `-windows` to each action ID. Example:

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## Rules

- Markers are the source of truth. The registry is a secondary index rebuilt from markers and live panes. See [docs/design-install-order.md](docs/design-install-order.md).
- Other plugins use the installed copy (the local path shown by `herdr plugin list`) first, and fall back to their own `src/` copy. Change this repository first when shared logic changes.
- Connecting herdr-dock-grid is optional. Without it, each plugin still works with its own `src/dock_layout.py` copy (multiple dock workspaces and the management actions are available only from the installed copy).
- Bump `version` in `herdr-plugin.toml` for every changed plugin.

## Requirements

- herdr 0.9.0 or later
- Windows, Linux, or macOS
- Python 3.9 or later

## Development

```sh
python -m unittest discover -s tests -q
```

Status and remaining work: [docs/todo.md](docs/todo.md). Layout restoration is on hold because herdr has no whole-topology setter.

## Support the project

If this project is useful to you, consider buying the developer a coffee.

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

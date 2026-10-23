# herdr-dock-grid

[**English**](README.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

Languages: English (default) · Korean · Russian · French · Spanish · German · Japanese (documentation only; no UI)

Shared pane allocation and state management for the `herdr-dock` workspace used by herdr plugins.
Dock plugins no longer need their own slot rules: this plugin keeps the layout policy, the
occupancy state, and the cleanup logic in one place.

## Structure

- `src/dock_layout.py`: `*.dock` markers (source of truth), the registry (`herdr-dock-grid.json`), atomic locking, layout policy, snapshots, and management API
  - Read-only calls (`list_docks`, `save_layout_snapshot`, `get_layout_snapshot`) ask herdr outside the registry lock. `ensure_dock_pane`, `reset_dock_state`, and `reconcile_dock_state` still ask herdr while holding the lock, because they must act on the same pane list they check.
- `src/dock_cli.py`: management commands (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: herdr CLI/socket calls and installed-plugin path lookup
  - CLI calls time out after 10 seconds by default. Set `HERDR_CLI_TIMEOUT_SECONDS` to change it. A value that is not a number, or is 0 or less, falls back to 10 seconds.
  - When a call times out, a `check=True` call raises `HerdrError` ("no response within N s"), and a `check=False` call returns `None`. If herdr does not answer for a long time, expect this error rather than a hang.

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
- To check the copies against this repository, run `python tools/check_copies.py`. It prints same, different, or missing for each copy and exits with 0 only when all match.
- Connecting herdr-dock-grid is optional. Without it, each plugin still works with its own `src/dock_layout.py` copy (multiple dock workspaces and the management actions are available only from the installed copy).
- When a workspace has 4 blocks, the next block goes to `herdr-dock2`, then `herdr-dock3`, and so on. Empty `herdr-dockN` (N ≥ 2) workspaces are closed by `reset`, not by release. See [docs/design-multi-dock.md](docs/design-multi-dock.md).
- Bump `version` in `herdr-plugin.toml` for every changed plugin.

## Language

- This plugin has no language setting. Its CLI output and messages are in English.
- Each plugin chooses its own language with an environment variable: `HERDR_<NAME>_LANG` (for example `HERDR_TALK_LANG=ko`, `HERDR_TIMEKIT_LANG=ko`). Plugin config files can also set `lang`.
- Adding multi-language support to this plugin is not planned yet. If needed, record it in [docs/common-todo.md](docs/common-todo.md).

## Requirements

- herdr 0.9.0 or later
- Windows, Linux, or macOS
- Python 3.9 or later

## Development

```sh
python -m unittest discover -s tests -q
```

Status and remaining work: [docs/todo.md](docs/todo.md). Layout restoration is on hold because herdr has no whole-topology setter.

## Documentation

- [docs/design-install-order.md](docs/design-install-order.md): install and start order, marker-based rules
- [docs/design-multi-dock.md](docs/design-multi-dock.md): multiple dock workspaces
- [docs/migration-guide.md](docs/migration-guide.md): moving each plugin to this module
- [docs/common-todo.md](docs/common-todo.md): decisions and work shared across plugins
- [docs/todo.md](docs/todo.md): this plugin's status

## Support the project

If this project is useful to you, consider buying the developer a coffee.

[![Support on Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

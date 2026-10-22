# herdr-dock-grid

[English](README.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [Français](README.fr.md) | [Español](README.es.md) | [**Deutsch**](README.de.md) | [日本語](README.ja.md)

Languages: English (default) · Korean · Russian · French · Spanish · German · Japanese (documentation only; no UI)

Gemeinsame Pane-Verwaltung und Zustandsverwaltung für den `herdr-dock`-Workspace, den herdr-Plugins verwenden. Dock-Plugins brauchen keine eigenen Platzregeln mehr: Dieses Plugin bündelt Layout-Richtlinie, Belegungszustand und Aufräumlogik an einer Stelle.

## Aufbau

- `src/dock_layout.py`: `*.dock`-Marker (maßgeblich), Registry (`herdr-dock-grid.json`), atomare Sperre, Layout-Richtlinie, Snapshots und Verwaltungs-API
- `src/dock_cli.py`: Verwaltungsbefehle (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: herdr-CLI/Socket-Aufrufe und Suche des Pfads des installierten Plugins

## API (`dock_layout`)

| Funktion | Beschreibung |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | Holt eine Dock-Pane und gibt `(workspace_id, pane_id)` zurück. Gibt die bereits belegte Pane zurück, falls vorhanden |
| `release_dock_pane(key)` | Gibt die Belegung und den Marker frei (die Pane selbst bleibt unberührt) |
| `register_dock(key, ...)` | Deklariert Titel, Standardposition, Mindestgröße und Einstiegspunkt |
| `reconcile_dock_state()` | Baut die Registry aus Markern und aktiven Panes neu auf |
| `list_docks()` | Meldet für jedes Dock, ob seine Pane lebt (nur lesend) |
| `reset_dock_state()` | Räumt Marker und Belegungen auf, deren Pane verschwunden ist |
| `get_layout_policy()` / `set_layout_policy()` | Layout-Richtlinie (derzeit `grid-2x2`, bis zu 4 Plätze) |
| `save_layout_snapshot()` / `get_layout_snapshot()` | Speichert und liest die Pane-Topologie |

## Installation

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## Aktionen

| Aktion | Funktion |
| --- | --- |
| `list` | Listet die Docks und ob ihre Panes leben |
| `reset` | Räumt veraltete Docks auf |
| `snapshot` | Speichert den aktuellen Layout-Snapshot |

Unter Windows hängen Sie `-windows` an die Aktions-ID an. Beispiel:

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## Regeln

- Marker sind die maßgebliche Quelle. Die Registry ist ein sekundärer Index, der aus Markern und aktiven Panes neu aufgebaut wird. Siehe [docs/design-install-order.md](docs/design-install-order.md).
- Andere Plugins verwenden zuerst die installierte Kopie (der lokale Pfad aus `herdr plugin list`) und sonst ihre eigene Kopie in `src/`. Ändert sich gemeinsame Logik, ändern Sie zuerst dieses Repository.
- Die Verbindung zu herdr-dock-grid ist optional. Ohne sie arbeitet jedes Plugin mit seiner eigenen Kopie `src/dock_layout.py` (mehrere Dock-Workspaces und die Verwaltungsaktionen gibt es nur mit der installierten Version).
- Hat ein Workspace 4 Blöcke, kommt der nächste Block nach `herdr-dock2`, dann `herdr-dock3` usw. Leere `herdr-dockN` (N ≥ 2) schließt `reset`, nicht release. Siehe [docs/design-multi-dock.md](docs/design-multi-dock.md).
- Erhöhen Sie `version` in `herdr-plugin.toml` für jedes geänderte Plugin.

## Sprache

- Dieses Plugin hat keine Spracheinstellung. Seine CLI-Ausgabe und Meldungen sind auf Englisch.
- Jedes Plugin wählt seine Sprache über eine Umgebungsvariable, `HERDR_<NAME>_LANG` (z. B. `HERDR_TALK_LANG=ko`). Plugin-Konfigurationsdateien können auch `lang` setzen.
- Mehrsprachige Unterstützung für dieses Plugin ist noch nicht geplant. Falls nötig, vermerken Sie es in [docs/common-todo.md](docs/common-todo.md).

## Anforderungen

- herdr 0.9.0 oder neuer
- Windows, Linux oder macOS
- Python 3.9 oder neuer

## Entwicklung

```sh
python -m unittest discover -s tests -q
```

Status und offene Arbeit: [docs/todo.md](docs/todo.md). Die Wiederherstellung des Layouts ist zurückgestellt, weil herdr keinen Setter für die gesamte Topologie hat.

## Dokumentation

- [docs/design-install-order.md](docs/design-install-order.md): Reihenfolge von Installation und Start, markerbasierte Regeln
- [docs/design-multi-dock.md](docs/design-multi-dock.md): mehrere Dock-Workspaces
- [docs/migration-guide.md](docs/migration-guide.md): wie jedes Plugin auf dieses Modul umgestellt wird
- [docs/common-todo.md](docs/common-todo.md): Entscheidungen und plugin-übergreifende Arbeit
- [docs/todo.md](docs/todo.md): Status dieses Plugins

## Projekt unterstützen

Wenn Ihnen dieses Projekt nützt, spendieren Sie dem Entwickler gern einen Kaffee.

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

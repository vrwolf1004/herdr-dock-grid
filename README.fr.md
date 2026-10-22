# herdr-dock-grid

[English](README.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [**Français**](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

Languages: English (default) · Korean · Russian · French · Spanish · German · Japanese (documentation only; no UI)

Allocation partagée des panneaux et gestion de l'état pour le workspace `herdr-dock` utilisé par les plugins herdr. Les plugins de dock n'ont plus besoin de leurs propres règles d'emplacement : ce plugin centralise la politique de disposition, l'état d'occupation et la logique de nettoyage.

## Structure

- `src/dock_layout.py` : marqueurs `*.dock` (source de vérité), registre (`herdr-dock-grid.json`), verrouillage atomique, politique de disposition, instantanés et API de gestion
- `src/dock_cli.py` : commandes de gestion (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py` : appels CLI/socket herdr et recherche du chemin du plugin installé

## API (`dock_layout`)

| Fonction | Description |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | Obtient un panneau de dock et renvoie `(workspace_id, pane_id)`. Renvoie le panneau existant si déjà attribué |
| `release_dock_pane(key)` | Libère l'attribution et le marqueur (le panneau lui-même n'est pas touché) |
| `register_dock(key, ...)` | Déclare le titre, la position par défaut, la taille minimale et le point d'entrée |
| `reconcile_dock_state()` | Reconstruit le registre à partir des marqueurs et des panneaux actifs |
| `list_docks()` | Indique si le panneau de chaque dock est actif (lecture seule) |
| `reset_dock_state()` | Nettoie les marqueurs et attributions dont le panneau a disparu |
| `get_layout_policy()` / `set_layout_policy()` | Politique de disposition (actuellement `grid-2x2`, jusqu'à 4 emplacements) |
| `save_layout_snapshot()` / `get_layout_snapshot()` | Enregistre et lit la topologie des panneaux |

## Installation

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## Actions

| Action | Fonction |
| --- | --- |
| `list` | Liste les docks et indique si leurs panneaux sont actifs |
| `reset` | Nettoie les docks obsolètes |
| `snapshot` | Enregistre l'instantané de disposition actuel |

Sous Windows, ajoutez `-windows` à l'ID de l'action. Exemple :

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## Règles

- Les marqueurs sont la source de vérité. Le registre est un index secondaire reconstruit à partir des marqueurs et des panneaux actifs. Voir [docs/design-install-order.md](docs/design-install-order.md).
- Les autres plugins utilisent d'abord la copie installée (le chemin local affiché par `herdr plugin list`), puis leur propre copie `src/`. Modifiez d'abord ce dépôt lorsque la logique partagée change.
- La connexion à herdr-dock-grid est facultative. Sans elle, chaque plugin fonctionne avec sa propre copie `src/dock_layout.py` (plusieurs workspaces de dock et les actions de gestion ne sont disponibles que depuis la copie installée).
- Lorsqu'un workspace compte 4 blocs, le bloc suivant va dans `herdr-dock2`, puis `herdr-dock3`, etc. Les `herdr-dockN` vides (N ≥ 2) sont fermés par `reset`, pas par release. Voir [docs/design-multi-dock.md](docs/design-multi-dock.md).
- Augmentez `version` dans `herdr-plugin.toml` pour chaque plugin modifié.

## Langue

- Ce plugin n'a pas de réglage de langue. Sa sortie CLI et ses messages sont en anglais.
- Chaque plugin choisit sa langue avec une variable d'environnement, `HERDR_<NAME>_LANG` (par exemple `HERDR_TALK_LANG=ko`). Les fichiers de configuration des plugins peuvent aussi définir `lang`.
- Le support multilingue de ce plugin n'est pas encore prévu. Si besoin, notez-le dans [docs/common-todo.md](docs/common-todo.md).

## Prérequis

- herdr 0.9.0 ou plus récent
- Windows, Linux ou macOS
- Python 3.9 ou plus récent

## Développement

```sh
python -m unittest discover -s tests -q
```

État et travaux restants : [docs/todo.md](docs/todo.md). La restauration de la disposition est en attente car herdr n'a pas de setter de topologie complète.

## Documentation

- [docs/design-install-order.md](docs/design-install-order.md) : ordre d'installation et de démarrage, règles basées sur les marqueurs
- [docs/design-multi-dock.md](docs/design-multi-dock.md) : plusieurs workspaces de dock
- [docs/migration-guide.md](docs/migration-guide.md) : comment migrer chaque plugin vers ce module
- [docs/common-todo.md](docs/common-todo.md) : décisions et travaux partagés entre les plugins
- [docs/todo.md](docs/todo.md) : état de ce plugin

## Soutenir le projet

Si ce projet vous est utile, pensez à offrir un café au développeur.

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

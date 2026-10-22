# herdr-dock-grid

[English](README.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [Français](README.fr.md) | [**Español**](README.es.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

Languages: English (default) · Korean · Russian · French · Spanish · German · Japanese (documentation only; no UI)

Asignación compartida de paneles y gestión de estado para el workspace `herdr-dock` que usan los plugins de herdr. Los plugins de dock ya no necesitan sus propias reglas de ubicación: este plugin centraliza la política de disposición, el estado de ocupación y la lógica de limpieza.

## Estructura

- `src/dock_layout.py`: marcadores `*.dock` (fuente de verdad), registro (`herdr-dock-grid.json`), bloqueo atómico, política de disposición, instantáneas y API de gestión
- `src/dock_cli.py`: comandos de gestión (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: llamadas CLI/socket de herdr y búsqueda de la ruta del plugin instalado

## API (`dock_layout`)

| Función | Descripción |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | Obtiene un panel del dock y devuelve `(workspace_id, pane_id)`. Devuelve el panel existente si ya está asignado |
| `release_dock_pane(key)` | Libera la asignación y el marcador (el panel en sí no se toca) |
| `register_dock(key, ...)` | Declara el título, la posición por defecto, el tamaño mínimo y el punto de entrada |
| `reconcile_dock_state()` | Reconstruye el registro a partir de los marcadores y los paneles activos |
| `list_docks()` | Informa si el panel de cada dock está activo (solo lectura) |
| `reset_dock_state()` | Limpia marcadores y asignaciones cuyo panel ya no existe |
| `get_layout_policy()` / `set_layout_policy()` | Política de disposición (actualmente `grid-2x2`, hasta 4 huecos) |
| `save_layout_snapshot()` / `get_layout_snapshot()` | Guarda y lee la topología de paneles |

## Instalación

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## Acciones

| Acción | Qué hace |
| --- | --- |
| `list` | Lista los docks y si sus paneles están activos |
| `reset` | Limpia los docks obsoletos |
| `snapshot` | Guarda la instantánea de disposición actual |

En Windows, añada `-windows` al ID de la acción. Ejemplo:

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## Reglas

- Los marcadores son la fuente de verdad. El registro es un índice secundario reconstruido a partir de los marcadores y los paneles activos. Vea [docs/design-install-order.md](docs/design-install-order.md).
- Los demás plugins usan primero la copia instalada (la ruta local que muestra `herdr plugin list`) y, si no existe, su propia copia en `src/`. Cuando cambie la lógica compartida, modifique primero este repositorio.
- Conectar herdr-dock-grid es opcional. Sin él, cada plugin funciona con su propia copia `src/dock_layout.py` (varios workspaces de dock y las acciones de gestión solo están disponibles desde la copia instalada).
- Cuando un workspace tiene 4 bloques, el siguiente bloque va a `herdr-dock2`, luego `herdr-dock3`, etc. Los `herdr-dockN` vacíos (N ≥ 2) los cierra `reset`, no release. Vea [docs/design-multi-dock.md](docs/design-multi-dock.md).
- Suba `version` en `herdr-plugin.toml` en cada plugin modificado.

## Idioma

- Este plugin no tiene ajuste de idioma. Su salida CLI y sus mensajes están en inglés.
- Cada plugin elige su idioma con una variable de entorno, `HERDR_<NAME>_LANG` (por ejemplo `HERDR_TALK_LANG=ko`). Los archivos de configuración de los plugins también pueden definir `lang`.
- El soporte multilingüe de este plugin no está previsto por ahora. Si hace falta, anótelo en [docs/common-todo.md](docs/common-todo.md).

## Requisitos

- herdr 0.9.0 o posterior
- Windows, Linux o macOS
- Python 3.9 o posterior

## Desarrollo

```sh
python -m unittest discover -s tests -q
```

Estado y trabajo pendiente: [docs/todo.md](docs/todo.md). La restauración de la disposición está en pausa porque herdr no tiene un setter de topología completa.

## Documentación

- [docs/design-install-order.md](docs/design-install-order.md): orden de instalación y arranque, reglas basadas en marcadores
- [docs/design-multi-dock.md](docs/design-multi-dock.md): varios workspaces de dock
- [docs/migration-guide.md](docs/migration-guide.md): cómo migrar cada plugin a este módulo
- [docs/common-todo.md](docs/common-todo.md): decisiones y trabajo compartido entre plugins
- [docs/todo.md](docs/todo.md): estado de este plugin

## Apoya el proyecto

Si este proyecto le resulta útil, considere invitar al desarrollador a un café.

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

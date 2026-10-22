# herdr-dock-grid

[English](README.md) | [한국어](README.ko.md) | [**Русский**](README.ru.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

Языки: английский (по умолчанию) · корейский · русский · французский · испанский · немецкий · японский (только документация; интерфейса нет)

Общее управление размещением панелей и состоянием для рабочего пространства `herdr-dock`, которое используют плагины herdr. Плагинам дока больше не нужны собственные правила размещения: этот плагин хранит политику раскладки, состояние занятости и логику очистки в одном месте.

## Структура

- `src/dock_layout.py`: маркеры `*.dock` (источник истины), реестр (`herdr-dock-grid.json`), атомарная блокировка, политика раскладки, снимки и API управления
- `src/dock_cli.py`: команды управления (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: вызовы herdr CLI/сокета и поиск пути установленного плагина

## API (`dock_layout`)

| Функция | Описание |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | Получает панель дока и возвращает `(workspace_id, pane_id)`. Если панель уже закреплена, возвращает её |
| `release_dock_pane(key)` | Освобождает закрепление и маркер (сама панель не трогается) |
| `register_dock(key, ...)` | Объявляет заголовок, позицию по умолчанию, минимальный размер и точку входа |
| `reconcile_dock_state()` | Пересобирает реестр по маркерам и живым панелям |
| `list_docks()` | Показывает, жива ли панель каждого дока (только чтение) |
| `reset_dock_state()` | Очищает маркеры и закрепления, у которых панель исчезла |
| `get_layout_policy()` / `set_layout_policy()` | Политика раскладки (сейчас `grid-2x2`, до 4 мест) |
| `save_layout_snapshot()` / `get_layout_snapshot()` | Сохраняет и читает топологию панелей |

## Установка

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## Действия

| Действие | Что делает |
| --- | --- |
| `list` | Показывает доки и живы ли их панели |
| `reset` | Очищает устаревшие доки |
| `snapshot` | Сохраняет текущий снимок раскладки |

В Windows добавьте `-windows` к ID действия. Пример:

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## Правила

- Маркеры — источник истины. Реестр — вспомогательный индекс, который пересобирается по маркерам и живым панелям. См. [docs/design-install-order.md](docs/design-install-order.md).
- Другие плагины сначала используют установленную копию (локальный путь из `herdr plugin list`), а если её нет — свою копию в `src/`. Когда меняется общая логика, сначала меняйте этот репозиторий.
- Подключение herdr-dock-grid необязательно. Без него каждый плагин работает со своей копией `src/dock_layout.py` (несколько рабочих пространств дока и действия управления доступны только из установленной копии).
- Когда в рабочем пространстве 4 блока, следующий блок идёт в `herdr-dock2`, затем в `herdr-dock3` и так далее. Пустые `herdr-dockN` (N ≥ 2) закрывает `reset`, а не release. См. [docs/design-multi-dock.md](docs/design-multi-dock.md).
- Увеличивайте `version` в `herdr-plugin.toml` для каждого изменённого плагина.

## Язык

- В этом плагине нет настройки языка. Вывод CLI и сообщения на английском.
- Каждый плагин выбирает язык переменной окружения `HERDR_<NAME>_LANG` (например, `HERDR_TALK_LANG=ko`). Файлы конфигурации плагинов тоже могут задавать `lang`.
- Многоязычная поддержка этого плагина пока не запланирована. Если понадобится, запишите в [docs/common-todo.md](docs/common-todo.md).

## Требования

- herdr 0.9.0 или новее
- Windows, Linux или macOS
- Python 3.9 или новее

## Разработка

```sh
python -m unittest discover -s tests -q
```

Состояние и оставшаяся работа: [docs/todo.md](docs/todo.md). Восстановление раскладки отложено, потому что в herdr нет установщика всей топологии.

## Документация

- [docs/design-install-order.md](docs/design-install-order.md): порядок установки и запуска, правила на основе маркеров
- [docs/design-multi-dock.md](docs/design-multi-dock.md): несколько рабочих пространств дока
- [docs/migration-guide.md](docs/migration-guide.md): как перевести каждый плагин на этот модуль
- [docs/common-todo.md](docs/common-todo.md): решения и общая работа плагинов
- [docs/todo.md](docs/todo.md): состояние этого плагина

## Поддержать проект

Если проект вам полезен, угостите разработчика чашкой кофе.

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

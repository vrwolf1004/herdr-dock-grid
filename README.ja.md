# herdr-dock-grid

[English](README.md) | [한국어](README.ko.md) | [Русский](README.ru.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [**日本語**](README.ja.md)

Languages: English (default) · Korean · Russian · French · Spanish · German · Japanese (documentation only; no UI)

herdr プラグインが共有する `herdr-dock` ワークスペースの pane 割り当てと状態管理を行います。ドックのプラグインはそれぞれ配置ルールを持つ必要がなく、このプラグインがレイアウト方針・占有状態・後片付けのロジックを一か所で管理します。

## 構成

- `src/dock_layout.py`: `*.dock` マーカー（正本）、レジストリ（`herdr-dock-grid.json`）、アトミックなロック、レイアウト方針、スナップショット、管理 API
- `src/dock_cli.py`: 管理コマンド（`list`、`status`、`reconcile`、`reset`、`snapshot`、`policy`）
- `src/herdr_api.py`: herdr の CLI/ソケット呼び出しと、インストール済みプラグインのパス検索

## API (`dock_layout`)

| 関数 | 説明 |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | ドックの pane を確保し `(workspace_id, pane_id)` を返す。すでに確保済みなら既存の pane を返す |
| `release_dock_pane(key)` | 確保とマーカーを解放する（pane 自体は触らない） |
| `register_dock(key, ...)` | タイトル、既定の位置、最小サイズ、エントリポイントを宣言する |
| `reconcile_dock_state()` | マーカーと実在する pane からレジストリを作り直す |
| `list_docks()` | 各ドックの pane が生きているかを返す（読み取り専用） |
| `reset_dock_state()` | pane が消えたマーカーと確保を片付ける |
| `get_layout_policy()` / `set_layout_policy()` | レイアウト方針（現在 `grid-2x2`、最大 4 枠） |
| `save_layout_snapshot()` / `get_layout_snapshot()` | pane のトポロジーのスナップショットを保存・読み込む |

## インストール

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## アクション

| アクション | 内容 |
| --- | --- |
| `list` | ドックの一覧と pane の生存状態を表示 |
| `reset` | 古いドックを片付ける |
| `snapshot` | 現在のレイアウトのスナップショットを保存 |

Windows では各アクション ID の末尾に `-windows` を付けます。例：

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## ルール

- マーカーが正本です。レジストリはマーカーと実在する pane から再構築される補助インデックスです。詳しくは [docs/design-install-order.md](docs/design-install-order.md) を参照してください。
- 他のプラグインは、まずインストール済みのコピー（`herdr plugin list` に表示されるローカルパス）を使い、なければ自分の `src/` のコピーを使います。共有ロジックを変えるときは、まずこのリポジトリを修正してください。
- herdr-dock-grid への接続は任意です。接続していなくても、各プラグインは自分の `src/dock_layout.py` のコピーで動作します（複数のドックワークスペースと管理アクションは、インストール済みのコピーでのみ使えます）。
- ワークスペースに 4 ブロックあるとき、次のブロックは `herdr-dock2`、その次は `herdr-dock3` に配置されます。空の `herdr-dockN`（N ≥ 2）は release ではなく `reset` で閉じます。詳しくは [docs/design-multi-dock.md](docs/design-multi-dock.md) を参照してください。
- 変更したプラグインは `herdr-plugin.toml` の `version` を上げます。

## 言語

- このプラグインには言語設定がありません。CLI の出力とメッセージは英語です。
- 各プラグインは環境変数 `HERDR_<NAME>_LANG` で言語を選びます（例：`HERDR_TALK_LANG=ko`）。プラグインの設定ファイルの `lang` も使えます。
- このプラグインの多言語対応は今のところ予定していません。必要になったら [docs/common-todo.md](docs/common-todo.md) に記録します。

## 要件

- herdr 0.9.0 以上
- Windows、Linux、macOS
- Python 3.9 以上

## 開発

```sh
python -m unittest discover -s tests -q
```

状態と残作業は [docs/todo.md](docs/todo.md) を参照してください。herdr にトポロジー全体を設定する API がないため、レイアウトの復元は保留中です。

## ドキュメント

- [docs/design-install-order.md](docs/design-install-order.md): インストールと起動の順序、マーカー基準のルール
- [docs/design-multi-dock.md](docs/design-multi-dock.md): 複数のドックワークスペース
- [docs/migration-guide.md](docs/migration-guide.md): 各プラグインをこのモジュールへ移行する方法
- [docs/common-todo.md](docs/common-todo.md): プラグイン共通の決定事項と作業
- [docs/todo.md](docs/todo.md): このプラグインの状態

## プロジェクトを応援する

このプロジェクトが役に立ったら、開発者にコーヒーを一杯おごってください。

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

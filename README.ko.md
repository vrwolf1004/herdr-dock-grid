# herdr-dock-grid

[English](README.md) | [**한국어**](README.ko.md)

herdr 플러그인들이 공용 `herdr-dock` 워크스페이스에서 쓰는 pane 배치와 점유 상태를 관리합니다.
도크 플러그인마다 자리 규칙을 따로 구현할 필요 없이, 레이아웃 정책·점유 상태·정리 로직을 이 플러그인 한 곳에서 관리합니다.

## 구성

- `src/dock_layout.py`: `*.dock` marker(정본), 레지스트리(`herdr-dock-grid.json`), 원자적 잠금, 레이아웃 정책, 스냅샷, 조작 API
- `src/dock_cli.py`: 관리 명령 (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: herdr CLI/socket 호출, 설치된 플러그인 경로 탐색

## API (`dock_layout`)

| 함수 | 설명 |
| --- | --- |
| `ensure_dock_pane(key, cwd)` | 도크 pane을 확보해 `(workspace_id, pane_id)` 반환. 이미 점유했으면 그대로 반환 |
| `release_dock_pane(key)` | 점유와 marker 해제 (pane 자체는 건드리지 않음) |
| `register_dock(key, ...)` | 제목·기본 위치·최소 크기·진입점 선언 |
| `reconcile_dock_state()` | marker와 실제 pane으로 레지스트리 재구성 |
| `list_docks()` | 도크별 pane 생존 여부 조회 (읽기 전용) |
| `reset_dock_state()` | 사라진 pane의 marker·할당 정리 |
| `get_layout_policy()` / `set_layout_policy()` | 레이아웃 정책 (현재 `grid-2x2`, 최대 4칸) |
| `save_layout_snapshot()` / `get_layout_snapshot()` | pane topology 스냅샷 저장·조회 |

## 설치

```sh
herdr plugin install vrwolf1004/herdr-dock-grid
```

## 액션

| 액션 | 기능 |
| --- | --- |
| `list` | 도크 목록과 pane 생존 여부 확인 |
| `reset` | 사라진 도크 정리 |
| `snapshot` | 현재 레이아웃 스냅샷 저장 |

Windows에서는 각 액션 ID 뒤에 `-windows`를 붙입니다. 예:

```sh
herdr plugin action invoke list-windows --plugin herdr-dock-grid
```

## 규칙

- marker가 정본입니다. 레지스트리는 marker와 실제 pane에서 재구성되는 보조 인덱스입니다. 자세한 내용은 [docs/design-install-order.md](docs/design-install-order.md)를 참고하세요.
- 다른 플러그인은 설치본(`herdr plugin list`에 보이는 local 경로)을 우선 쓰고, 없으면 자기 `src/` 복사본을 씁니다. 공용 로직을 바꿀 때는 이 저장소를 먼저 고칩니다.
- herdr-dock-grid 연결은 선택입니다. 설치되어 있지 않아도 각 플러그인의 `src/dock_layout.py` 복사본으로 동작합니다(다중 워크스페이스와 관리 기능은 설치본에서만 쓸 수 있습니다).
- 바뀐 플러그인은 `herdr-plugin.toml`의 version을 올립니다.

## 요구 사항

- herdr 0.9.0 이상
- Windows, Linux, macOS
- Python 3.9 이상

## 개발

```sh
python -m unittest discover -s tests -q
```

상태와 남은 일은 [docs/todo.md](docs/todo.md)를 참고하세요. 레이아웃 복원은 herdr에 전체 topology setter가 없어 보류 중입니다.

## 프로젝트 응원하기

프로젝트가 도움이 되셨다면 커피 한 잔으로 개발을 응원해 주세요.

[![Ko-fi에서 응원하기](https://img.shields.io/badge/Ko--fi-%EC%9D%91%EC%9B%90%ED%95%98%EA%B8%B0-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

# herdr-dock-grid

[English](README.md) | [**한국어**](README.ko.md) | [Русский](README.ru.md) | [Français](README.fr.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [日本語](README.ja.md)

지원 언어: 영어(기본) · 한국어 · 러시아어 · 프랑스어 · 스페인어 · 독일어 · 일본어 (문서만 해당, UI 없음)

herdr 플러그인들이 공용 `herdr-dock` 워크스페이스에서 쓰는 pane 배치와 점유 상태를 관리합니다.
도크 플러그인마다 자리 규칙을 따로 구현할 필요 없이, 레이아웃 정책·점유 상태·정리 로직을 이 플러그인 한 곳에서 관리합니다.

## 구성

- `src/dock_layout.py`: `*.dock` marker(정본), 레지스트리(`herdr-dock-grid.json`), 원자적 잠금, 레이아웃 정책, 스냅샷, 조작 API
  - 조회만 하는 호출(`list_docks`, `save_layout_snapshot`, `get_layout_snapshot`)은 herdr에 묻는 부분을 레지스트리 잠금 밖에서 합니다. `ensure_dock_pane`, `reset_dock_state`, `reconcile_dock_state`는 확인하는 pane 목록과 같은 순간의 목록이 필요해서 잠금을 쥔 채 herdr에 묻습니다.
- `src/dock_cli.py`: 관리 명령 (`list`, `status`, `reconcile`, `reset`, `snapshot`, `policy`)
- `src/herdr_api.py`: herdr CLI/socket 호출, 설치된 플러그인 경로 탐색
  - CLI 호출은 기본 10초가 지나면 제한 시간에 걸립니다. 환경 변수 `HERDR_CLI_TIMEOUT_SECONDS`로 바꿀 수 있습니다. 숫자가 아니거나 0 이하면 10초를 씁니다.
  - 제한 시간이 지나면 `check=True` 호출은 `HerdrError`("no response within N s")를 내고, `check=False` 호출은 `None`을 돌려줍니다. herdr가 오래 응답하지 않으면 멈추는 대신 이 오류가 납니다.

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
- 복사본이 이 저장소와 같은지 확인하려면 `python tools/check_copies.py`를 실행합니다. 복사본마다 같음, 다름, 없음을 출력하며, 모두 같을 때만 종료 코드 0을 돌려줍니다.
- herdr-dock-grid 연결은 선택입니다. 설치되어 있지 않아도 각 플러그인의 `src/dock_layout.py` 복사본으로 동작합니다(다중 워크스페이스와 관리 기능은 설치본에서만 쓸 수 있습니다).
- 블록이 4개 차면 다음 블록은 `herdr-dock2`, 그다음은 `herdr-dock3` 순서로 배치합니다. 빈 `herdr-dockN`(N ≥ 2)은 release 가 아니라 `reset` 에서 닫습니다. 자세한 내용은 [docs/design-multi-dock.md](docs/design-multi-dock.md)를 참고하세요.
- 바뀐 플러그인은 `herdr-plugin.toml`의 version을 올립니다.

## 언어

- 이 플러그인에는 언어 설정이 없습니다. CLI 출력과 메시지는 영문입니다.
- 각 플러그인은 환경 변수 `HERDR_<이름>_LANG`으로 언어를 고릅니다(예: `HERDR_TALK_LANG=ko`, `HERDR_TIMEKIT_LANG=ko`). 플러그인 설정 파일의 `lang` 도 쓸 수 있습니다.
- 이 플러그인의 다국어 지원은 아직 계획에 없습니다. 필요하면 [docs/common-todo.md](docs/common-todo.md)에 적습니다.

## 요구 사항

- herdr 0.9.0 이상
- Windows, Linux, macOS
- Python 3.9 이상

## 개발

```sh
python -m unittest discover -s tests -q
```

상태와 남은 일은 [docs/todo.md](docs/todo.md)를 참고하세요. 레이아웃 복원은 herdr에 전체 topology setter가 없어 보류 중입니다.

## 문서

- [docs/design-install-order.md](docs/design-install-order.md): 설치와 실행 순서, marker 기준 규칙
- [docs/design-multi-dock.md](docs/design-multi-dock.md): 여러 도크 워크스페이스
- [docs/migration-guide.md](docs/migration-guide.md): 각 플러그인을 이 모듈로 옮기는 방법
- [docs/common-todo.md](docs/common-todo.md): 플러그인 공통 결정과 작업
- [docs/todo.md](docs/todo.md): 이 플러그인의 상태

## 프로젝트 응원하기

프로젝트가 도움이 되셨다면 커피 한 잔으로 개발을 응원해 주세요.

[![Ko-fi에서 응원하기](https://img.shields.io/badge/Ko--fi-%EC%9D%91%EC%9B%90%ED%95%98%EA%B8%B0-FF5E5B?style=for-the-badge&logo=buymeacoffee&logoColor=white)](https://ko-fi.com/dev_ohyt)

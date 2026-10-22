# 인수인계: 도크 공용 모듈 적용 (Copilot 용)

## 목적
herdr-dock 워크스페이스의 2x2 배치와 자리 규칙을 한 곳(`herdr-dock-grid/src/dock_layout.py`)에서 관리한다.
herdr-dock-grid 가 설치되어 있으면 그 원본을 쓰고, 없으면 각 plugin 의 `src/dock_layout.py` 복사본을 쓴다.

## 현재 상태 (커밋 안 됨)

| 저장소 | 상태 | 내용 |
|---|---|---|
| herdr-dock-grid | 새 저장소, origin 설정됨, 커밋 없음 | 공용 모듈 원본, `installed_plugin_path` |
| herdr-timekit | 변경 있음 (version 0.5.3 상태) | 공용 모듈 사용. 테스트 35개 통과 |
| herdr-simple-git | 변경 있음 (version 0.5.3 상태) | 공용 모듈 사용. 테스트 15개 통과 |
| herdr-talk | 변경 있음 (version 0.5.2 상태) | 도크 블록 기능 + 공용 모듈 사용. 테스트 19개 통과 |

- 세 plugin 모두 `py_compile` 과 단위 테스트 통과. 실제 herdr 에서 공용 모듈 적용 후 재시작 테스트는 하지 않았다.
- `herdr-dock-grid` 는 local link로 설치되어 있다. 설치된 공용 모듈의 버전은 `0.6.0`이다. herdr 액션 `list`, `reset`, `snapshot`(`*-windows` 포함)으로 도크 상태를 조회·정리·저장할 수 있다.

## 2026-10-22 실제 herdr 검증

- `herdr plugin link C:\work\app\herdr-dock-grid --enabled`로 공용 모듈을 활성화했다.
- `herdr-timekit`, `local.simple-git`, `herdr-talk`의 Windows 도크 시작 액션을 동시에 실행했고 모두 성공했다.
- `reconcile_dock_state()`가 기존 marker를 `herdr-dock-grid.json` 레지스트리로 이관했다.
- 이관된 pane은 `herdr-simple-git` → `wN:pG`, `herdr-talk` → `wN:pK`, `herdr-timekit` → `wN:pH`이며 중복이 없었다.

## 파일 구조
- `herdr-dock-grid/src/dock_layout.py`: 원본. 상태 레지스트리, 원자적 잠금, marker 호환 이관, pane 검증, 레이아웃 정책, 버전 관리 스냅샷, `ensure_dock_pane(key, cwd)` → `(workspace_id, pane_id)`
- `herdr-dock-grid/src/herdr_api.py`: herdr 호출 + `installed_plugin_path(plugin_id)` (herdr plugin list 에서 활성 local 경로 찾기)
- 각 plugin `src/dock_layout.py`, `src/herdr_api.py`: 원본과 같은 내용의 복사본
- 각 plugin 의 `load_dock_layout()`: 설치본 우선, 없으면 복사본. 모듈 `dock` 으로 불러 쓴다.

## 규칙 (반드시 지킬 것)
1. 공용 로직을 바꾸려면 **원본(herdr-dock-grid)** 을 먼저 고치고, 각 plugin 의 `src/dock_layout.py` 와 `src/herdr_api.py` 를 같은 내용으로 맞춘다.
2. 공용 모듈은 모든 `*.dock` marker를 동적으로 읽는다. 새 플러그인은 고정 순서 목록을 수정하지 않고 marker와 `ensure_dock_pane()`으로 점유를 등록한다.
3. 바뀐 plugin 은 `herdr-plugin.toml` 의 version 을 올린다.
4. herdr 플러그인끼리 모듈을 공유하지 않는다는 원칙은 그대로다. 설치본 참조는 `herdr plugin list` 에 경로가 보이는 local 설치에만 된다.

## 남은 일 (우선순위 순)
완료: 레지스트리/락/마커 우선 정합, 배치 정책, 레이아웃 스냅샷 저장·조회, `list`/`reset`/`snapshot` 동작과 CLI(`src/dock_cli.py`), 한영 README, 실제 herdr 확인(timekit, simple-git, talk).
1. **다른 플러그인 이전**: timekit, simple-git, ai-feedbag, radio, stockpulse 는 아직 옛 방식(`wait_for_earlier`, `write_dock_marker`, `claimed_dock_panes`, `grid_split`, 자체 `pane.id`)이다. 공용 `ensure_dock_pane()` / `release_dock_pane()` 으로 옮기고 각자 테스트. 이 저장소 밖 작업이며 Claude 가 맡는다. 호환을 위해 `wait_for_earlier` 는 공용 모듈에 남겨 두었다.
2. **레이아웃 복원**: herdr 에 전체 배치 설정 API 가 없어 보류. 스냅샷 저장·조회만 가능.
3. **프로토콜 버전 불일치 경고**: 옛 복사본의 동작을 확인한 뒤 결정.
4. **소개 칸(`ensure_intro`)**: timekit, simple-git 에만 있다. 공용 모듈에는 넣지 않기로 했다. 소개 내용은 plugin 별로 둔다.
5. **GitHub 설치본 경로**: `herdr plugin list` 가 GitHub 설치본의 폴더를 보여 주지 않는다. 이 경우 복사본으로 동작한다. 실제 설치본 경로를 찾는 방법을 확인할 것.

## 알려진 문제
- talk 도크 블록: talk 의 10분 무활동 자동 종료가 그대로 적용되어, 10분 뒤 블록이 사라진다. 항상 떠 있게 할지 정해야 한다.
- talk 블록 클릭 시 대화창 포커스: 실제 herdr 에서 확인하지 않았다.
- simple-git: 상태 폴더 환경변수가 없으면 표시 파일 위치가 timekit 과 달라진다. herdr 가 항상 환경변수를 주는지 확인할 것.
- simple-git 에이전트가 25초 넘게 등록되지 않은 적이 있었다(이후 재실행 때는 정상). 원인 미확인.
- 정지 후 simple-git 의 이전 pane 이 빈 pane 으로 남은 적이 있다. 원인 미확인.

## 테스트 명령
```
cd <plugin 폴더>
python -m py_compile src/*.py
python -m unittest discover -s tests -q
```
herdr 동작 확인은 `herdr plugin action invoke <action> --plugin <id>` 로 하고, 결과는 `herdr pane list`, `herdr agent list`, `%LOCALAPPDATA%\herdr\plugins\*.dock` 로 본다.

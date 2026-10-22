# 다른 플러그인 이전 가이드

각 플러그인의 도크 코드를 herdr-dock-grid 공용 모듈로 바꾸는 방법. 이 저장소는 수정하지 않고 각 플러그인 쪽에서만 작업한다.

## 바꿀 것
옛 방식은 플러그인마다 아래를 직접 호출하고 자체 `pane.id` 파일을 둔다.

- `wait_for_earlier`, `write_dock_marker`, `claimed_dock_panes`, `grid_split`

이를 한 번의 호출로 바꾼다.

```python
dock = load_dock_layout()  # 설치된 herdr-dock-grid 우선, 없으면 복사본
workspace_id, pane_id = dock.ensure_dock_pane(DOCK_KEY, cwd)
```

- 종료 시 `dock.release_dock_pane(DOCK_KEY)` (pane 자체는 건드리지 않는다).
- 이미 할당돼 있으면 같은 pane 을 돌려주므로 여러 번 호출해도 안전하다.
- 자리가 없으면 `HerdrError` 가 나므로 기존 오류 처리 경로에 연결한다.

## 호환 규칙
- 마커(`<key>.dock`)가 기준이다. 레지스트리는 마커에서 다시 만들 수 있는 보조 색인이다.
- 키는 `herdr-<이름>` 이다. 예외로 simple-git 의 키는 `herdr-simple-git` 이고 herdr 플러그인 ID 는 `local.simple-git` 이다.
- 이전 전 플러그인과 이전 후 플러그인이 함께 떠도 자리가 겹치지 않는다. `wait_for_earlier` 는 호환용으로 남아 있다.
- 복사본 `src/dock_layout.py`, `src/herdr_api.py` 는 설치본이 없을 때의 대비용이므로 설치본 경로 탐색(`installed_plugin_path`)이 확인된 뒤에만 지운다. 복사본의 `DOCK_ORDER` 에 없는 키는 옛 복사본에서 오류가 난다.

## 순서
timekit → simple-git → talk → radio → ai-feedbag → stockpulse

## 플러그인별 확인
1. `python -m unittest discover -s tests -q` 통과.
2. `herdr plugin action invoke <dock-start 동작> --plugin <id>` 실행.
3. `herdr pane list` 로 pane 중복이 없는지, `herdr plugin action invoke list --plugin herdr-dock-grid` 로 `live` 인지 확인.
4. 이미 떠 있는 상태에서 다시 실행해도 새 pane 이 생기지 않는지 확인.

## 플러그인별 메모
- timekit, simple-git: `ensure_intro` 는 플러그인 쪽에 둔다.
- talk: 10분 무활동 자동 종료가 있어 블록이 사라진다. 유지 여부는 미정.
- simple-git: 상태 폴더 환경변수가 없으면 마커 위치가 달라질 수 있다.

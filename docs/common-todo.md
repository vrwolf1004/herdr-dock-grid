# 공통 TODO (도크 공용 모듈과 플러그인 공통)

이 문서는 herdr-dock-grid 를 포함한 여러 플러그인에 걸친 결정 사항과 남은 작업을 모은다.
저장소 고유 항목은 각 저장소의 `docs/todo.md` 에 둔다. 이 파일은 Copilot 이 작업 중인 `todo.md`, `handoff-copilot.md` 와 겹치지 않도록 따로 둔다.

## 결정 필요

- [x] **radio 옛 블록 정리**: 승인되어 진행했다. radio 를 정지하고 pane `wN:pA` 를 닫았으며, `release_dock_pane("herdr-radio")` 로 레지스트리 항목과 표시 파일을 지웠다. 이후 도크는 3개(ai-feedbag, simple-git, timekit)만 남았다.
- [x] **자리 정책 (결정)**: 워크스페이스당 4개(`grid-2x2`)를 유지한다. 블록이 4개를 넘으면 `herdr-dock2` 워크스페이스를 새로 만들어 거기에 배치한다. 같은 방식으로 필요하면 `herdr-dock3` 등으로 이어진다.
  - [ ] 구현: `ensure_dock_pane` 이 빈 자리가 없으면 다음 dock 워크스페이스(`herdr-dock2`, ...)를 찾거나 만든다.
  - [ ] 레지스트리: 각 항목에 `workspace_id` 가 이미 있으므로 여러 워크스페이스를 같은 레지스트리에서 관리한다. `list_docks`, `reset_dock_state`, `reconcile_dock_state` 가 모든 dock 워크스페이스를 본다.
  - [ ] 표시 파일(`<key>.dock`)은 그대로 둔다. 워크스페이스가 달라도 pane id 로 구분된다.
  - [ ] 워크스페이스 정리: 비어 있는 `herdr-dock2` 는 마지막 블록이 빠질 때 닫는다(또는 남긴다. 정한다).
  - [x] 확인(5번째 블록): stockpulse 대시보드가 `herdr-dock2`(`wP:p1`)에 뜨고 레지스트리에 워크스페이스 ID 가 기록됐다. 자리는 겹치지 않았다.
  - [x] 확인(정리): 블록을 닫고 `reset` 을 실행하면 빈 `herdr-dock2` 가 닫힌다. Copilot 이 사이드바 pane 을 검사에서 제외하도록 고쳤고, 라이브에서 `herdr-dock2` 가 없어졌으며 `herdr-dock` 의 기존 4개 블록은 그대로다. 단위 테스트 18개 통과.
  - 상세 설계: `docs/design-multi-dock.md`
- [x] **talk 블록 기동 시점**: radio 정리 후 자리가 생겨서 talk 블록을 띄웠다(아래 테스트 항목 참고).
- [x] **talk 10분 무활동 자동 종료 (결정: 유지)**: 자동 종료 유지(블록은 10분 무활동 후 사라짐).
- [x] **grid 링크 상태 (결정: 링크 유지)**: grid 는 링크(설치)된 상태로 유지한다.
- [x] **grid 연결 여부 (결정: 선택)**: herdr-dock-grid 연결은 선택이다. 설치되어 있지 않아도 각 플러그인의 `src/dock_layout.py` 복사본으로 동작한다(다중 워크스페이스와 관리 기능은 설치본에서만).
- [ ] **커밋과 푸시**: grid, timekit, simple-git, talk, radio, ai-feedbag, stockpulse 모두 커밋하지 않은 상태다. 커밋 순서, 메시지, 원격 푸시 여부를 정한다.

## 테스트 미완료

- [x] **S1 검증 (grid 설치 상태)**: timekit, simple-git, ai-feedbag 이 모두 grid 원본(`herdr-dock-grid\src\dock_layout.py`)을 불러온다. 이전 확인 코드의 `sys.path` 오류였고 플러그인 문제는 아니었다. (스크립트: scratchpad `which_dock.py`)
- [x] **S1 재시작 결과**: timekit `wN:pQ`, simple-git `wN:pS`, ai-feedbag `wN:pR`, radio `wN:pA` 로 겹치지 않았다. 표시 파일과 레지스트리도 일치했다.
- [x] **`wN:pP` 출처**: 소개 칸(`herdr-dock-intro`)이다. 도크 블록이 3개 이상이면 빈 칸에 뜨는 것이 정상이라 문제가 아니다.
- [x] **S2 (grid 없음)**: grid 를 해제하고 재시작했다. timekit, simple-git, ai-feedbag 이 모두 복사본을 불러왔다. timekit `wN:pV`, simple-git `wN:pT`, ai-feedbag `wN:pW` 로 겹치지 않았고 표시 파일과 레지스트리도 일치했다.
- [x] **S3 (나중에 설치)**: 플러그인이 떠 있는 상태에서 grid 를 링크했다. 링크만으로는 떠 있는 블록이 바뀌지 않았다(timekit `wN:pV` 유지). simple-git(`wN:pX`)과 ai-feedbag(`wN:pY`)을 재시작하자 새로 원본을 불러왔고, 옛 복사본을 쓰는 timekit 과 겹치지 않았다. 표시 파일과 레지스트리도 일치했다.
- [x] **talk 블록 실제 기동**: `wN:pZ` 에 "talk: 접속 0명" 으로 떴다. 표시 파일(`herdr-talk.dock`)과 레지스트리가 `wN:pZ` 로 일치하고, 액션 로그는 `succeeded`(exit 0)다.

## 발생한 문제 (기록)

- [x] **테스트 스크립트가 라이브 상태 폴더를 덮어씀**: 이름 확인용 smoke 실행이 실제 herdr 플러그인 폴더에 가짜 pane id(`p1`, `p2`)와 워크스페이스(`w1`)를 썼다. 에이전트 이름(timekit, git, feedbag)으로 대응시켜 표시 파일을 복구하고 `reconcile_dock_state()`로 레지스트리를 맞췄다. 같은 실수를 막으려면 확인용 스크립트는 실제 폴더를 쓰지 않도록 `HERDR_PLUGIN_STATE_DIR`을 임시 폴더로 바꿔서 실행한다.
- [x] **talk 블록 기동 실패(자리 부족)**: radio 옛 블록이 `grid-2x2` 의 4개 자리를 차지해 `no available slots` 로 실패했다. radio 정리 후 해결됐다.

- [x] **빈 `herdr-dock2` 가 닫히지 않음 (수정 완료, Copilot)**: `_close_empty_extra_workspaces` 가 워크스페이스의 모든 pane 을 `pick_pane` 으로 검사한다. 사이드바 pane(`label=Sidebar`, `tokens=herdr-sidebar-*`)은 라벨이 있어서 빈 자리로 인정되지 않으므로, 블록이 없어도 워크스페이스가 닫히지 않는다. 확인: `is_sidebar(pane)` 은 True 지만 `pick_pane([pane], ...)` 은 None 이다.
  - 수정 방향: 검사하기 전에 사이드바 pane 을 제외한다(`panes = [p for p in _panes_in([wid]) if not is_sidebar(p)]`). 남은 pane 이 모두 빈 자리이면(없으면 포함) 닫는다. `if panes and all(...)` 에서 `panes` 조건을 빼야 사이드바만 남은 경우도 닫힌다.
  - 테스트: 사이드바만 있는 워크스페이스가 닫히고, 블록이 하나라도 있으면 닫히지 않는 단위 테스트를 추가한다.
  - 확인: 라이브 `reset` 후 `herdr-dock2` 없음, `herdr-dock` 4개 블록 유지, 레지스트리 일치. 확인 시점에는 이미 닫혀 있어서 닫히는 순간 자체는 다시 재현하지 않았다.

## 추가 개선 (진행)

- [x] **플러그인 복사본을 0.7.0 원본에 맞춤**: timekit, simple-git, talk, radio, ai-feedbag, stockpulse 의 `src/dock_layout.py`, `src/herdr_api.py` 를 grid 원본과 같게 맞췄다. 원본(herdr-dock-grid)은 수정하지 않았다(Copilot 담당). 각 플러그인 단위 테스트 통과.
  - 버전: timekit, simple-git 0.5.4 / talk, radio, ai-feedbag, stockpulse 0.5.3 (커밋 안 됨)
  - [ ] 라이브 재시작으로 복사본 경로 확인(설치본 없을 때)
- [x] **stockpulse 대시보드 종료 시 정리 (결정: (a) 확정)**: Claude 가 `dock-host` 로 감싸고 `finally` 에서 `release_dock_pane` 을 호출하도록 구현했다(0.5.4). pane 을 강제로 닫으면 `finally` 가 실행되지 않으므로, `reset` 을 기다리지 않고 다음 `ensure_dock_pane` 호출 때 정리한다. 이벤트 훅(b)은 하지 않는다.
  - 처음 확인: 강제 닫기 후 레지스트리와 표시 파일이 남았다(`wQ:p1`).
  - 다음 `ensure` 확인 1: 레지스트리 항목은 `_reconcile_registry` 가 지웠지만 **표시 파일(`herdr-stockpulse.dock`)은 남았다**. 레지스트리만 정리하고 표시 파일은 정리하지 않던 공용 모듈 문제였다.
  - 수정(grid 0.7.1): `_remove_dead_markers` 를 추가했다. `ensure_dock_pane` 과 `reconcile_dock_state` 에서 pane 이 없는 표시 파일을 지운다. 단, 10초 안에 만들어진 표시 파일은 두어서, 옛 복사본이 pane 을 막 나눈 직후의 경쟁을 피한다. dock 워크스페이스에 pane 이 하나도 없으면 아무것도 지우지 않는다. 단위 테스트 1개 추가(19개 통과).
  - 다음 `ensure` 확인 2: `herdr-talk` 으로 `ensure_dock_pane` 을 직접 호출한 뒤 `herdr-stockpulse.dock` 이 사라졌다(`wR:p1` 강제 닫기 상태에서 시작). 레지스트리도 4개(`ai-feedbag`, `simple-git`, `talk`, `timekit`)만 남았다.
  - 주의: `herdr plugin action invoke dock-start-windows --plugin herdr-talk` 는 talk 가 이미 떠 있으면 `ensure_dock_pane` 을 호출하지 않는 것으로 보인다(액션 실행 후에도 표시 파일이 남았다). 새 키 배정이나 시작 때만 정리가 일어난다.
  - 정리: 확인 후 `reset` 으로 빈 `herdr-dock2` 를 닫았다. `herdr-dock` 의 기존 4개 블록은 그대로다.
- [ ] **죽은 코드 정리**: radio 의 `pick_pane`, `find_workspace` 는 테스트에서만 쓰인다. 테스트를 새 방식으로 바꾼 뒤 지운다.
  - [x] ai-feedbag (결정: 삭제): `find_workspace`(legacy rename)를 지웠다. ai-feedbag 0.5.6 에서 함수, `LEGACY_WS_LABEL`, 관련 테스트를 삭제했다.
- [x] **talk 10분 자동 종료 정책**: 위 결정 항목(유지)과 같다.
- [x] **문서 최신화**: `handoff-copilot.md`, `migration-guide.md` 를 다중 워크스페이스 기준으로 보완했다(Copilot).

## 설계 확인

- [ ] **herdr 액션 실행 결과 불일치**: 자리 부족 때 talk 의 `dock-start-windows` 는 herdr 로그에 `succeeded`(exit 0)로 남았지만 직접 실행은 exit 1 이었다. 자리가 생긴 뒤에는 로그와 결과가 일치했다. 자리 부족 상황에서 로그가 성공으로 남는 원인은 아직 확인하지 않았다.
- [ ] **시작 순서 가정**: herdr 가 플러그인 startup 을 어떤 순서로 실행하는지 보장하지 않는다는 가정이 맞는지 확인한다. 설계는 순서와 상관없도록 만들어져 있다(`docs/design-install-order.md`).
- [ ] **옛 복사본 버전 불일치**: 옛 복사본이 새 원본과 다른 버전을 만났을 때 경고할지, 자리를 양보할지 정한다.

## 참고

- 설계 원칙: `docs/design-install-order.md`
- 이전 가이드: `docs/migration-guide.md`
- 인수인계 상태: `docs/handoff-copilot.md`

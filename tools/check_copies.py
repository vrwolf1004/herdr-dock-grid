"""원본 공용 모듈과 플러그인 저장소의 복사본이 바이트 단위로 같은지 확인한다.

사용: python tools/check_copies.py [--origin 원본 폴더] [--root 상위 폴더]
  --root 아래의 일곱 저장소에서 SHARED_FILES 를 찾아 원본과 비교한다 (기본: 이 저장소의 부모 폴더).
  모두 같으면 종료 코드 0, 다르거나 없는 파일이 하나라도 있으면 1.
"""

import argparse
import sys
from pathlib import Path

ORIGIN = Path(__file__).resolve().parents[1]
COPY_REPOS = [
    "herdr-simple-git", "herdr-tetris", "herdr-timekit", "herdr-talk",
    "herdr-radio", "herdr-ai-feedbag", "herdr-stockpulse",
]
SHARED_FILES = ["src/dock_layout.py", "src/herdr_api.py"]
SAME, DIFFERENT, MISSING = "같음", "다름", "없음"


def compare(origin, parent, repos=COPY_REPOS, files=SHARED_FILES):
    """(저장소, 파일, 상태) 목록. 상태는 SAME, DIFFERENT, MISSING 중 하나."""
    rows = []
    for repo in repos:
        for name in files:
            copy = parent / repo / name
            if not copy.is_file():
                status = MISSING
            elif copy.read_bytes() == (origin / name).read_bytes():
                status = SAME
            else:
                status = DIFFERENT
            rows.append((repo, name, status))
    return rows


def format_table(rows):
    lines = [f"{'저장소':<20} {'파일':<20} 상태"]
    lines += [f"{repo:<20} {name:<20} {status}" for repo, name, status in rows]
    return "\n".join(lines)


def main(argv=None, origin=ORIGIN):
    parser = argparse.ArgumentParser(description="공용 모듈 복사본이 원본과 같은지 확인한다.")
    parser.add_argument("--origin", type=Path, default=origin, help="원본 저장소 폴더")
    parser.add_argument("--root", type=Path, default=None, help="복사본 저장소들이 있는 상위 폴더 (기본: 원본의 부모)")
    args = parser.parse_args(argv)
    parent = args.root if args.root is not None else args.origin.parent
    rows = compare(args.origin, parent)
    print(format_table(rows))
    return 0 if all(status == SAME for _, _, status in rows) else 1


if __name__ == "__main__":
    sys.exit(main())

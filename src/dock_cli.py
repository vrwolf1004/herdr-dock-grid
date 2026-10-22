"""Dock management commands: python dock_cli.py <list|status|reconcile|reset|snapshot|policy>."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dock_layout
import herdr_api

COMMANDS = ("list", "status", "reconcile", "reset", "snapshot", "policy")


def run(command):
    if command in ("list", "status"):
        return dock_layout.list_docks()
    if command == "reconcile":
        return dock_layout.reconcile_dock_state()
    if command == "reset":
        return {"removed": dock_layout.reset_dock_state()}
    if command == "snapshot":
        return dock_layout.save_layout_snapshot()
    return {"layout_policy": dock_layout.get_layout_policy()}


def main(argv):
    if len(argv) != 2 or argv[1] not in COMMANDS:
        print(f"usage: dock_cli.py <{'|'.join(COMMANDS)}>", file=sys.stderr)
        return 2
    try:
        print(json.dumps(run(argv[1]), ensure_ascii=False, indent=2))
    except (herdr_api.HerdrError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

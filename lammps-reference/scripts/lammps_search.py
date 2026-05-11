#!/usr/bin/env python3
"""Search local LAMMPS manual, doc source, and tutorial references."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_DIR / "references"
MANUAL_TEXT = REFERENCES / "lammps-manual-22Jul2025.txt"
LAMMPS_DOC = Path("/home/rs4223/Downloads/lammps-22Jul2025/doc")
LAMMPS_DOC_SRC = LAMMPS_DOC / "src"
LAMMPS_DOC_UTILS = LAMMPS_DOC / "utils"
TUTORIAL_REPO = REFERENCES / "lammpstutorials.github.io"
TUTORIAL_SOURCE = TUTORIAL_REPO / "docs" / "sphinx" / "source"
TUTORIAL_INPUTS = TUTORIAL_REPO / ".dependencies" / "lammpstutorials-inputs"


TARGETS = {
    "all": [LAMMPS_DOC_SRC, MANUAL_TEXT, TUTORIAL_SOURCE, TUTORIAL_INPUTS],
    "manual": [MANUAL_TEXT],
    "doc-src": [LAMMPS_DOC_SRC],
    "doc-utils": [LAMMPS_DOC_UTILS],
    "lammps-doc": [LAMMPS_DOC_SRC, LAMMPS_DOC_UTILS],
    "tutorials": [TUTORIAL_SOURCE, TUTORIAL_INPUTS],
    "tutorial-text": [TUTORIAL_SOURCE],
    "inputs": [TUTORIAL_INPUTS],
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search the LAMMPS 22Jul2025 manual text, doc/src, and tutorial sources."
    )
    parser.add_argument("query", help="Regex or literal text to search for")
    parser.add_argument(
        "--where",
        choices=sorted(TARGETS),
        default="all",
        help="Reference subset to search",
    )
    parser.add_argument(
        "-C",
        "--context",
        type=int,
        default=3,
        help="Context lines before and after each match",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Search case-insensitively",
    )
    parser.add_argument(
        "-F",
        "--fixed-strings",
        action="store_true",
        help="Treat query as a literal string instead of a regex",
    )
    parser.add_argument(
        "--max-count",
        type=int,
        default=40,
        help="Stop after this many matches per file",
    )
    args = parser.parse_args()

    paths = [path for path in TARGETS[args.where] if path.exists()]
    if not paths:
        print(f"No searchable paths exist for --where={args.where}", file=sys.stderr)
        return 2

    cmd = [
        "rg",
        "--line-number",
        "--with-filename",
        f"--context={args.context}",
        f"--max-count={args.max_count}",
    ]
    if args.ignore_case:
        cmd.append("--ignore-case")
    if args.fixed_strings:
        cmd.append("--fixed-strings")
    cmd.append(args.query)
    cmd.extend(str(path) for path in paths)

    env = os.environ.copy()
    env["LC_ALL"] = env.get("LC_ALL", "C.UTF-8")
    completed = subprocess.run(cmd, env=env)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

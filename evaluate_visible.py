#!/usr/bin/env python3
"""Evaluate routes and regex assertions supplied with the visible challenge cases."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 evaluate_visible.py <cases.jsonl> <answers.jsonl>", file=sys.stderr)
        return 2
    cases = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line]
    answers = {row["id"]: row for row in (json.loads(line) for line in Path(sys.argv[2]).read_text().splitlines() if line)}
    failures = 0
    for case in cases:
        answer = answers.get(case["id"], {})
        checks = [answer.get("route") == case["expected_route"]]
        text = answer.get("answer", "")
        checks += [bool(re.search(pattern, text, re.I)) for pattern in case["must_include"]]
        checks += [not bool(re.search(pattern, text, re.I)) for pattern in case["must_not_include"]]
        status = "PASS" if all(checks) else "FAIL"
        failures += status == "FAIL"
        print(f"{status} {case['id']}: route={answer.get('route', 'missing')}")
    print(f"{len(cases) - failures}/{len(cases)} cases passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

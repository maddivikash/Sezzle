#!/usr/bin/env python3
"""Required challenge contract: python3 run_cases.py INPUT.jsonl OUTPUT.jsonl"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agent import SupportAgent


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 run_cases.py <cases.jsonl> <answers.jsonl>", file=sys.stderr)
        return 2
    input_path, output_path = map(Path, sys.argv[1:])
    agent = SupportAgent()
    # Publish results only after every case completes. This prevents a follow-up
    # evaluation from silently grading a partial file after an API failure.
    temporary_output = output_path.with_name(f".{output_path.name}.tmp")
    with input_path.open() as source, temporary_output.open("w") as destination:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            case = json.loads(line)
            if not all(key in case for key in ("id", "question", "user_id")):
                raise ValueError(f"Input line {line_number} lacks id, question, or user_id")
            result = agent.answer(case["question"], case["user_id"])
            destination.write(json.dumps({"id": case["id"], **result}) + "\n")
    temporary_output.replace(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

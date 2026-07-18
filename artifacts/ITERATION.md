# Iteration evidence

This file is intentionally incomplete until Gemini is run with a locally configured API key.

Run the baseline, inspect each answer, make one evidence-driven change, then preserve both answer files:

```bash
python3 run_cases.py cases/golden_visible.jsonl artifacts/first_answers.jsonl
python3 evaluate_visible.py cases/golden_visible.jsonl artifacts/first_answers.jsonl
# make one documented improvement
python3 run_cases.py cases/golden_visible.jsonl artifacts/final_answers.jsonl
python3 evaluate_visible.py cases/golden_visible.jsonl artifacts/final_answers.jsonl
```

Replace this note with: baseline score; failures grouped by failure taxonomy; exact change; final score; and remaining failures. Do not claim a run that did not happen.

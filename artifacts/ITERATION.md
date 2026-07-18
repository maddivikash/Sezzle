# Iteration evidence

## Baseline — 10/10 visible cases passed

The first full Gemini run is preserved in `first_answers.jsonl`. Regex assertions and
routes all passed. During qualitative review, however, I identified a privacy-minimization
gap: sensitive requests that were already guaranteed to escalate could still trigger an
otherwise authorized order lookup, placing unnecessary account context in the LLM prompt.

## Change

For forced-escalation requests (fraud, hardship, dispute filing, credit-report corrections,
and precise-limit/override requests), the application now skips the order lookup entirely.
The LLM still receives relevant policy excerpts and writes the explanation, but has no
personalized order context to inspect. I also bounded 429 retry waits for serverless use.

## Final — 10/10 visible cases passed

`final_answers.jsonl` records the post-change run; all route and content assertions passed.
The visible set exposed no remaining failures. Next I would add adversarial hidden-style
tests for prompt injection and cross-account order IDs, plus retrieval-recall telemetry.

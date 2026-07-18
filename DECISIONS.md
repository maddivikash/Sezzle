# Decision records

## 1. One bounded generation with local retrieval
**Decision:** retrieve up to three policy documents and make one small-model generation call.
**Options:** agentic multi-tool loop; vector database/RAG; pass all 12 policies; lexical retrieval.
**Why:** this corpus is tiny and versioned; lexical retrieval is inspectable and adds no service or embedding cost.
**Production trade:** cache repeated FAQ answers/retrieval and use a small model; reserve a stronger model for sampled audits.
**What changes my mind:** measured missed-policy recall or a substantially larger, frequently revised corpus.

## 2. Authorization before the model
**Decision:** the mock order lookup filters by authenticated `user_id` before merchant matching or serialization.
**Options:** expose an order-ID tool to the model; authorize after retrieval; pre-authorize in application code.
**Why:** a prompt cannot turn an unauthorized order into model context, including through guessed IDs or injection.
**Trade:** less flexible than a broad search tool, but customer-data disclosure is a non-negotiable failure mode.
**What changes my mind:** a production identity/entitlements service could safely provide a more expressive scoped query API.

## 3. Guardrail escalation plus LLM explanation
**Decision:** force the route to `escalate` for fraud, hardship, dispute filing, credit corrections, and exact-limit/override requests.
**Options:** rely on system instructions; deterministic canned answers; deterministic route guardrail with LLM-written response.
**Why:** policy asks for human action; the model still provides an empathetic, grounded explanation but cannot downgrade risk.
**Production trade:** this reduces automation rate, but protects high-impact decisions and supports a ≤3s, ~$50/day tiered design.
**What changes my mind:** audited false-positive/negative rates plus human-resolution data for each sensitive intent.

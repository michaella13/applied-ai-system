# Portfolio Artifacts — Music Recommender RAG Edition

## GitHub

[Repository link](YOUR_GITHUB_LINK_HERE)

---

## Demo Video (Loom)

[Watch the full walkthrough](YOUR_LOOM_LINK_HERE)

The video demonstrates:
- End-to-end system run with three different queries (high-energy, vague, low-energy)
- RAG pipeline behavior: parse → retrieve → generate
- Confidence guardrail triggering on an ambiguous query
- Live log output showing every pipeline stage
- Test suite results: 12/13 passing unit tests

---

## Reflection — What This Project Says About Me as an AI Engineer

This project showed me that building with AI is as much about knowing where not to use it as knowing where to apply it. I kept the scoring engine as plain, testable Python — because correctness and consistency need to be verifiable — and used Gemini only where language flexibility was genuinely needed: interpreting the user's intent and explaining the results in a way that feels natural. The two-call RAG design came from a real engineering decision: separating parse from generate created a logged checkpoint that made debugging fast and honest. The confidence guardrail came from watching the system handle vague queries and realizing that telling users when you're uncertain is more responsible than confidently returning a bad result. I'm an AI engineer who treats the model as one component in a system — not the whole system — and who measures reliability with real test runs, not optimism.

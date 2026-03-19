# Why Evaluation Matters

Modern AI systems fail in ways that ordinary unit tests do not capture. A model can answer one prompt correctly and still be unreliable across edge cases, adversarial inputs, or structured-output constraints. Evaluation matters because it turns vague quality claims into repeatable evidence.

In practice, teams need to answer questions like:

- Does a prompt change improve average behavior or just one demo?
- Does a new model version regress on tool calling or JSON formatting?
- Does retrieval keep answers grounded in the provided context?
- Does a judge or rubric reward the behavior we actually want?

This starter repository begins with deterministic local evaluation because it is the fastest way to build trust in the mechanics. If the harness cannot reliably pass a small frozen suite with no network calls, it is not ready to judge more expensive live systems.

The goal is not to pretend deterministic fixtures are enough forever. The goal is to establish a clean baseline:

1. Stable schemas
2. Interpretable scoring rules
3. Reproducible reports
4. CI feedback contributors can trust

Once that baseline exists, more realistic online or stochastic evaluations can be layered on top without losing the safety of a local first line of defense.


# AI DevOps Agent Project

> A modular toolkit for building AI-powered DevOps agents that analyze logs, diagnose failures, and recommend fixes using ReAct-style workflows.

## What this project does

This repository provides reusable modules for intelligent DevOps troubleshooting flows, including:

- Parsing and structuring CI/CD logs (including Jenkins logs)
- Finding similar historical failures using embeddings
- Generating fix-oriented prompts from traces and errors
- Running ReAct agents with planning and tool-calling capabilities
- Supporting utilities such as token counting and attention analysis

In short: this is a practical foundation for agents that transform raw failures into actionable remediation steps.

---

## Project structure

```text
ai_devops_agent_project/
├── modules/
│   ├── attention_map/
│   ├── fixprompt_gen_with_traceinsight/
│   ├── jenkins_log_eror_parser/
│   ├── log_drop_server/
│   ├── log_embeddings_similarity/
│   ├── log_fixflow_react_agent/
│   ├── react_agent_with_questions_template/
│   ├── token_counter/
│   └── ReAct_Agent_with_Planning_and_Tools/
│       ├── version1/
│       └── version2/
└── prompts/
```

---

## Core modules

| Module | Primary role | When to use it |
|---|---|---|
| `jenkins_log_eror_parser` | Extracts and structures Jenkins log errors | When you need automated failure signal extraction |
| `log_embeddings_similarity` | Computes similarity between log incidents | When you want to retrieve related past failures |
| `fixprompt_gen_with_traceinsight` | Builds fix-generation prompts from traces/logs | When preparing high-quality LLM repair prompts |
| `log_fixflow_react_agent` | ReAct-style flow for troubleshooting | When you need guided, step-by-step reasoning |
| `react_agent_with_questions_template` | Agent template with clarification questions | When missing context must be collected first |
| `token_counter` | Counts prompt/output tokens | When controlling model limits and cost |
| `attention_map` | Attention visualization and analysis | For debugging and explainability experiments |
| `ReAct_Agent_with_Planning_and_Tools/version2` | Advanced tool-calling pipeline + Docker setup | For operational usage and end-to-end testing |

---

## `prompts/` directory

The `prompts/` folder contains reusable prompt templates for:

- Diagnostic and fix-generation tasks
- Output validation and security-focused constraints
- Chat and tool-calling interaction patterns
- Structured output generation

Start from an existing template whenever possible, then adapt to your domain.

---

## Quick start

### 1) Prerequisites

- Python 3.10+
- `pip`
- (Optional) Docker for running the `version2` agent stack

### 2) Setup environment and dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r modules/ReAct_Agent_with_Planning_and_Tools/version2/requirements.txt
```

### 3) Run the Version 2 agent pipeline

```bash
python modules/ReAct_Agent_with_Planning_and_Tools/version2/run_tool_calling_react_agent_pipeline.py
```

### 4) Run the Flask test script (if relevant in your environment)

```bash
python modules/ReAct_Agent_with_Planning_and_Tools/version2/test_flask_agent.py
```

---

## Recommended troubleshooting pipeline

1. **Input:** Collect failure logs from CI/CD systems.
2. **Parsing:** Extract high-signal errors (for example with `jenkins_log_eror_parser`).
3. **Similarity:** Find related incidents via `log_embeddings_similarity`.
4. **Prompting:** Generate a fix-focused prompt (`fixprompt_gen_with_traceinsight`).
5. **Reasoning:** Execute ReAct planning/tool-calling flow.
6. **Output:** Return likely root cause, remediation plan, and validation steps.

---

## Recommended engineering practices

- **Keep it modular:** each capability should remain isolated in its module.
- **Treat prompts as code:** maintain prompts in versioned files under `prompts/`.
- **Prefer transparent reasoning:** ReAct traces make recommendations easier to audit.
- **Validate before automation:** gate outputs before production actions.

---

## Production hardening checklist

- Add observability (logs, metrics, traces) around every pipeline stage.
- Persist incidents + outcomes to improve similarity quality over time.
- Add guardrails for risky tool execution paths.
- A/B test prompt variants and measure downstream remediation quality.

---

## Contributing

When adding a new module:

1. Create a dedicated folder under `modules/`.
2. Add `logic.py`, `__init__.py`, and a local `README.md`.
3. Document input/output contracts and sample usage.
4. Keep naming and structure consistent with existing modules.

---

## License

No license is currently defined. Add a `LICENSE` file that matches your organization’s policy.

---

## TL;DR

If you want an AI DevOps foundation that turns logs into explainable, actionable fix guidance, this repository is a strong starting point.

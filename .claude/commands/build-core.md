---
description: Build the small shared foundation for the Engineering Track - Postgres schema and DB roles, the instructor class setup notebook (data/00_lab_setup.ipynb, shared.json) and the validator. No package for learners
---

Build the course core: $ARGUMENTS

(Optional argument: one piece to (re)build: `schema`, `lab-setup`, `validator`. With no
argument, check the status of all three.)

## GUARD

```bash
ls plans/DECISIONS.md plans/lab_environment.md plans/NOTEBOOK_STYLE.md 2>/dev/null
```

Missing any: "Run `/init-course` first."

---

## Why this is small (v3 scope, `plans/core_plan.md` section 00)

Learner notebooks import frameworks only (boto3, langgraph, langchain_aws,
langgraph_checkpoint_aws, mcp 1.30.0, gradio, psycopg, httpx, bedrock_agentcore). Every AWS
call, SQL query, deploy, Gateway, Cognito, Cedar, Memory, Guardrail, trace and Gradio step is
a visible cell; helpers are visible HELPER cells; deployed files use `%%writefile`. No hidden
package, no toolkit zip, no mock mode. `course/harborview/` is source material that
`/research-module` copies into cells (contract names, SQL, ui launch pattern), never imported.

So the core is only what lives outside the module notebooks.

## The three pieces

| # | Piece | Path | Status |
|---|---|---|---|
| 1 | Schema, seed, reader/writer roles (`SET ROLE harborview_reader` / `harborview_writer`) | `data/schema.sql`, `data/setup_lab.py --db`, `data/check_db_roles.py` | done |
| 2 | Instructor class setup, run once by Axel in his instructor Studio space: shared Memory + demo actor, Cognito pool (reader/writer clients), code bucket, prebuilt arm64 deps zip, Transaction Search check, smoke deploy, `shared.json` to `s3://<class bucket>/course/shared.json` | `data/00_lab_setup.ipynb` | done |
| 3 | Static validator: pinned `%pip` first cell, CONFIG cell, no harborview import, banners, labs, `--pair`, inline mermaid, regions, mcp 1.x, infra, AI tells | `validate_notebooks.py`, `tests/test_validator.py` | done |

`course/module_00/start_here.ipynb` is NOT core: `/build-module 0` builds it like any module.

## Rebuilding a piece

1. Read DECISIONS, `plans/lab_environment.md` and `plans/core_plan.md` section 00
2. Plan the change in chat and **wait for approval**
3. Build it. Verify:
   - schema: through the SSM tunnel with `AWS_PROFILE=datacouch`, then `data/check_db_roles.py`
   - lab setup: Axel runs `data/00_lab_setup.ipynb` in his instructor space (the laptop
     identity cannot create Cognito, Guardrails or AgentCore resources) and reports the summary
   - validator: `.venv/bin/python3 -m pytest tests/test_validator.py` and
     `.venv/bin/python3 validate_notebooks.py --code`
4. Record results in `plans/lab_environment.md`

## Handoff

> Core done. Next: `/research-module 0` (start_here) or `/research-module 1`.

---
name: agentic-engineering
description: Course vocabulary, the Harborview Life running case, the module arc and lab design rules for the Agentic AI Engineering Track (engineers code in SageMaker notebooks; LangGraph, Bedrock Haiku 4.5, AgentCore Runtime/Gateway/Identity/Memory, MCP, Bedrock KB, Guardrails, Gradio). Use when planning, writing or reviewing any notebook cell, lab, diagram or plan in this repo.
---

# Agentic AI Engineering Track: how to teach it here

Read with: `plans/DECISIONS.md` (what we build, wins on conflict),
`plans/TEACHING_STYLE.md` (voice and flavor; the concierge workshop is ideas only),
`plans/NOTEBOOK_STYLE.md` (cell anatomy and the demo and lab structure, copied exactly from
bread-financial weeks 16 to 19), `plans/CONTENT_SOURCES.md` (reusable ideas from bread weeks
15 to 19). Scope: `imp_files/outline_engineering.md`. Every API is verified by running it,
never from memory.

## Audience

Software engineers, AI and ML engineers, solution architects. Solid Python, pytest,
some LangGraph. They will build and operate agents in production. Success = they leave
having built, deployed, permissioned, grounded, evaluated and traced one agent system,
and can explain every box in it.

## Module arc (every concept inside every module, bread-financial anatomy)

| Step | Cell | Rule |
|---|---|---|
| 1 | `# Section N` markdown | The concept, with its inline mermaid diagram |
| 2 | `# DEMO:` problem | A runnable cell shows what breaks. Designed failures are measured and seeded so they happen on cue |
| 3 | `# DEMO:` solution | Code revealed bottom up, each layer named. Plumbing in visible `# HELPER` cells where first needed, the idea on screen |
| 4 | `> **Think About It**:` | A production question (cost, risk, scale, security) |
| 5 | `## Lab N: <Title> (15 minutes)` + one `# LAB N` cell | Done in class. Learners write the decision code (`name = None  # YOUR CODE`), the cell prints the result to compare with Expected Output; labs that produce an agent end by launching it in Gradio. A `# FALLBACK` cell follows only when a later section needs the result |

No CHECK cells, no mini exercises. Concierge ideas (failure first, named closers, the honest
part) are flavor, not structure. Each fix uncovers the next problem. That chain is the day.

## The running case (all day)

**Harborview Life** Policyholder Service Desk, a fictional insurer. One agent that grows:
hand loop (1), LangGraph graph (2), deployed on Runtime (3), tools via Gateway (4), grounded
in the KB (5), remembers (6), split under a supervisor with approval (7), evaluated, guarded
and traced (8).

| Request type | Modules | Why it teaches |
|---|---|---|
| Policy loan | 1, 2, 4, 7, 8 | tools, DMN rule, write tool under least privilege, approval above threshold, invented limit |
| Claim status | 2, 4 | routing to servicing, read-only tool |
| Beneficiary change | 2, 7 | BPMN gateway to escalation, always a human |
| Coverage question | 5, 8 | RAG, citations, refusal when the KB is silent |
| Returning policyholder | 6 | memory across sessions |
| Out of scope or sensitive data | 5, 8 | refusal, Bedrock Guardrails |

All data is synthetic. Seeded cases live in Postgres (`data/schema.sql`, `data/setup_lab.py`);
`course/harborview/` is source material for plans (contract names, SQL, ui launch pattern),
never imported by a notebook.

## What a notebook may use

- Frameworks only: boto3, langgraph, langchain_aws, langgraph_checkpoint_aws, mcp 1.30.0,
  gradio, psycopg, httpx, bedrock_agentcore. No hidden package, no toolkit zip
- Cell 1: pinned `%pip install`. Then a visible `# CONFIG` cell: `MODEL_REGION = "us-east-1"`,
  `AGENTCORE_REGION = "us-west-2"`, `MODEL_ID`, `STUDENT_NAME = "default"` refused by a
  visible check (id `{name}_{6 digits}` saved in `~/harborview_learner.json`), and `shared.json`
  from the class bucket for shared ids. Every notebook repeats it
- Every AWS call, SQL query (`SET ROLE harborview_reader` or `harborview_writer`), deploy
  (deps zip + `%%writefile main.py` + `create_agent_runtime`), Gateway, Cognito token, Cedar,
  Memory, Guardrail, trace lookup and Gradio launch is a visible cell. Small helpers are
  defined in a `# HELPER` cell where first needed (concierge style)

## How the pieces map to concepts

| Piece | Concept |
|---|---|
| Bedrock Converse (Haiku 4.5, us-east-1) | The model answers; it never runs a tool |
| Hand-written loop | An agent is a loop: ask, run the tool, hand back, repeat, with a ceiling |
| LangGraph StateGraph | The same loop with the plumbing written; state, nodes, conditional edges |
| Intake node + routing function | BPMN gateway and DMN decision table as code |
| Loan rules table (a visible cell) | DMN table the agent follows instead of guessing |
| AgentCore Runtime | The graph as a managed endpoint with isolated sessions |
| MCP server + AgentCore Gateway | Same tools, new transport; one front door with auth |
| AgentCore Identity | Least privilege: who may call which tool |
| Bedrock KB (S3 Vectors) | Grounded, cited answers; refusal when nothing is retrieved |
| LangGraph checkpointer + AgentCore Memory | Short-term state, long-term facts |
| Supervisor + `interrupt` | Specialists by capability; a human checkpoint on high-risk actions |
| Eval set + Bedrock Guardrails + traces | Measure, block, diagnose |

## Vocabulary (gloss once, never vary)

| Term | Definition used in the course |
|---|---|
| Agent | A model in a loop that calls tools and decides when it is done |
| Tool | A function the agent may ask us to run, described by a schema |
| State | The typed dict the graph passes between nodes |
| Node / edge / conditional edge | A step / a fixed next step / a next step chosen by a function |
| Checkpointer | Saves state per thread so a run can pause and resume |
| Runtime | AgentCore's managed host for the agent |
| Gateway | AgentCore's MCP front door for tools |
| Identity | AgentCore's inbound and outbound auth for agents and tools |
| Interrupt | A pause in the graph that waits for a human value |
| Guardrail | A Bedrock policy that blocks or masks input or output |
| Trace | The step-by-step record of a run (spans) |
| Eval set | Fixed cases with expected outcomes, scored pass or fail |

## Lab design rules (engineers)

1. **Learners write the decisions, not the plumbing.** Slots are where a design decision
   lives: state fields, a routing rule, a tool body, an interrupt condition, a guardrail policy.
2. **Every lab shows its result.** The `# LAB N` cell prints what the learner compares with
   Expected Output. Where the outline says pytest (Module 2 routing), the tests are a step
   of the lab. No CHECK cells.
3. **Nothing blocks.** A `# FALLBACK` cell repeats the full working code inline, only when a
   later section uses the lab's result. Removed in solutions.ipynb.
4. **Talk to what you built.** Labs that produce an agent end with a step that launches it in
   Gradio on the Studio proxy, visible in the LAB cell: chat plus trace.
5. **One-day class.** Labs are done in class, `(15 minutes)` each. No mini exercises.
6. **Change, rerun, compare.** Keep variants alive (`_v2`) and print before and after.
7. **Per-learner resources** carry the participant id in their names. Never touch another
   learner's resources or shared seed rows.
8. **Live only.** No mock mode. Solutions are validated by running them live: modules 1, 2, 5
   from the laptop; modules 3+ by Axel in his instructor Studio space.
9. **Regulated register.** Auditability, least privilege, approval and refusal are features.

## Copy rules

US English, short declaratives, no AI tells (see CLAUDE.md). Harborview Life only; the
client name appears nowhere in learner material.

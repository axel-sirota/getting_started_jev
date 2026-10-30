---
name: agentic-foundations
description: Course vocabulary, the Harborview Life running case, the 5-beat module arc and lab design rules for the Agentic AI Foundations day for non-coders (SageMaker, Bedrock, LangGraph, Gradio). Use when planning, writing or reviewing any demo, lab, slide or diagram in this repo.
---

# Agentic AI Foundations: how to teach it here

Scope: `imp_files/outline_foundations.md`. Decisions: `plans/DECISIONS.md` (wins on
conflict). This file fixes vocabulary and teaching shape. It does not replace research:
every factual claim on a slide needs a source found with `/research`, and every API
needs to be verified by running it.

## Audience

Business professionals, product managers, operations and service leads, risk and
compliance partners at the client (Northwestern Mutual). They will specify, sponsor or
supervise agents. They do not code. Success = they leave understanding how an agent works
inside and how to use, test and govern one.

## The 5-beat arc (every module)

| Beat | Where | Rule |
|---|---|---|
| 1. Problem | Module notebook, Part A (Axel runs it on screen) | Real, visible failure a business person recognizes. Seed it so it happens on cue |
| 2. Theory | Slides | The concept that fixes it, diagram-first |
| 3. Fix | Same notebook, Part B (Axel runs it on screen) | Same request, now working; the change is on screen |
| 4. Lab | Same notebook, "Lab:" section at the bottom: Axel launches the Gradio app and shares its link in the chat | Learners change one thing, rerun, compare side by side |

ONE notebook per module (`moduleNN_<slug>.ipynb`): demo on top, Lab section at the bottom.
Never separate demo and lab notebooks.
| 5. Lesson | Slide | One takeaway sentence and who owns it in their org |

## The running case (all day)

**Harborview Life** Policyholder Service Agent, a fictional insurer's service desk.

| Request type | Modules | Why it teaches |
|---|---|---|
| Policy question ("is X covered?") | 1, 6 | RAG, citations, hallucination |
| Policy loan request | 2, 3, 4, 5, 8 | multi-step plan, decision table, auto-approval limit, approval on high value |
| Beneficiary change | 3 | always needs a human: identity, fraud risk |
| Ambiguous or out-of-scope request | 5, 8 | escalation language, guardrails |

One agent that gains a capability or a control per module, so learners see the same agent
change. All data is synthetic.

## How the pieces map to concepts

| Piece (in `course/harborview`) | Concept it makes visible |
|---|---|
| Bedrock Claude Haiku 4.5 (us-east-1) | The model: generates text, cannot act alone |
| LangGraph graph | The plan, act, evaluate loop as nodes and edges |
| Tools over Postgres (fixed queries) | Acting on enterprise systems; why the agent never writes its own SQL |
| AgentCore Memory checkpoints | Memory, and pausing for a human then resuming |
| Approval queue table | Human-in-the-loop as a real work item |
| Decision table (DMN) in `rules.py` | Rules the agent follows instead of guessing |
| Bedrock Knowledge Base (S3 Vectors) | RAG: grounded, cited answers |
| MCP server | One standard plug for tools across systems |
| Guardrails | Blocking or correcting outputs that break a rule |
| `traces` table | Observability: what the agent did, step by step, for the whole room |

## Vocabulary (define each the first time it appears)

| Term | Plain definition |
|---|---|
| Generative AI | A model that produces text from a prompt. It answers; it does not act |
| Agent | A model in a loop that plans, uses tools, checks results and acts toward a goal |
| Plan, act, evaluate loop | The agent decides a step, does it, checks the result, repeats |
| Tool | Something the agent can call: look up a policy, compute a loan value, open a case |
| Trace | The step-by-step record of what the agent thought, called, got back and decided |
| Memory | What the agent keeps between steps and conversations |
| Autonomy level | How much the agent may do without a person: suggest, act with approval, act and report, act alone |
| Human-in-the-loop | A required human checkpoint before the agent's action takes effect |
| BPMN | A standard way to draw a business process: tasks, decisions, lanes, hand-offs |
| DMN decision table | Rules as a table: inputs in columns, one outcome per row |
| Instructions | The agent's job description: role, constraints, output format, when to escalate |
| RAG | The agent looks up passages in approved documents and cites them |
| MCP | Model Context Protocol: a standard plug that lets agents use tools and data from many systems the same way |
| Guardrail | A check that blocks or corrects an output or action that breaks a rule |
| Hallucination | A confident answer not backed by the documents or data, like an invented loan limit |
| Evaluation | Running a fixed scenario pack and scoring each result pass or fail against success criteria |
| Observability | Measuring the agent in production: volume, escalation rate, failures, quality |
| Coding agent | The same loop applied to software work: plan a change, edit code, run tests, check |

## Lab design rules (non-coders)

1. **Learners never write code, upload or run anything.** Axel runs the Lab section's launch cell
   and pastes the public link and class password in the chat; learners open it and work in
   the Gradio app: forms, toggles, dropdowns, text boxes (instructions, guardrails) and
   editable tables (decision tables, scenario packs). The one exception is Module 4's
   starter Mermaid diagram: labels and arrows only.
2. **Change, rerun, compare.** Baseline, change one thing, rerun the same requests, show
   before and after side by side. The comparison is the lesson.
3. **Show the trace.** When the agent acts, show steps labelled reasoning, tool call, tool
   result, rule applied, response.
4. **Per-learner edits stay in the session.** Never write learner edits to shared tables.
   Their runs go to `traces` so Module 8 can show the room's day.
4a. **One app serves the whole room.** Every app starts with a "Your name" textbox with
   the instruction "Type your first name so your results show as yours". Every handler
   that writes or reads per-learner data (traces, approvals, ratings, evals, "Just me"
   views, checkpoint thread ids) is wired with `for_learner(handler)` and the name box as
   its first input. Room views count distinct names. Per-browser state stays in `gr.State`
5. **Designed failures happen on cue.** Seed or cache them; mock mode tells the same story.
6. **Nothing blocks.** Run all works with defaults; a learner who clicks nothing still sees
   every result.
7. **Plain-language instructions** before every action; "What did you notice?" after.
8. **Every module ends on the human role**: who approves, who owns the rule, who reads the
   dashboard.
9. **Regulated register.** Auditability, explainability, escalation and approval are
   features, not friction.
10. **No timings.** No lab timers, no "about N minutes", no "takes about 30 seconds"
    wait messages; say "Working..." or "This can take a little while the first time".

## Copy rules

US English, short declarative sentences, no AI tells (see CLAUDE.md). No hype: say what
the agent did and what it cannot do. Harborview Life only; the client name appears only on
the title slide.

No timings in any content: no slot or beat minutes, no Minutes columns, no 'takes about N minutes/seconds', no lab timers. Axel paces live. Policy facts (grace periods, business days) are not timings. The validators fail on duration patterns.

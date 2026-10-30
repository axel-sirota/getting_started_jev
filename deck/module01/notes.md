# Module 1 speaker notes: Meet Jev: Typed Decisions Instead of Text

## Slide 1 · Getting Started with Jev

Over four hours we build one thing: a triage layer that reads a message and decides where it goes. Module 1 starts with the question every team asks first: why not just use an LLM?

Playbook: Before slide 1: open the module 1 exercises notebook in Colab; keys ready to paste.

## Slide 2 · The reply that breaks your parser

This is how most LLM triage starts: a prompt that lists the teams and a parser that hopes. I left the format line out on purpose: with it the same model gave 40 of 40 clean names in our run, and the next slide turns that hope into a guarantee.

## Slide 3 · A schema fixes the format, not the doubt

Give the LLM the fix every OpenAI user knows: a JSON schema whose enum is the 10 teams. The format problem is gone, but there is still no number your code can act on.

## Slide 4 · Jev answers questions. It never writes text.

Jev is TypeSafe's first System One model: it answers judgment questions and never writes text. Write down your prediction, then open the notebook, run the four Setup cells, and go to Demo 1.

Playbook, Demo 1: Everyone runs "Section 0: Setup" (install, keys, config, data), then "Demo 1". The "40 messages, three ways, one table" cell makes 120 calls per person; if the shared keys slow down, run it once on the instructor screen and let the room watch the table.

## Slide 5 · Accuracy within noise, 3 to 4x faster, 12x cheaper

In our runs the schema LLM and Jev were within noise on accuracy, and in our first run 10 of Jev's 11 misses were labels a person could argue about. Jev was 3x to 4x faster across three runs, about 12x cheaper, and the only one with a probability per team.

## Slide 6 · One request, three kinds of question

A Choice picks one option, a Score rates on levels you describe, and a Noul says how likely a statement is true. Each question is answered on its own against the same state, all in one request.

Playbook, Demo 2: "Demo 2", its three DEMO cells. Point at the frustration probabilities: the score averages the levels, and confidence is 0.00 because the probability is spread.

## Slide 7 · Read the distribution, not only the top answer

Calm is the top level, but almost half the probability sits off it, 22% of it two levels away, so Score confidence floors at 0.00. Confidence measures spread, not correctness, and every response names the model that answered, so log it next to the decision.

## Slide 8 · Rules in Python, not in the prompt

Never ask Jev "should we escalate?"; ask what is true, and keep the rules in Python, checked in this order. 0.7 and 0.3 are TypeSafe's suggested starting thresholds for a Noul, and Module 3 checks them against data.

## Slide 9 · Lab 1: Build triage() in one call

Level 1 is two design decisions: how you describe urgency, and how you phrase risk. Level 2 is the function your product would ship.

Playbook, Lab 1: "Lab 1". Walk the room at Level 1; most questions are about how to word the levels. Anyone stuck runs the FALLBACK cell (it fills only the empty slot) and moves to Level 2. Backup if Jev rate-limits: pairs share one notebook.

## Slide 10 · Urgent is not risky: the declined card

The declined card never reaches the escalation rule: its risk is low, so the urgency rule decides. If you ran Level 3, one bundled call read 632 input tokens against 1,180 for three calls, and parallel calls matched its median speed.

Playbook: Slide 10: put the LAB 1.2 table on screen, then its sorted risk line, and ask where the room would put the cut-offs.

## Slide 11 · Jev always picks a team, even when none fits

A Choice always returns one of its options, even when none fits. The fix is a second question in the same request, a Noul that asks whether anything fits, and we build it in Module 3.

## Slide 12 · Jev judges, your code decides

If you remember one thing: Jev judges, your code decides, and your triage() is the pattern we reuse all course. Next, Module 2 splits our risk question, which joins three conditions with "or", so you know which risk fired.

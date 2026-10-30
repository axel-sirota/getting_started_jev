# Module 1: Meet Jev: Typed Decisions Instead of Text, Slide Diagrams

| Slide | Title | Layout | Mermaid type |
| --- | --- | --- | --- |
| 1 | Getting Started with Jev | title slide | none |
| 2 | The reply that breaks your parser | full diagram | flowchart |
| 3 | A schema fixes the format, not the doubt | points left, diagram right | flowchart |
| 4 | Jev answers questions. It never writes text. | points left, diagram right | flowchart |
| 5 | Accuracy within noise, 4x faster, 12x cheaper | full diagram | flowchart |
| 6 | One request, three kinds of question | full diagram | flowchart |
| 7 | Read the distribution, not only the top answer | full diagram | xychart-beta |
| 8 | Rules in Python, not in the prompt | full diagram | flowchart |
| 9 | Lab 1: Build triage() in one call | lab holding slide | flowchart |
| 10 | Urgent is not risky: the declined card | full diagram | flowchart |
| 11 | Jev always picks a team, even when none fits | full diagram | flowchart |
| 12 | Jev judges, your code decides | full diagram | flowchart |

### Slide 2 · The reply that breaks your parser

```mermaid
flowchart LR
  M["40 CLINC150 messages<br/>prompt with no format line"] --> L["LLM, plain prompt"]
  L -- "the rest" --> OK["credit_cards<br/>your code routes it"]
  L -- "13 to 18 of 40" --> BAD["**credit_cards** or a sentence<br/>parse error"]
  classDef bad fill:#FEE2E2,stroke:#B91C1C,color:#7F1D1D
  class BAD bad
```

### Slide 3 · A schema fixes the format, not the doubt

```mermaid
flowchart TD
  M["message"] --> S["LLM + JSON schema"]
  S --> T["team: credit_cards"]
  T --> Q["how sure?<br/>no answer"]
```

### Slide 4 · Jev answers questions. It never writes text.

```mermaid
flowchart TD
  ST["state: the message"] --> J["Jev"]
  Q["question: Choice of 10 teams"] --> J
  J --> A["choice + a probability per team"]
  A --> C["your code decides"]
```

### Slide 5 · Accuracy within noise, 4x faster, 12x cheaper

```mermaid
flowchart LR
  LT["<b>946 ms</b><br/>LLM + JSON schema"]:::llm ~~~ JT["<b>252 ms</b><br/>Jev"]:::jev ~~~ RT["3.8x faster"]:::ratio
  LC["<b>$0.256</b><br/>per 1,000, LLM + schema"]:::llm ~~~ JC["<b>$0.022</b><br/>per 1,000, Jev"]:::jev ~~~ RC["11.6x cheaper"]:::ratio
  classDef llm fill:#F3F4F6,stroke:#9CA3AF,color:#4B5563
  classDef jev fill:#40B8A6,stroke:#2F9987,color:#0F2938
  classDef ratio fill:#FFFFFF,stroke:#1A3D4D,stroke-width:4px,color:#1A3D4D
```

### Slide 6 · One request, three kinds of question

```mermaid
flowchart LR
  ST["state: the message"] --> J["Jev, one request"]
  QC["team: Choice<br/>pick one"] --> J
  QS["frustration: Score<br/>rate on levels"] --> J
  QN["travel_plans: Noul<br/>how likely is it true?"] --> J
  J --> AC["choice + probabilities"]
  J --> AS["score + probabilities"]
  J --> AN["noul: one probability, 0 to 1"]
```

### Slide 7 · Read the distribution, not only the top answer

```mermaid
xychart-beta
  title "frustration: score 0.70, confidence 0.00"
  x-axis ["0 calm", "1 annoyed", "2 angry"]
  y-axis "probability" 0 --> 1
  bar [0.51, 0.27, 0.22]
```

### Slide 8 · Rules in Python, not in the prompt

```mermaid
flowchart LR
  J["Jev judges<br/>urgency 0 to 2, risk 0 to 1"] --> R1{"risk >= 0.7"}
  R1 -- yes --> E["ESCALATE<br/>to a human"]
  R1 -- no --> R2{"risk > 0.3"}
  R2 -- yes --> V["REVIEW<br/>by a human"]
  R2 -- no --> R3{"urgency >= 1.5"}
  R3 -- yes --> P["PRIORITY<br/>to the team"]
  R3 -- no --> RT["ROUTE<br/>to the team"]
  classDef jev fill:#1A3D4D,stroke:#0F2938,color:#FFFFFF
  classDef esc fill:#B91C1C,stroke:#7F1D1D,color:#FFFFFF
  classDef rev fill:#FDE68A,stroke:#B45309,color:#111827
  classDef pri fill:#40B8A6,stroke:#2F9987,color:#111827
  classDef rt fill:#F9FAFB,stroke:#9CA3AF,color:#111827
  class J jev
  class E esc
  class V rev
  class P pri
  class RT rt
```

### Slide 9 · Lab 1: Build triage() in one call

```mermaid
flowchart LR
  L1["Level 1: Guided<br/>urgency levels, risk question"] --> L2["Level 2: Core<br/>triage(): one call + rules"]
  L2 --> D["Done<br/>every message has an action"]
  L2 -.-> L3["Level 3: Challenge, optional<br/>what does bundling buy?"]
  classDef done fill:#1A3D4D,stroke:#0F2938,color:#FFFFFF
  classDef opt fill:#F9FAFB,stroke:#9CA3AF,color:#4B5563,stroke-dasharray:6 4
  class D done
  class L3 opt
```

### Slide 10 · Urgent is not risky: the declined card

```mermaid
flowchart LR
  D["declined card<br/>urgent, low risk"] --> DR["risk 0.04<br/>below 0.3"] --> DU["urgency 1.8<br/>at least 1.5"] --> DA["PRIORITY<br/>not ESCALATE"]
  L["lost card<br/>high risk"] --> LK["risk 0.97<br/>at least 0.7"] --> LA["ESCALATE<br/>urgency not read"]
  classDef hero fill:#40B8A6,stroke:#2F9987,color:#0F2938,stroke-width:3px
  classDef esc fill:#B91C1C,stroke:#7F1D1D,color:#FFFFFF
  class D,DA hero
  class LA esc
```

### Slide 11 · Jev always picks a team, even when none fits

```mermaid
flowchart LR
  M["what movies are playing"] --> C["Choice: team"]
  C --> T["small_talk<br/>confidence below 0.5"]
  M -.-> N["Noul: does any team fit?<br/>not built yet, Module 3"]
  classDef future fill:#F3F4F6,stroke:#9CA3AF,color:#6B7280,stroke-dasharray:6 4
  class N future
```

### Slide 12 · Jev judges, your code decides

```mermaid
flowchart LR
  A["ask: what is true?"] --> J["Jev: judgments"] --> C["your code: decisions"]
  X["ask: what should we do?"] -- "never" --x J
  linkStyle 2 stroke:#B91C1C,stroke-width:3px,color:#B91C1C
```

# Module 1: Meet Jev: Typed Decisions Instead of Text, Slide Diagrams

| Slide | Title | Layout | Mermaid type |
| --- | --- | --- | --- |
| 1 | Getting Started with Jev | title slide | none |
| 2 | The reply that breaks your parser | points left, diagram right | flowchart |
| 3 | What a JSON schema cannot give you | points left, diagram right | flowchart |
| 4 | System One: judgments, not text | points left, diagram right | flowchart |
| 5 | Accuracy within noise, 4x faster, 12x cheaper | points left, diagram right | flowchart |
| 6 | One state, several questions | full diagram | flowchart |
| 7 | Read the distribution, not only the top answer | points left, diagram right | xychart-beta |
| 8 | Judgments in Jev, decisions in code | full diagram | flowchart |
| 9 | Lab 1: Triage in one call | lab holding slide | flowchart |
| 10 | Urgent is not risky: the declined card | points left, diagram right | flowchart |
| 11 | A Choice always picks a team | points left, diagram right | flowchart |
| 12 | Jev judges, your code decides | points left, diagram right | flowchart |

### Slide 2 · The reply that breaks your parser

```mermaid
flowchart TD
  M["message: i lost my card"] --> L["LLM, plain prompt"]
  L --> OK["credit_cards<br/>your code routes it"]
  L --> BAD["**credit_cards** or a sentence<br/>parse error"]
```

### Slide 3 · What a JSON schema cannot give you

```mermaid
flowchart TD
  M["message"] --> S["LLM + JSON schema"]
  S --> T["team: credit_cards"]
  T --> Q["how sure?<br/>no answer"]
```

### Slide 4 · System One: judgments, not text

```mermaid
flowchart TD
  ST["state: the message"] --> J["Jev"]
  Q["question: Choice of 10 teams"] --> J
  J --> A["choice + a probability per team"]
  A --> C["your code decides"]
```

### Slide 5 · Accuracy within noise, 4x faster, 12x cheaper

```mermaid
flowchart TD
  subgraph L["gpt-5.4-mini + JSON schema"]
    L1["median 946 ms<br/>$0.256 per 1,000 messages<br/>no probabilities"]
  end
  subgraph J["jev-1.14.0"]
    J1["median 252 ms<br/>$0.022 per 1,000 messages<br/>a probability per team"]
  end
```

### Slide 6 · One state, several questions

```mermaid
flowchart TD
  ST["state: the message"] --> J["system_one, one request"]
  QC["team: Choice, pick one"] --> J
  QS["frustration: Score, rate on levels"] --> J
  QN["travel_plans: Noul, yes or no"] --> J
  J --> AC["choice + probabilities"]
  J --> AS["score + probabilities"]
  J --> AN["noul: one number, 0 to 1"]
```

### Slide 7 · Read the distribution, not only the top answer

```mermaid
xychart-beta
  title "frustration: probability per level"
  x-axis ["calm", "annoyed", "angry"]
  y-axis "probability" 0 --> 1
  bar [0.51, 0.27, 0.22]
```

### Slide 8 · Judgments in Jev, decisions in code

```mermaid
flowchart TD
  J["Jev judges: urgency 0 to 2, risk 0 to 1"] --> R1{"risk >= 0.7"}
  R1 -- yes --> E["ESCALATE to a human"]
  R1 -- no --> R2{"risk > 0.3"}
  R2 -- yes --> V["REVIEW by a human"]
  R2 -- no --> R3{"urgency >= 1.5"}
  R3 -- yes --> P["PRIORITY to the team"]
  R3 -- no --> RT["ROUTE to the team"]
```

### Slide 9 · Lab 1: Triage in one call

```mermaid
flowchart LR
  L1["Level 1: Guided<br/>urgency levels, risk question"] --> L2["Level 2: Core<br/>triage(): one call + rules"]
  L2 -.-> L3["Level 3: Challenge, optional<br/>what does bundling buy?"]
```

### Slide 10 · Urgent is not risky: the declined card

```mermaid
flowchart TD
  D["declined card"] --> U["urgency 1.8"]
  D --> K["risk 0.04"]
  U --> P["PRIORITY, not ESCALATE"]
  K --> P
  LC["lost card"] --> K2["risk 0.97"] --> E["ESCALATE"]
```

### Slide 11 · A Choice always picks a team

```mermaid
flowchart TD
  M["what movies are playing"] --> C["Choice: team"]
  C --> T["small_talk, 0.49"]
  M -.-> N["Noul: does any team fit?<br/>Module 3"]
```

### Slide 12 · Jev judges, your code decides

```mermaid
flowchart TD
  A["ask: what is true?"] --> J["Jev: judgments"]
  J --> C["your code: decisions"]
  X["never ask: what should we do?"] -.-> J
```

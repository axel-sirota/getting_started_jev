# Platform Engineering Foundations: Slide Diagrams (Barclays)

Sep 29, 2026 · @Axel

Every slide diagram as raw Mermaid, keyed by slide number, in deck order. 30 diagrams: slide 1 is the title slide and has none. Export as `DIAGRAMS.md` next to `SLIDES.md` and render them on your laptop; titles and layouts match the [slide plan](https://claude.ai/code/artifact/840c85f2-47b5-4cf9-89eb-7c6057db591e).

## Index

Layouts: split is points left with the diagram right, full is the diagram as the whole body, demo is a holding slide shown while the Colab is on screen.

| Slide | Title | Layout | Mermaid type |
| --- | --- | --- | --- |
| 01 | Platform Engineering Foundations | title | none |
| 02 | Today's route | full | flowchart |
| 03 | The ticket test | split | sequenceDiagram |
| 04 | Why platforms, why now | split | flowchart |
| 05 | Ops vs DevOps vs platform engineering | full | flowchart |
| 06 | It's not a rebrand if it passes the ticket test | split | xychart-beta |
| 07 | What an IDP actually is | split | mindmap |
| 08 | Reference architecture: five planes | full | flowchart |
| 09 | Anatomy of a golden path | split | flowchart |
| 10 | Demo 1: new service in minutes | split | sequenceDiagram |
| 11 | When a rule breaks | split | flowchart |
| 12 | Debrief: what just happened | split | flowchart |
| 13 | From project to product | split | flowchart |
| 14 | How the platform team works with everyone else | split | stateDiagram-v2 |
| 15 | Buyer vs user | split | flowchart |
| 16 | Who owns the platform product today | split | pie |
| 17 | Build the roadmap from developer journeys | split | quadrantChart |
| 18 | The platform API is the product | split | flowchart |
| 19 | Golden path vs golden cage | split | flowchart |
| 20 | Why one metric lies | split | flowchart |
| 21 | Demo 2: the platform team's dashboard | split | flowchart |
| 22 | Live in Colab | demo | flowchart |
| 23 | Debrief: read adoption and satisfaction together | split | quadrantChart |
| 24 | How adoption actually happens | split | pie |
| 25 | Four barriers that stall adoption | full | flowchart |
| 26 | Demo 3: three ways to roll out the same tool | split | flowchart |
| 27 | Live: the rollout simulator | demo | timeline |
| 28 | Debrief: mandate the outcome, pave the path | split | flowchart |
| 29 | Early adoption playbook | full | flowchart |
| 30 | What to take back | split | flowchart |
| 31 | Q&A, and one thing to do this week | split | flowchart |

## Opening

### Slide 02 · Today's route

Layout: full

```mermaid
flowchart LR
  A["1. Fundamentals<br/>Demo: new service in minutes"] --> B["2. Product operating model<br/>Demo: the platform team's dashboard"]
  B --> C["3. Change adoption<br/>Demo: mandate vs make it easy"]
```

### Slide 03 · The ticket test

Layout: split

```mermaid
sequenceDiagram
  participant Dev as Developer
  participant Q as Ticket queue
  participant Ops as Infra team
  participant Sec as Security review
  Dev->>Q: Request an environment
  Q->>Ops: Picked up when there's capacity
  Ops->>Sec: Approval needed
  Sec-->>Ops: Questions
  Ops-->>Dev: Environment ready
  Dev->>Q: Now request monitoring
```

## Module 1: Platform Engineering Fundamentals

### Slide 04 · Why platforms, why now

Layout: split

```mermaid
flowchart LR
  A["Ops silo<br/>devs file tickets"] --> B["DevOps<br/>every team owns everything"]
  B --> C["Platform engineering<br/>shared complexity shifted down"]
  B -.->|cost, risk, duplication| C
```

### Slide 05 · Ops vs DevOps vs platform engineering

Layout: full

```mermaid
flowchart TB
  subgraph T["Traditional ops"]
    d1[Developer] -->|ticket| o1[Ops team] --> i1[Infra]
  end
  subgraph D["DevOps"]
    d2[Developer] -->|builds and runs it all| i2["Infra, CI, security, monitoring"]
  end
  subgraph P["Platform engineering"]
    d3[Developer] -->|self-service| p3["Platform API and golden paths"] --> i3[Infra]
    pt[Platform team] -->|builds and runs| p3
  end
```

### Slide 06 · It's not a rebrand if it passes the ticket test

Layout: split

```mermaid
xychart-beta
  title "The J-curve (illustrative shape, not data)"
  x-axis ["Start", "Launch", "Early use", "Complexity grows", "Maturing", "Mature"]
  y-axis "Performance" 0 --> 10
  line [5, 6, 6.5, 4, 6, 8]
```

### Slide 07 · What an IDP actually is

Layout: split

```mermaid
mindmap
  root((IDP))
    Interfaces
      Portal
      APIs and CLIs
      Golden path templates and docs
    Delivery
      Build and test automation
      Delivery automation
      Artifact storage
      Dev environments
    Run
      Infrastructure
      Data
      Messaging
      Observability
    Guardrails
      Identity and secrets
      Security
```

### Slide 08 · Reference architecture: five planes

Layout: full

```mermaid
flowchart TB
  DCP["Developer control plane<br/>portal, CLI, IDE, Git, workload spec"]
  subgraph PT["Wired and tested by the platform team"]
    IDP["Integration and delivery plane<br/>CI, registry, orchestrator, CD"]
    RES["Resource plane<br/>compute, databases, network, messaging"]
    OBS["Observability plane<br/>metrics, logs, traces, SLOs"]
    SEC["Security plane<br/>secrets, identity, policy as code"]
  end
  DCP -->|code and workload spec| IDP
  IDP -->|provisions and deploys| RES
  OBS -.- IDP
  OBS -.- RES
  SEC -.- IDP
  SEC -.- RES
```

### Slide 09 · Anatomy of a golden path

Layout: split

```mermaid
flowchart LR
  T[Template in portal] --> R["Repo with service,<br/>pipeline, config"]
  R --> C[CI build and tests]
  C --> P{Policy checks}
  P -->|pass| D[Deploy via GitOps]
  P -->|fail| F[Clear error with the fix]
  F --> R
  D --> O["Dashboards and alerts<br/>already wired"]
  R -.->|escape hatch| X["Override defaults,<br/>team owns it"]
```

### Slide 10 · Demo 1: new service in minutes

Layout: split

```mermaid
sequenceDiagram
  actor Dev as Developer
  participant Portal
  participant Git
  participant CI as CI and policy
  participant CD as GitOps CD
  participant K8s as Cluster
  Dev->>Portal: Name, owner, data class
  Portal->>Git: Repo, pipeline, catalog entry
  Git->>CI: Build, test, policy checks
  CI->>CD: Image and manifests
  CD->>K8s: Deploy
  K8s-->>Dev: Running service, dashboard, alerts
```

### Slide 11 · When a rule breaks

Layout: split

```mermaid
flowchart LR
  R["Request: confidential data,<br/>public ingress"] --> P{Policy check}
  P -->|fail| E["Error: confidential services<br/>can't be public.<br/>Set ingress to internal."]
  E -->|one-line fix| R2[Request updated]
  R2 --> P2{Policy check}
  P2 -->|pass| D[Deployed and monitored]
```

### Slide 12 · Debrief: what just happened

Layout: split

```mermaid
flowchart TB
  subgraph Before["Ticket path"]
    b1[Request] --> b2[Queue] --> b3[Manual provisioning] --> b4[Security review] --> b5[Monitoring request] --> b6[Running]
  end
  subgraph After["Golden path"]
    a1[Template] --> a2["Automated pipeline<br/>with policy checks"] --> a3[Running and monitored]
  end
```

## Module 2: Product Operating Models for Platform Teams

### Slide 13 · From project to product

Layout: split

```mermaid
flowchart TB
  subgraph Project["Platform as a project"]
    p1[Requirements] --> p2[Build] --> p3[Launch] --> p4[Hand over, move on]
  end
  subgraph Product["Platform as a product"]
    q1[Research journeys] --> q2[Ship a thin version]
    q2 --> q3[Measure value]
    q3 --> q4[Learn and reprioritise]
    q4 --> q1
  end
```

### Slide 14 · How the platform team works with everyone else

Layout: split

```mermaid
stateDiagram-v2
  state "Collaboration" as C
  state "X-as-a-Service" as X
  state "Facilitating" as F
  [*] --> C: new capability
  C --> X: capability is stable
  X --> F: a team needs uplift
  F --> X: team is self-sufficient
  X --> C: big change needed
```

### Slide 15 · Buyer vs user

Layout: split

```mermaid
flowchart LR
  B["Buyers<br/>CIO, risk, compliance"] -->|fund and set controls| PM[Platform product owner]
  U["Users<br/>engineers"] -->|journeys, pain, feedback| PM
  PM -->|roadmap| PL[Platform]
  PL -->|golden paths| U
  PL -->|control evidence| B
```

### Slide 16 · Who owns the platform product today

Layout: split

```mermaid
pie showData
  title Who owns the platform product (Vol 4, 518 respondents)
  "Dedicated Platform PMs" : 21.6
  "PMs plus product-minded engineers" : 15
  "No PM, engineers think like PMs" : 38
  "No product mindset" : 25.4
```

### Slide 17 · Build the roadmap from developer journeys

Layout: split

```mermaid
quadrantChart
  title Journeys by frequency and pain (example placement)
  x-axis Rare --> Frequent
  y-axis Mild pain --> Severe pain
  quadrant-1 Build first
  quadrant-2 Plan deliberately
  quadrant-3 Ignore for now
  quadrant-4 Quick wins
  New service to prod: [0.8, 0.85]
  Get a database: [0.7, 0.6]
  Debug a prod issue: [0.6, 0.75]
  Onboard a new hire: [0.35, 0.7]
  Rotate secrets: [0.3, 0.35]
```

### Slide 18 · The platform API is the product

Layout: split

```mermaid
flowchart LR
  subgraph Interfaces
    P[Portal]
    C[CLI]
    I[IDE]
    A[AI assistant]
  end
  P --> API
  C --> API
  I --> API
  A --> API
  API["Platform API<br/>declarative, versioned, in Git"] --> T[Terraform modules]
  API --> K[Kubernetes operators]
  API --> M[Managed cloud services]
```

### Slide 19 · Golden path vs golden cage

Layout: split

```mermaid
flowchart LR
  subgraph Path["Golden path"]
    g1[Defaults] --> g2[Override when needed]
    g1 --> g3[Clear error with the fix]
    g1 --> g4[Teams contribute templates]
  end
  subgraph Cage["Golden cage"]
    c1[Mandatory abstraction] --> c2[No escape hatch]
    c1 --> c3[Cryptic wrapper error]
    c1 --> c4[Central team approves all]
  end
```

### Slide 20 · Why one metric lies

Layout: split

```mermaid
flowchart TB
  L1["Adoption<br/>voluntary vs mandated"]
  L2["Onboarding speed<br/>idea to first prod deploy"]
  L3["Experience<br/>feedback loops, cognitive load, flow"]
  L4["Delivery outcomes<br/>DORA, on vs off platform"]
  L5["Health and control evidence<br/>workarounds, policy pass rate"]
  L1 ~~~ L2 ~~~ L3 ~~~ L4 ~~~ L5
```

### Slide 21 · Demo 2: the platform team's dashboard

Layout: split

```mermaid
flowchart LR
  S1[Service catalog] --> A[Adoption]
  S2[Pipeline timestamps] --> O[Onboarding speed]
  S3[DevEx survey] --> E[Experience]
  S4[Delivery and incident data] --> D[Delivery outcomes]
  S5[Support queue and policy engine] --> H[Health and controls]
  A --> R{Next quarter's bet}
  O --> R
  E --> R
  D --> R
  H --> R
```

### Slide 22 · Live in Colab

Layout: demo

```mermaid
flowchart LR
  H[Headline only] -->|Peel| L["Six layers, one per click"]
  L --> T[Flip CI mandated off]
  T --> B{Pick one bet}
  B -->|Play quarter| N[Next quarter with deltas]
  N -->|up to Q4| B
```

### Slide 23 · Debrief: read adoption and satisfaction together

Layout: split

```mermaid
quadrantChart
  title Adoption vs satisfaction (synthetic demo data)
  x-axis Low adoption --> High adoption
  y-axis Low satisfaction --> High satisfaction
  quadrant-1 Healthy product
  quadrant-2 Hidden gem
  quadrant-3 Rethink or retire
  quadrant-4 Likely a golden cage
  CI pipelines: [0.85, 0.25]
  Databases: [0.65, 0.75]
  Secrets: [0.3, 0.8]
  Preview environments: [0.2, 0.3]
```

## Module 3: Change Adoption Basics

### Slide 24 · How adoption actually happens

Layout: split

```mermaid
pie showData
  title How platform adoption happens (Vol 4)
  "Mandate (extrinsic push)" : 36.6
  "Genuine pull (intrinsic)" : 28.2
  "Participatory (users contribute)" : 18.3
  "Erratic, no strategy" : 16.9
```

### Slide 25 · Four barriers that stall adoption

Layout: full

```mermaid
flowchart LR
  B1[Built without asking users] --> S1[Solves problems nobody has]
  B2["Slow v1 in the J-curve dip"] --> S2[Teams wait it out]
  B3["Golden cage, no escape hatch"] --> S3[Workarounds and shadow IT]
  B4["No sponsor, buyer and user pulling apart"] --> S4[Funding cut before value shows]
```

### Slide 26 · Demo 3: three ways to roll out the same tool

Layout: split

```mermaid
flowchart TB
  T[Same new deployment pipeline] --> A["Division A<br/>mandate the tool"]
  T --> B["Division B<br/>pave the path"]
  T --> C["Division C<br/>mandate the outcome, pave the path"]
  A --> Q{Month 6: who's better off?}
  B --> Q
  C --> Q
```

### Slide 27 · Live: the rollout simulator

Layout: demo

```mermaid
timeline
  title Three rollouts of the same pipeline (illustrative scenario)
  section Division A, mandate the tool
    Month 1 : Deadline announced : Teams migrate under pressure
    Month 3 : High adoption on paper : Wrapper scripts appear
    Month 6 : Complaints go quiet : Gaps hidden in workarounds
  section Division B, pave the path
    Month 1 : Three pilot teams : Built with them
    Month 3 : Before and after numbers published : Champions demo it
    Month 6 : Next wave pulls it in : Old path gets a sunset date
  section Division C, mandate the outcome
    Month 1 : Controls announced with a deadline : Pilots build the golden path
    Month 3 : Golden path meets the controls by default : Off-path teams start proving their own
    Month 6 : Most teams on the path : Everyone else provably compliant
```

### Slide 28 · Debrief: mandate the outcome, pave the path

Layout: split

```mermaid
flowchart LR
  M["Mandated outcome<br/>control set for every prod service"] --> Q{How will a team comply?}
  Q -->|golden path| G["Controls built in,<br/>evidence automatic"]
  Q -->|own route| O["Team proves each control<br/>and carries the cost"]
  G --> W[The paved road becomes the easy, obvious choice]
```

### Slide 29 · Early adoption playbook

Layout: full

```mermaid
flowchart TB
  s1[Pick one frequent, painful journey] --> s2[Build with 2 to 3 pilot teams]
  s2 --> s3[Ship a thin version in weeks]
  s3 --> s4[Publish before and after numbers]
  s4 --> s5[Pilots become champions]
  s5 --> s6[Next wave with enabling support]
  s6 --> s7[Only then, sunset the old path]
```

## Wrap-up

### Slide 30 · What to take back

Layout: split

```mermaid
flowchart TB
  a[Remove tickets and cognitive load] --> b[Build what developer journeys call for]
  b --> c[Run it as a product]
  c --> d["Versioned API, golden paths,<br/>layered scorecard"]
  d --> e[Mandate the outcome, pave the path]
  e --> f["At Barclays: governance first,<br/>several platforms, shared standards"]
```

### Slide 31 · Q&A, and one thing to do this week

Layout: split

```mermaid
flowchart LR
  j[Pick one painful journey] --> o[Name its owner]
  o --> m[Baseline it today]
  m --> p[Find 2 pilot teams]
```

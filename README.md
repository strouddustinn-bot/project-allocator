# Project Allocator

**Evidence-driven project capital allocation for deciding what deserves your next hour, dollar, and unit of attention.**

Project Allocator is a decision engine for evaluating projects under uncertainty. It is designed to answer a harder question than _“Is this a good idea?”_:

> **Given everything else I could be doing, what should I fund, test, delay, scale, or kill right now?**

The system treats projects like investments competing for finite resources. It separates evidence from assumptions, models downside and opportunity cost, authorizes only the next justified level of commitment, and records real outcomes so future decisions become better calibrated.

---

## Why this exists

Most project evaluation systems fail in one of two ways:

1. They are qualitative enough to become motivational storytelling.
2. They are quantitative enough to create false precision.

Project Allocator is built to avoid both.

A score is useful as a summary, but it is **not the decision engine**. A project can score well and still be blocked from meaningful commitment if the evidence is weak. Likewise, a high-upside idea may deserve only a six-hour validation test rather than a full build.

The core principle is simple:

> **A project earns progressively larger allocations of resources as evidence improves.**

---

## Decision stages

Project Allocator uses staged commitment instead of a binary yes/no decision.

| Stage | Meaning |
|---|---|
| `REJECT` | Do not allocate further resources under current conditions |
| `OBSERVE` | Keep visible, but do not actively fund |
| `INVESTIGATE` | Spend a small amount gathering missing information |
| `VALIDATE` | Run a falsifiable test of the critical assumption |
| `PILOT` | Prove the project works in a constrained real-world setting |
| `COMMIT` | Allocate meaningful resources |
| `SCALE` | Increase allocation because results justify it |
| `EXIT` | Stop allocating resources and close the loop |

A decision should answer not only **what to do**, but also **how much to risk next**.

Example:

```text
DECISION: VALIDATE

Primary uncertainty:
Customers may not pay the proposed price.

Authorized next investment:
$100
6 hours

Test:
Offer a paid pilot to 20 qualified prospects.

Pass:
3+ genuine commitments

Fail:
0-1 genuine commitments
```

---

## Core evaluation model

Every project is evaluated across several layers.

### 1. Fatal constraints

Before scoring anything, the engine checks for blockers such as:

- no identifiable customer, user, or beneficiary
- no credible value-creation mechanism
- unavailable required resources
- structural or regulatory blockers
- unacceptable downside
- dependencies that cannot currently be satisfied
- economics that fail even in a strong scenario

Fatal constraints override a high score.

### 2. Evidence quality

Claims are tracked as:

- `VERIFIED`
- `ESTIMATE`
- `ASSUMPTION`
- `UNKNOWN`

Each claim also has:

- importance
- confidence
- source
- consequence if wrong

This creates an evidence ledger instead of allowing assumptions to quietly become facts.

### 3. Economics

The engine considers:

```text
Expected gross value
- cash required
- operating costs
- value of time
- downside cost
- opportunity cost
= net expected value
```

Projects can be evaluated across low, base, and high scenarios.

### 4. Opportunity cost

Projects are not evaluated in isolation.

The engine asks:

> What would receive these same hours, dollars, and attention if this project did not?

That competing use of resources is treated as a real cost.

### 5. Reversibility and downside

Cheap, reversible experiments are preferred over expensive irreversible commitments.

The engine is designed to buy information before buying execution whenever uncertainty is high.

### 6. Strategic leverage

Direct financial return is not the only source of value.

Projects may create reusable assets such as:

- code
- customers
- audience
- data
- distribution
- brand
- domain expertise
- automation
- intellectual property
- equipment
- supplier relationships

These assets can increase the value of future projects.

---

## Summary score

The current engine can produce a 100-point summary score using:

| Factor | Weight |
|---|---:|
| Economic / practical upside | 20 |
| Evidence quality | 15 |
| Speed to signal | 15 |
| Strategic leverage | 15 |
| Execution feasibility | 10 |
| Downside / reversibility | 10 |
| Differentiation | 5 |
| Reusability | 5 |
| Comparative advantage | 5 |

The score is **diagnostic, not authoritative**.

Weak evidence can prevent `COMMIT` regardless of score.

---

## Current architecture

The first version is intentionally small.

```text
project-allocator/
├── project_allocator/
│   ├── models.py
│   ├── evidence.py
│   ├── economics.py
│   ├── scoring.py
│   ├── decision.py
│   ├── db.py
│   ├── serde.py
│   ├── cli.py
│   └── __main__.py
├── tests/
│   └── test_engine.py
├── example_project.json
├── pyproject.toml
└── README.md
```

### Python owns

- deterministic decision rules
- economics
- evidence scoring
- staged commitment logic
- persistence
- resource authorization
- portfolio ranking
- calibration

### AI will eventually own

- turning messy project descriptions into structured inputs
- identifying hidden assumptions
- adversarial critique
- proposing validation tests
- interpreting new evidence
- explaining tradeoffs

The AI layer should call the engine. The AI should not be the engine.

---

## CLI design

The intended CLI is:

```bash
python -m project_allocator evaluate example_project.json
```

List latest evaluations:

```bash
python -m project_allocator list
```

Record what actually happened:

```bash
python -m project_allocator result "Example Project" PASS \
  --cash 80 \
  --hours 5.5 \
  --notes "4 paid pilot commitments"
```

The default database is SQLite:

```text
project_allocator.db
```

A custom database can be supplied with:

```bash
python -m project_allocator --db my-portfolio.db evaluate example_project.json
```

---

## Example project input

```json
{
  "name": "Example Project",
  "objective": "Prove demand before committing to a full build",
  "beneficiary": "Small construction companies",
  "value_mechanism": "Save administrative time and reduce payroll errors",

  "upside_low": 2000,
  "upside_base": 10000,
  "upside_high": 30000,

  "probability_low": 0.2,
  "probability_base": 0.45,
  "probability_high": 0.7,

  "cash_required": 1000,
  "hours_required": 40,
  "hourly_value": 50,

  "time_to_signal_days": 14,

  "strategic_leverage": 4,
  "reversibility": 4,
  "execution_feasibility": 4,
  "differentiation": 3,
  "reusability": 4,
  "comparative_advantage": 4
}
```

---

## Design rules

Project Allocator follows several non-negotiable rules:

1. **Evidence beats narrative.**
2. **Sunk costs do not justify future spending.**
3. **Time is treated as a real cost.**
4. **Opportunity cost is explicit.**
5. **Potential upside is not the same as expected value.**
6. **Weak evidence buys a test, not a commitment.**
7. **The cheapest falsifiable experiment is preferred.**
8. **Scores summarize; they do not overrule hard constraints.**
9. **Projects compete against alternatives, not against zero.**
10. **Real outcomes must be recorded so estimates can be calibrated over time.**

---

## What is deliberately not in v0.1

The project is intentionally avoiding premature complexity.

Not yet included:

- web dashboard
- multi-agent orchestration
- authentication
- Monte Carlo simulation
- automated public-web research
- automatic project generation
- complex integrations
- polished UI

Those features only earn their way into the system if the decision kernel proves useful in real allocation decisions.

---

## Roadmap

### Phase 1 — Decision kernel

- deterministic project evaluation
- evidence ledger
- staged decisions
- bounded validation budgets
- SQLite persistence
- result recording

### Phase 2 — Portfolio allocator

The next major feature.

Given:

```text
Available time: 30 hours
Available capital: $500
Active projects: 8
```

The engine should answer:

```text
Project A -> 12h / $100
Project B -> 8h / $250
Project C -> 4h / $0
Project D -> validation only
Project E -> no allocation
```

The goal is to decide where the **next marginal hour and dollar** should go.

### Phase 3 — Calibration

Compare predictions against actual outcomes:

- predicted hours vs actual hours
- predicted cost vs actual cost
- predicted conversion vs actual conversion
- predicted payoff vs actual payoff

Over time, the engine should learn where estimates are consistently optimistic or conservative.

### Phase 4 — AI reasoning layer

Add an AI interface that can:

- accept project ideas in plain language
- structure them into the project model
- identify critical assumptions
- red-team the thesis
- propose experiments
- explain the resulting allocation decision

### Phase 5 — Optional interfaces

The core should remain interface-independent.

Possible clients:

- ChatGPT
- CLI / TUI
- web application
- local agent
- MCP server
- API clients

---

## Long-term goal

Project Allocator is not intended to become another productivity dashboard.

The long-term system should function like a small investment committee for a person's projects:

```text
CAPTURE
  -> STRUCTURE
  -> RED TEAM
  -> IDENTIFY ASSUMPTIONS
  -> CHECK EVIDENCE
  -> MODEL ECONOMICS
  -> MODEL UNCERTAINTY
  -> COMPARE OPPORTUNITY COST
  -> AUTHORIZE NEXT INVESTMENT
  -> RUN TEST
  -> RECORD RESULT
  -> UPDATE BELIEFS
  -> RE-RANK PORTFOLIO
```

The success criterion is not how sophisticated the software becomes.

The success criterion is whether it reliably causes better projects to receive more resources and weaker projects to receive less.

> **If Project Allocator eventually tells us to stop working on Project Allocator because something else has a better expected return, it is doing its job.**

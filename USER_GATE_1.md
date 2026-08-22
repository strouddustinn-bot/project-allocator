# User Gate 1 — First Real Project

The first product gate is reached when a clean checkout can:

1. install Project Allocator,
2. pass its environment health check,
3. interactively capture a real project,
4. save the project snapshot,
5. evaluate the project deterministically,
6. persist the decision history, and
7. return an explicit next-stage allocation of cash and hours.

## Enter the gate

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
pursuit doctor
pursuit intake
```

The engine should end the intake with a decision such as:

```text
DECISION: VALIDATE
EVIDENCE CONFIDENCE: LOW

AUTHORIZED NEXT INVESTMENT:
  Cash:  $100.00
  Hours: 6

NEXT ACTION:
  Offer a paid pilot to 20 qualified prospects before building further.
```

The point of this gate is not polish. It is to prove that a real user can move from an unstructured project idea to a persisted, bounded allocation decision without hand-editing source code.

## Gate acceptance criteria

- `python -m unittest discover -s tests -v` passes.
- `pursuit doctor` reports `STATUS: READY`.
- `pursuit intake` creates a JSON snapshot under `.pursuit/projects/`.
- the same intake creates/updates `.pursuit/project_allocator.db`.
- the output includes decision, score, evidence confidence, scenario economics, authorized cash, authorized hours, and next action.

Once those conditions hold, stop adding infrastructure and use the engine on a real project.

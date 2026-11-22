# Project Allocator — repository instructions

## Purpose
Evidence-driven allocation of time, money, and effort among competing projects. The source of truth for the product model is `README.md`.

## Decision invariants
- Separate observed evidence, assumptions, and forecasts; never turn uncertainty into false precision.
- Enforce fatal constraints and explicit capital/authority limits before ranking opportunities.
- Consider opportunity cost, execution burden, downside, reversibility, speed to proof, and real cash consequences.
- Maintain transparent calculations. Keep scoring explanations traceable to user-supplied inputs.
- AI-generated rationales may help interpret inputs but must not bypass deterministic constraints or fabricate outcomes.

## Working practices
Inspect the implemented Python entry points, persistence layer, fixtures, and tests before changing decision logic. Use the commands currently documented in `README.md` only after confirming the corresponding files exist; do not assume the whole roadmap is implemented. Run targeted tests or CLI examples with synthetic data and disclose checks not performed.

## Safety and maintenance
Do not initiate purchases, payments, or autonomous resource commitments. Keep project and financial information private. Update this document when the decision kernel, data model, or operating commands materially change.

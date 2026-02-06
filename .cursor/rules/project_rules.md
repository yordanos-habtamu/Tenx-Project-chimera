# Project Chimera - Autonomous Influencer System Rules

## Prime Directive
NEVER generate code without checking `specs/` first. Specifications are the single source of truth.

## Traceability
Explain your plan before writing code. Every action should be traceable back to a requirement or a spec.

## Tech Stack
- **Backend:** FastAPI, Python 3.11/3.12 (using `uv` for management)
- **Database:** PostgreSQL + TimescaleDB (production), SQLite (local development)
- **Frontend:** Vanilla JS/HTML/CSS (Static SPA)
- **Governance:** Spec-Driven Development (SDD), Test-Driven Development (TDD)

## File Conventions
- Agent logic belongs in `src/agents/`
- Skill interfaces belong in `skills/`
- All tests must go in `tests/`
- Specifications are located in `specs/`

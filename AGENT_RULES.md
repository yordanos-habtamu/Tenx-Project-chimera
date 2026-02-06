
# Project Chimera - The Brain

This file serves as the central context for any AI agent working on this repository.

## Project Identity
**Project Chimera** is an autonomous influencer system designed to research trends, generate content, and publish it across platforms.

## CORE RULES (The Prime Directive)
1.  **NEVER generate code without checking specs/ first.**
    *   Always verify your proposed changes against the documented requirements.
    *   If specs are missing, ask for clarification.

2.  **Traceability**
    *   **Explain your plan before writing code.**
    *   Use formatted markdown for plans (e.g., `implementation_plan.md`).

## Architecture
-   **Swarm**: Hierarchical agent swarm (Supervisor -> Research/Content/Safety/Distribution).
-   **API**: FastAPI backend serving both API endpoints and the Frontend Dashboard.
-   **Persistence**: SQLAlchemy with SQLite (local) / PostgreSQL (prod).

## Critical Files
-   `src/main.py`: Main entry point for the agent system.
-   `src/api/app.py`: Main entry point for the Web API.
-   `.github/copilot-instructions.md`: Rules for GitHub Copilot.

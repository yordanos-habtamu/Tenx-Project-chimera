# Loom Video Script & Submission Guide

This guide prepares you for the 5-minute Loom video submission.

## 1. Spec Structure & OpenClaw Plan (1.5 Mins)
- **Action:** Open the `specs/` directory in your IDE.
- **Narrative:** "Our project follows a strict Spec-Driven Development (SDD) approach. We have full specs for functional requirements, technical API contracts, and our OpenClaw integration."
- **Focus:** Show `specs/technical.md` (mention ERDs and API schemas) and `specs/openclaw_integration.md`. Explain that Chimera acts as a discoverable ContentProducer in the agent social network.

## 2. Failing Tests (TDD) (1.5 Mins)
- **Action:** Open a terminal and run `make test`.
- **Narrative:** "We use a Test-Driven Development strategy. I've defined the contract goal-posts using failing tests before implementing the core logic."
- **Focus:** Point out the failures in `test_trend_fetcher.py` and `test_skills_interface.py`. Explain how these define the "empty slots" the AI agents will fill.

## 3. IDE Agent Context (1 Min)
- **Action:** Open your IDE's Chat (Cursor/Claude) and ask: *"How does Project Chimera ensure content safety and traceability?"*
- **Narrative:** "Our IDE agents are governed by strict context rules."
- **Focus:** Show the agent's response. It should mention the `specs/` directory, the `SafetyLayer` (HITL), and the rules in `.cursor/rules/`.

## 4. Infrastructure & Governance (1 Min)
- **Action:** Show the `Dockerfile`, `Makefile`, and `.github/workflows/main.yml`.
- **Narrative:** "The repository is production-ready with a multi-stage Docker build, standardized Makefile commands, and a CI/CD governance pipeline that runs spec-checks and security scans."

## Submission Reminders:
- **GitHub Link:** Ensure your repo is public.
- **Report Link:** Submit the link to your Google Doc/PDF report (not the drive link).
- **Video Link:** Paste your Loom link.
- **MCP Sense:** Keep it active while you demonstrate—this is your "Black Box" flight data.

# Project Chimera: Autonomous AI Influencer Infrastructure

Project Chimera is a state-of-the-art autonomous AI influencer infrastructure designed from the orchestration layer downward. It implements a hierarchical swarm architecture to automate the end-to-end content creation, moderation, and distribution lifecycle.

## 🌟 Core Thesis
Project Chimera bridges the gap between raw AI power and reliable, scalable application. Its competitive advantage lies in its reliable orchestration, observability, and robust governance—turning AI into a dependable agentic service.

## 🏗️ Architecture: Hierarchical Swarm

Chimera leverages a **Hierarchical Swarm with Supervisor Orchestration** pattern for maximum modularity and resilience.

### Supervisor Layer
- **SupervisorAgent**: The central orchestrator that decomposes high-level objectives into specialized tasks.
- **AgentOrchestrator**: Maintains registry and status tracking for the entire agent fleet.

### Specialized Swarms
- **ResearchSwarm**: Fetches trends (`TrendFetcherAgent`) and identifies niches (`NicheAnalystAgent`).
- **ContentSwarm**: Writes scripts (`ScriptWriterAgent`) and generates assets (`VideoGeneratorAgent`, `ThumbnailDesignerAgent`).
- **SafetyLayer**: Provides automated moderation (`ContentModerationAgent`) and human intervention mechanisms (`HumanInLoopAgent`).
- **DistributionSwarm**: Publishes to social platforms (`PlatformPublisherAgent`) and announces to the OpenClaw network (`OpenClawAnnouncerAgent`).

## 🛠️ Technology Stack
- **Language**: Python 3.11+
- **Framework**: FastAPI (API & Dashboard)
- **Database**: SQLite with SQLAlchemy ORM
- **Package Manager**: `uv` (Fast dependency management)
- **Quality**: `ruff` (Linting), `black` (Formatting), `pytest` (Testing)

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yordanos-habtamu/Tenx-Project-chimera.git
   cd Tenx-Project-chimera
   ```
2. Setup environment:
   ```bash
   make setup
   ```

### Running the App
Start the FastAPI server and Dashboard:
```bash
make run
```
The dashboard will be available at `http://localhost:8000/dashboard`.

## 🧪 Development Workflow
The `Makefile` contains all necessary commands for development:
- `make lint`: Run code quality checks (Ruff & Black).
- `make spec-check`: Verify alignment with architectural specifications.
- `make test`: Run the test suite.
- `make build`: Build the Docker image.
- `make clean`: Remove build artifacts and temporary files.

## 📄 Key Documentation
- [IMPLEMENTATION.md](IMPLEMENTATION.md): Technical deep-dive into the system architecture.
- [CONTRIBUTIONS.md](CONTRIBUTIONS.md): Summary of project stabilization and CI/CD fixes.
- [AGENT_RULES.md](AGENT_RULES.md): Governing rules for autonomous agents.

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

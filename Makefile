.PHONY: setup test test-docker spec-check lint run clean build help

# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = $(PYTHON) -m pytest
DOCKER_IMAGE = project-chimera:latest

help: ## Show this help message
	@echo "Project Chimera - Development & Operations Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@$(grep_search -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}')
	@echo "  setup          Install dependencies using uv"
	@echo "  test           Run pytest locally"
	@echo "  test-docker    Run tests inside a Docker container"
	@echo "  spec-check     Verify if code aligns with project specifications"
	@echo "  lint           Run ruff and black for code quality"
	@echo "  run            Start the application locally"
	@echo "  build          Build the Docker image"
	@echo "  clean          Clean up cache and temporary files"

setup: ## Install dependencies using uv
	@echo "Installing dependencies..."
	@uv pip install --system .[dev]

test: ## Run local tests
	@echo "Running tests..."
	@uv run pytest tests/ -v

build: ## Build Docker image
	@echo "Building Docker image $(DOCKER_IMAGE)..."
	docker build -t $(DOCKER_IMAGE) .

test-docker: build ## Run tests inside Docker
	@echo "Running tests in Docker..."
	docker run --rm $(DOCKER_IMAGE) python3 -m pytest tests/

spec-check: ## Verify code alignment with specs
	@echo "Running specification alignment check..."
	@uv run python scripts/spec_checker.py

lint: ## Run linting checks
	@echo "Running ruff check..."
	@uv run ruff check .
	@echo "Running black check..."
	@uv run black --check .

run: ## Run the application
	@echo "Starting application..."
	@uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

clean: ## Remove build artifacts and caches
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".coverage" -exec rm -rf {} +
	@find . -type d -name "dist" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

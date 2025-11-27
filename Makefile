.PHONY: help setup install init-db run test lint format clean docker-build docker-up docker-down

PYTHON := python3
VENV := siberindo-venv
VENV_BIN := $(VENV)/bin

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)SIBERINDO BTS GUI - Available Commands$(NC)"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Create virtual environment and install dependencies
	@echo "$(BLUE)Setting up virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(VENV_BIN)/pip install --upgrade pip setuptools wheel
	$(VENV_BIN)/pip install -r requirements.txt
	@echo "$(GREEN)✓ Setup complete!$(NC)"

install: setup ## Alias for setup

init-db: ## Initialize database with schema and sample data
	@echo "$(BLUE)Initializing database...$(NC)"
	$(VENV_BIN)/python scripts/init_db.py
	@echo "$(GREEN)✓ Database initialized!$(NC)"

run: ## Run the application
	@echo "$(BLUE)Starting SIBERINDO BTS GUI...$(NC)"
	$(VENV_BIN)/python app.py

dev: ## Run in development mode with debug
	@echo "$(BLUE)Starting SIBERINDO BTS GUI (Development Mode)...$(NC)"
	FLASK_ENV=development FLASK_DEBUG=1 $(VENV_BIN)/python app.py

test: ## Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	$(VENV_BIN)/pytest tests/test_suite.py -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(VENV_BIN)/pytest tests/test_suite.py -v --cov=modules --cov-report=html --cov-report=term

lint: ## Run linting (flake8)
	@echo "$(BLUE)Running flake8 linter...$(NC)"
	$(VENV_BIN)/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=120 \
	  --statistics --exclude=siberindo-venv,__pycache__,.git || true

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code with black...$(NC)"
	$(VENV_BIN)/black . --exclude=siberindo-venv
	@echo "$(BLUE)Sorting imports with isort...$(NC)"
	$(VENV_BIN)/isort . --skip=siberindo-venv
	@echo "$(GREEN)✓ Code formatted!$(NC)"

check-osmo: ## Check for remaining 'osmo' references
	@echo "$(BLUE)Checking for 'osmo' references...$(NC)"
	@if grep -r -i "osmo" --include="*.py" --include="*.html" --include="*.js" --include="*.md" . \
	  --exclude-dir=siberindo-venv \
	  --exclude-dir=.git \
	  --exclude-dir=__pycache__ \
	  2>/dev/null | grep -v "third-party\|osmosdr"; then \
	  echo "$(RED)✗ Found osmo references!$(NC)"; \
	  exit 1; \
	else \
	  echo "$(GREEN)✓ No osmo references found!$(NC)"; \
	fi

clean: ## Clean up cache, test files, and virtual environment
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/ || true
	rm -rf dist/ build/ *.egg-info || true
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t siberindo-bts:latest -t siberindo-bts:$(shell date +%Y%m%d) .
	@echo "$(GREEN)✓ Docker image built!$(NC)"

docker-up: ## Start Docker containers with docker-compose
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Containers started!$(NC)"
	@echo "Access application at http://localhost:5000"
	@echo "Admin: admin / password123"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers stopped!$(NC)"

docker-logs: ## Show Docker logs
	docker-compose logs -f siberindo-bts

docker-ps: ## Show running Docker containers
	docker ps --filter "label=com.docker.compose.project=bts"

db-reset: ## Reset database (WARNING: Deletes all data!)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
	  rm -f data/siberindo_bts.db; \
	  $(MAKE) init-db; \
	else \
	  echo "Cancelled."; \
	fi

smoke-test: ## Run smoke tests (quick validation)
	@echo "$(BLUE)Running smoke tests...$(NC)"
	@echo "Testing health endpoint..."
	curl -s http://localhost:5000/health | grep -q "healthy" && echo "$(GREEN)✓ Health check passed$(NC)" || echo "$(RED)✗ Health check failed$(NC)"
	@echo "$(GREEN)✓ Smoke tests complete!$(NC)"

all: setup init-db test ## Run complete setup: environment, database, tests

.DEFAULT_GOAL := help

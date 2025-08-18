.PHONY: help install dev test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt

dev: ## Start development server
	python dev.py

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html

lint: ## Run linting
	ruff check .

format: ## Format code
	black .
	ruff check --fix .

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov

seed: ## Seed database with sample data
	python -m app.seed.seed

setup: install-dev ## Setup development environment
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the server"
	@echo "Run 'make seed' to populate the database"

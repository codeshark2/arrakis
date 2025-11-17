.PHONY: help install dev test lint format clean docker-build docker-up docker-down docker-logs

# Default target
.DEFAULT_GOAL := help

## help: Show this help message
help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'

## install: Install all dependencies (backend + frontend)
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm ci
	@echo "Done!"

## install-dev: Install development dependencies
install-dev:
	@echo "Installing backend dev dependencies..."
	cd backend && pip install ruff black pytest pytest-cov
	@echo "Installing frontend dev dependencies..."
	cd frontend && npm ci
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "Done!"

## dev: Start development servers (backend + frontend)
dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && source venv/bin/activate && python -m app.main

dev-frontend:
	cd frontend && npm run dev

## test: Run all tests
test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false
	@echo "All tests passed!"

## test-cov: Run tests with coverage
test-cov:
	@echo "Running backend tests with coverage..."
	cd backend && pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "Running frontend tests with coverage..."
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "Coverage reports generated!"
	@echo "Backend: backend/htmlcov/index.html"
	@echo "Frontend: frontend/coverage/lcov-report/index.html"

## lint: Run linters
lint:
	@echo "Linting backend..."
	cd backend && ruff check app/
	@echo "Linting frontend..."
	cd frontend && npm run lint
	@echo "Linting complete!"

## format: Format code
format:
	@echo "Formatting backend code..."
	cd backend && black app/
	cd backend && ruff check app/ --fix
	@echo "Formatting frontend code..."
	cd frontend && npm run lint -- --fix
	@echo "Formatting complete!"

## type-check: Run type checking
type-check:
	@echo "Type checking frontend..."
	cd frontend && npm run type-check
	@echo "Type checking complete!"

## clean: Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Clean complete!"

## docker-build: Build Docker images
docker-build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "Docker build complete!"

## docker-up: Start Docker containers
docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "Containers started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "View logs: make docker-logs"

## docker-down: Stop Docker containers
docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "Containers stopped!"

## docker-logs: View Docker logs
docker-logs:
	docker-compose logs -f

## docker-restart: Restart Docker containers
docker-restart: docker-down docker-up

## setup-env: Create environment files from samples
setup-env:
	@echo "Setting up environment files..."
	@if [ ! -f backend/.env ]; then cp backend/env.sample backend/.env && echo "Created backend/.env"; fi
	@if [ ! -f frontend/.env.local ]; then cp frontend/env.local.sample frontend/.env.local && echo "Created frontend/.env.local"; fi
	@echo "Done! Please edit the .env files with your configuration."

## ci: Run CI checks locally
ci: lint type-check test
	@echo "All CI checks passed!"

## pre-commit: Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

## build: Build for production
build:
	@echo "Building backend..."
	cd backend && python -m compileall app/
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build complete!"

## serve: Serve production build
serve:
	@echo "Serving production build..."
	@make -j2 serve-backend serve-frontend

serve-backend:
	cd backend && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

serve-frontend:
	cd frontend && npm start

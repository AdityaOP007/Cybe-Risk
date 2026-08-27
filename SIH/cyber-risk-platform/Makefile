# ==============================================================================
# Cyber Risk Platform — Makefile
# ==============================================================================
# Usage: make <target>
# On Windows without make, use the equivalent commands shown in README.md.
# ==============================================================================

.PHONY: install dev test lint format docker-up docker-down docker-build clean help

# --- Help (default target) ---
help:
	@echo ""
	@echo "  Cyber Risk Platform — Development Commands"
	@echo "  ==========================================="
	@echo ""
	@echo "  make install       Install backend & frontend dependencies"
	@echo "  make dev           Start backend & frontend dev servers"
	@echo "  make test          Run all tests"
	@echo "  make lint          Run linters (backend + frontend)"
	@echo "  make format        Auto-format code (backend + frontend)"
	@echo "  make docker-up     Start all services via Docker Compose"
	@echo "  make docker-down   Stop all Docker Compose services"
	@echo "  make docker-build  Build and start Docker Compose services"
	@echo "  make clean         Remove build artifacts and caches"
	@echo ""

# --- Install dependencies ---
install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# --- Development servers ---
dev:
	@echo "Starting backend and frontend dev servers..."
	@echo "Run these in separate terminals:"
	@echo "  Terminal 1: cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
	@echo "  Terminal 2: cd frontend && npm run dev"

# --- Testing ---
test:
	cd backend && python -m pytest tests/ -v

# --- Linting ---
lint:
	cd backend && ruff check . && black --check .
	cd frontend && npx eslint src/

# --- Formatting ---
format:
	cd backend && ruff check --fix . && black .
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,css,json}"

# --- Docker ---
docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-build:
	docker compose up --build -d

# --- Cleanup ---
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true

# Makefile for MongoDB Labs

.PHONY: help test test-fast test-all test-coverage docker-up docker-down clean install lint

# Default target
help:
	@echo "MongoDB Labs - Available Commands"
	@echo "================================="
	@echo "  make test          Run fast tests only"
	@echo "  make test-all      Run all tests (including slow)"
	@echo "  make test-coverage Run tests with coverage report"
	@echo "  make test-lab LAB=name Test specific lab"
	@echo ""
	@echo "  make docker-up     Start MongoDB with Docker"
	@echo "  make docker-down   Stop MongoDB"
	@echo "  make docker-reset  Reset Docker (removes data)"
	@echo ""
	@echo "  make update-index  Update lab index (README/LABS.md)"
	@echo "  make check-index   Check if lab index is current"
	@echo "  make list-labs     List all available labs"
	@echo "  make validate-labs Validate all lab structures"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make install-dev   Install dev dependencies"
	@echo "  make lint          Run code quality checks"
	@echo "  make format        Auto-format code"
	@echo "  make clean         Remove generated files"

# Testing targets
test:
	@echo "Running fast tests..."
	python scripts/test_runner.py

test-fast:
	@echo "Running unit tests only..."
	pytest tests/ -m "unit" -v

test-all:
	@echo "Running all tests (including slow)..."
	python scripts/test_runner.py --slow

test-coverage:
	@echo "Running tests with coverage..."
	python scripts/test_runner.py --coverage

test-lab:
	@echo "Testing lab: $(LAB)"
	python scripts/test_runner.py --lab $(LAB)

test-ci:
	@echo "Running CI tests..."
	pytest tests/ -v -m "not slow" --tb=short

# Docker targets
docker-up:
	@echo "Starting MongoDB with Docker..."
	docker-compose up -d
	@echo "Waiting for MongoDB to be ready..."
	python scripts/wait_for_mongo.py --docker --quiet

docker-down:
	@echo "Stopping MongoDB..."
	docker-compose down

docker-reset:
	@echo "Resetting Docker (removes all data)..."
	docker-compose down -v
	docker-compose up -d
	python scripts/wait_for_mongo.py --docker --quiet

docker-logs:
	docker logs mongodb-labs -f

# Installation targets
install:
	@echo "Installing dependencies..."
	pip install pymongo

install-dev: install
	@echo "Installing development dependencies..."
	pip install -r requirements-test.txt

install-all: install-dev
	@echo "Installing all lab requirements..."
	@for lab in labs/*/; do \
		if [ -f "$$lab/requirements.txt" ]; then \
			echo "Installing $$lab requirements..."; \
			pip install -r "$$lab/requirements.txt"; \
		fi \
	done

# Code quality targets
lint:
	@echo "Running linters..."
	flake8 labs/ scripts/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
	@echo "Checking formatting..."
	black --check labs/ scripts/ tests/ || true
	isort --check-only labs/ scripts/ tests/ || true

format:
	@echo "Auto-formatting code..."
	black labs/ scripts/ tests/
	isort labs/ scripts/ tests/

# Lab management
list-labs:
	@python scripts/lab.py list

validate-labs:
	@for lab in labs/*/; do \
		lab_name=$$(basename $$lab); \
		echo "Validating $$lab_name..."; \
		python scripts/lab.py validate $$lab_name || true; \
	done

update-index:
	@echo "Updating lab index..."
	@python scripts/build_index.py
	@echo "Lab index updated"

check-index:
	@echo "Checking if lab index is up-to-date..."
	@python scripts/build_index.py --check

run-lab:
	@if [ -z "$(LAB)" ]; then \
		echo "Usage: make run-lab LAB=lab_name"; \
		exit 1; \
	fi
	@echo "Running lab: $(LAB)"
	python scripts/lab.py all $(LAB) --hours 0.1

# Cleanup targets
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf *.egg-info

clean-data:
	@echo "Cleaning MongoDB data..."
	@for lab in labs/*/; do \
		lab_name=$$(basename $$lab); \
		echo "Cleaning $$lab_name database..."; \
		python scripts/lab.py clean $$lab_name || true; \
	done

# Development shortcuts
dev: docker-up
	@echo "Development environment ready"
	@echo "MongoDB running at: mongodb://localhost:27017"
	@echo "Run 'make test' to run tests"

# CI simulation
ci-local: docker-up
	@echo "Running CI locally..."
	make test-ci
	make lint
	@echo "CI simulation complete"

.DEFAULT_GOAL := help
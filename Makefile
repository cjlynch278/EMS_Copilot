# Variables
PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python
DOCKER_COMPOSE := docker-compose

# Colors for terminal output
CYAN := \033[0;36m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help setup clean build run stop logs test lint format install-dev install-prod

# Default target
help:
	@echo "${CYAN}Available commands:${NC}"
	@echo "${GREEN}setup${NC}        - Create virtual environment and install dependencies"
	@echo "${GREEN}clean${NC}        - Remove virtual environment and cache files"
	@echo "${GREEN}build${NC}        - Build Docker containers"
	@echo "${GREEN}run${NC}          - Run the application using Docker Compose"
	@echo "${GREEN}stop${NC}         - Stop running containers"
	@echo "${GREEN}logs${NC}         - View container logs"
	@echo "${GREEN}test${NC}         - Run tests"
	@echo "${GREEN}lint${NC}         - Run linting"
	@echo "${GREEN}format${NC}       - Format code"
	@echo "${GREEN}install-dev${NC}  - Install development dependencies"
	@echo "${GREEN}install-prod${NC} - Install production dependencies"

# Setup virtual environment
setup:
	@echo "${CYAN}Creating virtual environment...${NC}"
	$(PYTHON) -m venv $(VENV)
	@echo "${CYAN}Installing dependencies...${NC}"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements_local.txt
	@echo "${GREEN}Setup complete!${NC}"

# Clean up
clean:
	@echo "${CYAN}Cleaning up...${NC}"
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	@echo "${GREEN}Clean complete!${NC}"

# Docker commands
build:
	@echo "${CYAN}Building Docker containers...${NC}"
	$(DOCKER_COMPOSE) build
	@echo "${GREEN}Build complete!${NC}"

run:
	@echo "${CYAN}Starting application...${NC}"
	$(DOCKER_COMPOSE) up

stop:
	@echo "${CYAN}Stopping containers...${NC}"
	$(DOCKER_COMPOSE) down
	@echo "${GREEN}Containers stopped!${NC}"

logs:
	@echo "${CYAN}Viewing logs...${NC}"
	$(DOCKER_COMPOSE) logs -f

# Development commands
test:
	@echo "${CYAN}Running tests...${NC}"
	$(PYTHON_VENV) -m pytest

lint:
	@echo "${CYAN}Running linter...${NC}"
	$(PYTHON_VENV) -m flake8 backend/src
	$(PYTHON_VENV) -m mypy backend/src

format:
	@echo "${CYAN}Formatting code...${NC}"
	$(PYTHON_VENV) -m black backend/src
	$(PYTHON_VENV) -m isort backend/src

# Installation commands
install-dev:
	@echo "${CYAN}Installing development dependencies...${NC}"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements_local.txt
	$(PIP) install pytest flake8 mypy black isort
	@echo "${GREEN}Development dependencies installed!${NC}"

install-prod:
	@echo "${CYAN}Installing production dependencies...${NC}"
	$(PIP) install -r requirements.txt
	@echo "${GREEN}Production dependencies installed!${NC}"

# Add any additional commands specific to your project here
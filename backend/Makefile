# Makefile for Food Delivery Microservices

.PHONY: help up down logs build clean dev seed test lint

help:
	@echo "Available commands:"
	@echo "  make up        - Start all services with Docker Compose"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - View logs from all services"
	@echo "  make build     - Build all Docker images"
	@echo "  make clean     - Remove all containers, volumes, and images"
	@echo "  make dev       - Start only infrastructure (DB, Redis) for local dev"
	@echo "  make seed      - Seed database with test data"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linters"

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build

clean:
	docker-compose down -v --rmi all --remove-orphans

dev:
	docker-compose -f docker-compose.dev.yml up -d

seed:
	python -m scripts.seed_data

test:
	pytest tests/ -v

lint:
	ruff check .
	black --check .

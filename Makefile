.PHONY: help setup run stop clean test lint

help:
	@echo "Available commands:"
	@echo "  make setup    - Initial setup"
	@echo "  make run      - Start all services"
	@echo "  make stop     - Stop all services"
	@echo "  make clean    - Clean up data"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linting"

setup:
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	docker-compose pull
	@echo "Setup complete! Don't forget to copy .env.example to .env"

run:
	docker-compose up -d
	@echo "Services starting... Check http://localhost:9000 for MinIO"

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf data/*

test:
	pytest tests/

lint:
	black src/
	flake8 src/
	mypy src/
include .config
include .env

lint:
	black . --line-length 120 --exclude=${DEPENDENCIES_PATH}
	isort .
	ruff --exclude=${DEPENDENCIES_PATH} .

test:
	pytest -svv

build:
	docker compose build

build-and-start:
	docker compose up --build

start:
	docker compose up

start-detached:
	docker compose up -d

stop:
	docker compose down
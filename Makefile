# Loading environment variables
ifneq (,$(wildcard ./.env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

dev_requirements:
	poetry export --dev -f requirements.txt --output requirements_dev.txt --without-hashes

run_pipeline:
	~/.local/bin/poetry run kedro run --pipeline=data

start_bot:
	make requirements
	docker compose up --build -d

stop_bot:
	docker compose down

restart_bot:
	make stop_bot
	make start_bot
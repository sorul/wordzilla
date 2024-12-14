# Loading environment variables
ifneq (,$(wildcard ./.env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

run_pipeline:
	~/.local/bin/poetry run kedro run --pipeline=data

start_bot:
	~/.local/bin/poetry run python src/wordzilla/telegrambot.py
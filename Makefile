.PHONY: install test run docker-up

install:
	pip install -r requirements.txt

test:
	pytest -v

run:
	uvicorn app.main:app --reload

docker-up:
	docker compose up --build

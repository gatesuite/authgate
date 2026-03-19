.PHONY: dev run docker-up docker-down docker-logs clean

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-up:
	cd deployments/docker-compose && docker compose up --build -d

docker-down:
	cd deployments/docker-compose && docker compose down

docker-logs:
	cd deployments/docker-compose && docker compose logs -f authgate

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: install install-dev run test lint format docker-up docker-down clean

install:
	pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

install-dev:
	pip install -r requirements-dev.txt -i https://mirrors.aliyun.com/pypi/simple/

run:
	python manage.py

test:
	pytest --cov=app --cov-report=term-missing

lint:
	flake8 app/ tests/
	isort --check-only app/ tests/

format:
	black app/ tests/
	isort app/ tests/

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

migrate:
	flask db upgrade

migrate-init:
	flask db init
	flask db migrate -m "initial"
	flask db upgrade

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

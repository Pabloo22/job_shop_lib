lint:
	poetry run flake8
	poetry run mypy

test:
	poetry run pytest --cov=job_shop_lib --cov-report lcov:lcov.info

poetry_install_all:
	poetry install --with notebooks --with test --with lint

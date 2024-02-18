lint:
	poetry run flake8
	poetry run mypy

poetry_install_all:
	poetry install --with notebooks --with test --with lint

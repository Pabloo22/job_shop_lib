lint:
	poetry run flake8
	poetry run mypy

test:
	poetry run pytest --cov=job_shop_lib --cov-report lcov:lcov.info  --mpl

poetry_install_all:
	poetry install --with notebooks --with test --with lint --with docs --all-extras

html_docs:
	cd docs && make html

clean_docs:
	cd docs && make clean

claude_engineer:
	poetry run python claude_engineer.py

# Contributing to This Project

Thank you for your interest in contributing to our project! We value the contributions of each community member and want to make the contribution process as smooth as possible.

## Before You Start

- **For significant changes**: Please create an issue first to discuss the proposed changes. This helps prevent duplicate work and ensures your contribution aligns with the project's direction.
- **For minor changes** (like fixing typos, small bug fixes): Feel free to submit a pull request directly.

## Development Process

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Write or update tests (we use pytest)
5. Ensure all tests pass
6. Run the linting checks
7. Submit a pull request

## Setting Up Your Development Environment

This project uses [Poetry](https://python-poetry.org/) for dependency management. Follow these steps to set up your development environment:

1. Install Poetry following the [official instructions](https://python-poetry.org/docs/#installation)
2. Clone your forked repository
3. Navigate to the project root directory
4. Install all dependencies with:
   ```
   make poetry_install_all
   ```
   or
   ```
   poetry install --with notebooks --with test --with lint --with docs --all-extras
   ```

## Available Make Commands

The project includes several helpful commands in the Makefile:

- `make lint` - Run flake8 and mypy linters to check code quality
- `make test` - Run pytest with coverage reporting
- `make poetry_install_all` - Install all project dependencies including development dependencies
- `make html_docs` - Generate HTML documentation
- `make clean_docs` - Clean the documentation build directory

## Testing

- All new features should include appropriate tests using pytest
- Ensure all existing tests pass before submitting your PR
- Run tests with `pytest` in the project root

## Code Style

- We use **Black** with line length of 79 characters for code formatting
- Follow the **Google Style Guide** for docstrings
- Include docstrings for all new functions and classes
- Keep your changes focused on the specific issue/feature at hand

## Pull Request Process

1. Update the README.md or documentation with details of changes if needed
2. Update the pyproject.toml if you've added dependencies
3. Your PR will be reviewed by maintainers, who may request changes
4. Once approved, your PR will be merged

## Getting Help

If you need assistance or have questions about your contribution, you can:

- Comment on the related issue
- Contact Pablo Ariño directly at pablo.arino22@gmail.com to schedule a call to discuss your contribution

## Code of Conduct

- Be respectful and inclusive in your interactions
- Constructive criticism is welcome, but be kind
- Focus on what is best for the community and project

Thank you for contributing!

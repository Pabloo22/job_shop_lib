# Contributing to This Project

Thank you for your interest in contributing to our project! I (Pablo Ariño) started this project as part of my bachelor's thesis, which it's already finished (see README.md file for a link to it). Right now, I plan on publishing a paper about the RL environments to a software journal. Version 2 will refactor these environments to make it easier to use. However, this project depends mainly on you, the community, to keep it alive and improve it. I'll do my best to help you with your contributions. Any contribution is welcome, whether it's a small bug or documentation fix or a new feature.

## Before You Start

- **For significant changes**: Please create an issue first to discuss the proposed changes. This helps prevent duplicate work and ensures your contribution aligns with the project's direction. This type of changes include adding new features, refactoring the code, changes to the style of the code, changes to the documentation other than typos, wording, or small mistakes.
- **For minor changes** (like fixing typos, small bug fixes): Feel free to submit a pull request directly. If in doubt, it's always better to open a new issue! I always try to answer ASAP.

## Development Process

1. Fork the repository
2. Create a new branch for your feature or fix
3. Make your changes, including writing or updating tests (we use `pytest`). Commit messages must follow the guideline below.
4. Ensure all tests pass (`make test`)
5. Run the linting checks (`make lint`)
6. Check for issues with the documentation formatting (`make html_docs` and open the generated HTML files in your browser)
7. Submit a pull request. It must contain a clear description of the changes and reference any related issues

## Commit Messages

The structure of a commit should be the following:

```
[Label] BREAKING CHANGE: Short description under 50 characters (#N)

A more detailed description if needed. This body must begin one blank line after
the description and should mention the specific changes and the reasoning behind them.
This body is free-form.
```

Some considerations:

- "BREAKING CHANGE:" This should be added if the commit contains changes that break the backward compatibility of the code. Introducing
  this type of changes require updating the major version of the library. This shouldn't be done in the same commit though. Typically,
  major versions will be worked on inside their own branch (i.e, v2.0.0), and once all the changes are made, the major version is updated and the
  changes merged. Don't introduce breaking changes without prior confirmation from a library maintainer.
- Here, "#N" makes reference to the specific issue that the commit solves. This is important to quickly identify the commits that
  solved a specific issue.

### Commit labels

We prefix commit messages with one the following labels written between brackets:

- "[Feature]": For adding a specific, identifiable part of the code that provides a particular function or capability of the software.
- "[BugFix]": For commits that solve an error or flaw in the code that causes it to behave in an unintended or incorrect way.
- "[Refactor]": Refactoring is the process of restructuring existing code, altering its internal structure without changing its external behavior. However, code refactoring aimed to solve linting problems exclusively shouldn't use this label, but "[Lint]".
- "[CI]": For adding or updating files related to continous integration aspects. This includes modifying files in the `.github` folder or the `.readthedocs.yaml` file.
- "[Chore]": Used when updating the dependencies, the version of the library, or modifying files that are not related to either code or documentation. Those files include: `.gitignore`, `.flake8`, `.pylintrc`, `Makefile`, `poetry.lock`, `pyproject.toml`.
- "[Docs]": For changes related to the documentation of the project. This includes updating: files in the `docs` folder, the `README.md` and `CONTRIBUTING.md` files, and docstrings.
- "[Lint]": When addressing problems raised by mypy, flake8, pylint, or other linters. If the change is not an error or a warning raised by a linter, then it's consider refactoring.

If a commit contains changes that may fall in more than one of the above labels, two options are possible:

1. Use the label with the highest priority. The above list of labels is written in order of priority (Feature > BugFix > Refactor > CI > Chore > Docs > Lint). For example, if a commit adds a new function (a feature), it's also expected to contain tests and documentation for it. Thus, in this case, it's recommended to simply use the "[Feature]" label.
2. Combine two labels using "+". Needing to do this is a sign that changes could be better splitted into two different commits. However, if you consider them to be highly related and want to emphasize that two or more types of changes were made, you can use the "+" to combine more than one feature inside the brackets. For example, if there is a bug with the documentation, it would be reasonable to use "[BugFix + Docs]". Similarly, if a bugfix, requires a significant refactoring, "[BugFix + Refactor]" could be used.

## Setting Up Your Development Environment

This project uses [Poetry](https://python-poetry.org/) for dependency management. Follow these steps to set up your development environment:

1. Install Poetry following the [official instructions](https://python-poetry.org/docs/#installation). We use Poetry version ^1.7
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

## Code Style

- We use **Black** with line length of 79 characters for code formatting
- Include docstrings for all new functions and classes. Follow the [**Google Style Guide**](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) for docstrings, but check the existing code's style. Some discrepancies with this guide may exist to comply with `sphinx` (e.g., classes' docstring contain `__init__`'s arguments)
- Keep your changes focused on the specific issue/feature at hand

## Pull Request Process

1. Update the `README.md` or documentation with details of changes if needed
2. Update the `pyproject.toml` and `poetry.lock` if you've added dependencies
3. Your PR will be reviewed by maintainers, who may request changes
4. Once approved, your PR will be merged

## Getting Help

If you need assistance or have questions about your contribution, you can:

- Comment on the related issue
- Contact Pablo Ariño directly at pablo.arino22@gmail.com to schedule a call to discuss your contribution

## Code of Conduct

- Be respectful and inclusive in your interactions
- Constructive criticism is welcome, but be kind

Thank you for contributing!

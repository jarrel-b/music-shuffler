.DEFAULT_GOAL := help

.PHONY: help

help: ## Show help for commands.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

flake: ## Run style guide checks.
	flake8 .

black: ## Run code formatting.
	black .

black-diff: ## Create diff of code formatting and display on stdout without modifying files.
	black --check --diff .

coverage: ## Display code coverage results.
	coverage xml
	coverage report -m --skip-covered

isort: ## Sort import definitions.
	isort -rc .

isort-diff: ## Create diff of import sorting and display on stdout without modifying files.
	isort -rc . --diff --check-only

pylint: ## Check that project satifies a coding standard.
	pylint music_shuffler

mypy: ## Run type checking.
	find . -name '*.py' | xargs mypy --ignore-missing-imports

format: isort black ## Run code formatting and import sorting.

test: black-diff isort-diff flake mypy ## Run tests on the project.
	coverage run --source=. -m pytest . -v

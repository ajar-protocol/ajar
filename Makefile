.PHONY: validate examples links markdown

PYTHON ?= python3

validate: examples links markdown

examples:
	$(PYTHON) tools/validate_examples.py

links:
	$(PYTHON) tools/check_links.py

markdown:
	$(PYTHON) tools/check_markdown.py

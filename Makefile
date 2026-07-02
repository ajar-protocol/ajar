.PHONY: validate examples links markdown phase0

PYTHON ?= python3

validate: examples links markdown

phase0:
	$(PYTHON) tools/check_phase0.py

examples:
	$(PYTHON) tools/validate_examples.py

links:
	$(PYTHON) tools/check_links.py

markdown:
	$(PYTHON) tools/check_markdown.py

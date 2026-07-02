.PHONY: validate examples must links markdown phase0 manifest-check

PYTHON ?= python3

validate: examples must links markdown

phase0:
	$(PYTHON) tools/check_phase0.py

manifest-check:
	$(PYTHON) tools/manifest_check.py examples/manifests/blog-core.json --served-path /.well-known/ajar.json

examples:
	$(PYTHON) tools/validate_examples.py

must:
	$(PYTHON) tools/check_must_coverage.py

links:
	$(PYTHON) tools/check_links.py

markdown:
	$(PYTHON) tools/check_markdown.py

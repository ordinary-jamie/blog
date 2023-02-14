DATA_DIR := data/
ASSETS_SRC_DIR := src/assets/
PUBLIC_DIR := public/

blog:
	python -m pymd --data $(DATA_DIR)blog --output $(ASSETS_SRC_DIR)content --static $(PUBLIC_DIR)assets

mdbook-python-tutorial:
	mdbook build $(DATA_DIR)mdbook-python-tutorial --dest-dir ../../$(PUBLIC_DIR)books/python

local: blog mdbook-python-tutorial
	npm run dev

.PHONY: blog mdbook-python-tutorial local
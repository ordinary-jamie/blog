# Jamie's Blog

## Local development

``` bash
# Setup
npm install
pip install -r pymd/requirements.in

# Generate HTML content from markdown
python -m pymd --data data --output src/assets --post-ext md

# Serve locally
npm run dev
```


## Dev notes


### `<h1>` only for page headings

- Only use `<h1>` for page headings since the `@apply` directive is set at the base layer for this element.

## Todo

- Pagination
- Post date, tags, section meta info on post page
- Push to router query params on filter select
- Clickable section/tags on post listing
- Clear filters
- Multi-select for Tags
- Static files
- Pre-processor macros (python `md` extensions)
    - Figures
    - Citations
    - TLDR
    - Blockquotes
    - Callouts (info)
- Re-skin manual coloring
    - `dev/8`
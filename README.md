# Jamie's Blog

## Local development

``` bash
# Setup
npm install
pip install -r requirements.in

# Generate HTML content from markdown
python gen.py --data data --output src/assets --post-ext md

# Serve locally
npm run dev
```


## Dev notes


### `<h1>` only for page headings

- Only use `<h1>` for page headings since the `@apply` directive is set at the base layer for this element.
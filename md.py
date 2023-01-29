import htmlmin
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension


def convert_markdown_to_html(text: str) -> str:
    return htmlmin.minify(markdown.markdown(
        text,
        extensions=[
            "tables",
            FencedCodeExtension(),
        ],
    ))

import re
import xml.etree.ElementTree as etree

import htmlmin
import markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor

RE_KEY_VALUE_PARSER = re.compile(
    r"(?P<key>[^,]*?)\s*=\s*(\"|')(?P<value>[^,]*?)(\"|')",
)

MUNGED_COMMENT_PLACEHOLDER = "UXcjPMN4vAuwqQKs3Y"


def get_kv_pairs(text: str) -> dict[str, str]:
    if not text:
        return {}
    _mch = RE_KEY_VALUE_PARSER.finditer(text)
    return (
        {mch.group("key").strip(): mch.group("value").strip() for mch in _mch}
        if _mch
        else {}
    )


def get_div_pattern(class_name: str) -> str:
    return rf"<div class=('|\"){class_name}('|\")>\s*(?P<body>.*)\s*</div>"


class CommentMungerExtension(markdown.Extension):
    class Preprocessor(Preprocessor):
        custom_comments_ptrn = re.compile(r"^<!--% (.*) %-->$")

        def run(self, lines):
            return list(
                map(
                    lambda ln: self.custom_comments_ptrn.sub(
                        MUNGED_COMMENT_PLACEHOLDER
                        + r"\g<1>"
                        + MUNGED_COMMENT_PLACEHOLDER,
                        ln,
                    ),
                    lines,
                )
            )

    def extendMarkdown(self, md):
        md.preprocessors.register(self.Preprocessor(), "ext-comment-munger", 175)


class RelativeStaticFilesExtension(markdown.Extension):
    """Modify all relative path references

    Args:
        static_path_prefix (str): Prefix path for dst static files
    """

    def __init__(self, *args, static_path_prefix: str = "", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.static_path_prefix = static_path_prefix

    class Preprocessor(Preprocessor):

        ref_ptrn = re.compile(r"\[(?P<txt>.*)\]\(\./(?P<relPath>.*)\)")

        def __init__(self, *args, static_path_prefix: str = "", **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.static_path_prefix = static_path_prefix.rstrip("/")

        def run(self, lines):
            return list(
                map(
                    lambda ln: self.ref_ptrn.sub(
                        r"[\g<txt>](" + self.static_path_prefix + r"/\g<relPath>)", ln
                    ),
                    lines,
                )
            )

    def extendMarkdown(self, md):
        md.preprocessors.register(
            self.Preprocessor(static_path_prefix=self.static_path_prefix),
            "ext-img-preprocess",
            175,
        )


def extension_with_comment_modifiers(name: str, pattern: str):
    def _decorator(fn) -> markdown.Extension:
        class Extension(markdown.Extension):
            class Processor(InlineProcessor):
                def handleMatch(self, m, data):

                    opts = (
                        get_kv_pairs(
                            re.sub(MUNGED_COMMENT_PLACEHOLDER, "", m.group("config"))
                        )
                        if m.group("config")
                        else {}
                    )
                    return fn(m, opts), m.start(0), m.end(0)

            def extendMarkdown(self, md):
                md.inlinePatterns.register(
                    self.Processor(
                        rf"{pattern}(\s*{MUNGED_COMMENT_PLACEHOLDER}(?P<config>.*){MUNGED_COMMENT_PLACEHOLDER})?"
                    ),
                    f"ext-{name}",
                    175,
                )

        Extension.__name__ = f"{name.title}Extension"
        return Extension

    return _decorator


@extension_with_comment_modifiers("image", r"!\[(?P<altxt>.*?)\]\((?P<path>.*?)\)")
def ImageExtension(m, opts):
    el = etree.Element("div", attrib={"class": "ext-image"})
    img = etree.Element("img", attrib={"alt": m.group("altxt"), "src": m.group("path")})
    el.append(img)

    if opts.get("caption"):
        caption = etree.Element("span", attrib={"class": "ext-image-caption"})
        caption.text = opts.get("caption")
        el.append(caption)

    return el


@extension_with_comment_modifiers("note", r"!note{\s*(?P<body>.*)\s*}")
def CalloutNoteExtension(m, opts):
    el = etree.Element("div", attrib={"class": "ext-callout-note"})
    label = etree.Element("span", attrib={"class": "ext-callout-note-label"})
    label.text = "Note."
    el.append(label)

    for line in filter(lambda s: s != "", map(str.strip, m.group("body").split("\n"))):
        p = etree.Element("p")
        p.text = line
        el.append(p)

    return el


@extension_with_comment_modifiers("tldr", r"!tldr{\s*(?P<body>.*)\s*}")
def TldrExtension(m, opts):
    el = etree.Element("div", attrib={"class": "ext-tldr"})
    label = etree.Element("span", attrib={"class": "ext-tldr-label"})
    label.text = "TLDR."
    el.append(label)

    p = etree.Element("p")
    p.text = re.sub(r"\s+", " ", m.group("body"))
    el.append(p)

    return el


@extension_with_comment_modifiers("quote", r"!quote{\s*(?P<body>.*)\s*}")
def QuoteExtension(m, opts):
    url = opts.get("src")
    author = opts.get("author")

    el = etree.Element("div", attrib={"class": "ext-quote"})

    authorEl = etree.Element("span", attrib={"class": "ext-quote-author"})
    if url and author:
        a = etree.Element("a", attrib={"href": url})
        a.text = author
        authorEl.append(a)
    elif url or author:
        p = etree.Element("p")
        p.text = author if author else url
        authorEl.append(p)

    el.append(authorEl)

    p = etree.Element("p")
    p.text = re.sub(r"\s+", " ", m.group("body"))
    el.append(p)

    return el


def convert_markdown_to_html(text: str, static_path_prefix: str = "assets") -> str:
    return htmlmin.minify(
        markdown.markdown(
            text,
            extensions=[
                RelativeStaticFilesExtension(static_path_prefix=static_path_prefix),
                CommentMungerExtension(),
                "tables",
                FencedCodeExtension(),
                TocExtension(title="Contents"),
                CalloutNoteExtension(),
                TldrExtension(),
                QuoteExtension(),
                ImageExtension(),
            ],
        )
    )

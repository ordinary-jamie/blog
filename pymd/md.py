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
    return {mch.group("key"): mch.group("value") for mch in _mch} if _mch else {}


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


class ImageExtension(markdown.Extension):
    """Image with options.

    Note that this extension requires the comment munger pre-processor too.

    Usage:
        ![alternate text](image path)
        <!--% caption="some caption" src="https://...." %-->

    Outputs:
        <div class="ext-callout-note">
            <span class="ext-callout-note-label">Note.</span>
            <p>note as callout</p>
        </div>
    """

    class Processor(InlineProcessor):
        def handleMatch(self, m, data):
            opts = get_kv_pairs(m.group("config"))

            el = etree.Element("div", attrib={"class": "ext-image"})
            img = etree.Element(
                "img", attrib={"alt": m.group("altxt"), "src": m.group("path")}
            )
            el.append(img)

            if opts.get("caption"):
                caption = etree.Element("span", attrib={"class": "ext-image-caption"})
                caption.text = opts.get("caption")
                el.append(caption)

            return el, m.start(0), m.end(0)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            self.Processor(
                r"!\[(?P<altxt>.*?)\]\((?P<path>.*?)\)\s*"
                + MUNGED_COMMENT_PLACEHOLDER
                + r"?(?P<config>.*?)?"
                + MUNGED_COMMENT_PLACEHOLDER
                + "?",
                md,
            ),
            "ext-callout-note",
            175,
        )


class CalloutNoteExtension(markdown.Extension):
    """Callout notes

    Usage:
        !note{
            note as callout
        }

    Outputs:
        <div class="ext-callout-note">
            <span class="ext-callout-note-label">Note.</span>
            <p>note as callout</p>
        </div>
    """

    class Processor(InlineProcessor):
        def handleMatch(self, m, data):
            el = etree.Element("div", attrib={"class": "ext-callout-note"})
            label = etree.Element("span", attrib={"class": "ext-callout-note-label"})
            label.text = "Note."
            el.append(label)

            for line in filter(
                lambda s: s != "", map(str.strip, m.group("text").split("\n"))
            ):
                p = etree.Element("p")
                p.text = line
                el.append(p)

            return el, m.start(0), m.end(0)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            self.Processor(r"!note{(?P<text>(.|\n)*?)}", md),
            "ext-callout-note",
            175,
        )


class QuoteExtension(markdown.Extension):
    """Quotes

    Usage:
        !quote[src="https://www.google.com", author="Albert Einstein"]{
            Some quote
        }

    Outputs:
        <div class="ext-quote">
            <span class="ext-quote-author"><a href="https://www.google.com">Albert Einstein</a></span>
            <p>Some quote</p>
        </div>
    """

    class Processor(InlineProcessor):
        def handleMatch(self, m, data):

            opts = get_kv_pairs(m.group("opts"))
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
            p.text = re.sub(r"\s+", " ", m.group("text"))
            el.append(p)

            return el, m.start(0), m.end(0)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            self.Processor(r"!quote(\[(?P<opts>.*?)\])?{(?P<text>(.|\n)*?)}", md),
            "ext-quote",
            175,
        )


class TldrExtension(markdown.Extension):
    """TLDR

    Usage:
        !tldr{
            TL;DR
        }

    Outputs:
        <div class="ext-tldr">
            <span class="ext-tldr-label">Note.</span>
            <p>TL;DR</p>
        </div>
    """

    class Processor(InlineProcessor):
        def handleMatch(self, m, data):
            el = etree.Element("div", attrib={"class": "ext-tldr"})
            label = etree.Element("span", attrib={"class": "ext-tldr-label"})
            label.text = "TLDR."
            el.append(label)

            p = etree.Element("p")
            p.text = re.sub(r"\s+", " ", m.group("text"))
            el.append(p)

            return el, m.start(0), m.end(0)

    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            self.Processor(r"!tldr{(?P<text>(.|\n)*?)}", md),
            "ext-tldr",
            175,
        )


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

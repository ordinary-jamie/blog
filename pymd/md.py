import re
import xml.etree.ElementTree as etree

import htmlmin
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension
from markdown.inlinepatterns import InlineProcessor

RE_KEY_VALUE_PARSER = re.compile(
    r"(\s*(?P<key>[^,]*?)\s*=\s*(\"|')(?P<value>[^,]*?)(\"|')\s*)+",
)


def get_kv_pairs(text: str) -> dict[str, str]:
    return {
        mch.group("key"): mch.group("value")
        for mch in RE_KEY_VALUE_PARSER.finditer(text)
    }


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


def convert_markdown_to_html(text: str) -> str:
    return htmlmin.minify(
        markdown.markdown(
            text,
            extensions=[
                "tables",
                FencedCodeExtension(),
                TocExtension(title="Contents"),
                CalloutNoteExtension(),
                TldrExtension(),
                QuoteExtension(),
            ],
        )
    )

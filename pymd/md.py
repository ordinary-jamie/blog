import xml.etree.ElementTree as etree

import htmlmin
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension
from markdown.inlinepatterns import InlineProcessor


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


def convert_markdown_to_html(text: str) -> str:
    return htmlmin.minify(
        markdown.markdown(
            text,
            extensions=[
                "tables",
                FencedCodeExtension(),
                TocExtension(title="Contents"),
                CalloutNoteExtension(),
            ],
        )
    )

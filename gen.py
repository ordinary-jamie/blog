import collections
import datetime
import json
import re
from pathlib import Path

import click
import yaml
from attrs import define, field
from pydantic import BaseModel, validator
from slugify import slugify

import md


def format_tag(in_tag: str) -> str:
    return slugify(in_tag)


class FrontMatter(BaseModel):
    id: int
    title: str
    date: datetime.date
    preview: str
    section: str
    tags: list[str]
    draft: bool = True

    @property
    def ref(self):
        return f"{self.section}/{self.id}"

    @validator("title", "preview")
    def normalise(cls, v):
        v = v.strip()
        v = v[0].upper() + v[1:]
        if not v.endswith("."):
            v += "."
        return v

    @validator("preview")
    def strip_preview(cls, v):
        return v.strip()

    @validator("section", "tags", each_item=True)
    def clean_tags(cls, v):
        v = v.strip()
        assert v != "", "Tag cannot be empty"
        return format_tag(v)

    def as_dict(self) -> dict[str, str]:
        return dict(
            ref=self.ref,
            title=self.title,
            preview=self.preview,
            date=self.date.isoformat(),
            section=self.section,
            tags=self.tags,
        )


@define
class Post:

    _RE_MD_POST_FORMAT = re.compile(
        r"^\s*?-{3}\s+?(?P<frontmatter>(.|\s)*?)\s*?-{3}\s*?(?P<body>(.|\s)*)$"
    )

    source: Path
    front_matter: FrontMatter
    body: str

    @property
    def ref(self) -> str:
        return self.front_matter.ref

    @property
    def tags(self) -> list[str]:
        return self.front_matter.tags

    @property
    def section(self) -> str:
        return self.front_matter.section

    @property
    def should_publish(self) -> bool:
        return not self.front_matter.draft

    def html_path(self, base_path: Path = Path(".")) -> Path:
        return base_path / self.front_matter.section / f"{self.front_matter.id}.html"

    @classmethod
    def from_md(cls, md_file: Path) -> "Post":
        with md_file.open("r") as fd:
            raw = fd.read()

        mch = cls._RE_MD_POST_FORMAT.fullmatch(raw)
        if not mch:
            raise ValueError(f"Invalid post format. Could not parse {md_file}")

        try:
            front_matter = FrontMatter(**yaml.safe_load(mch.group("frontmatter")))
        except Exception as exc:
            raise ValueError(f"Failed to parse front matter from {md_file}") from exc

        # Admin control, make sure file name and front matter are consistent
        path_section = md_file.parent.name
        if path_section != front_matter.section:
            raise ValueError(
                f"Post file '{md_file}' was saved in the {path_section} directory, but the front matter suggests it should be in the {front_matter.section} directory."
            )
        path_id_mch = re.match(r"(?P<id>\d*).*", md_file.name)
        if not path_id_mch:
            raise ValueError(
                f"Post file '{md_file}' name is not correctly labelled with an identifier prefix. Please rename and try again."
            )

        if (path_id := int(path_id_mch.group("id"))) != front_matter.id:
            raise ValueError(
                f"Post '{md_file}' front matter requires an ID={front_matter.id} but file name is prefixed with {path_id}."
            )

        return cls(
            source=md_file,
            front_matter=front_matter,
            body=mch.group("body"),
        )

    def build(self, output_dir: Path):

        output_file = self.html_path(base_path=output_dir)
        if not output_file.parent.exists():
            output_file.parent.mkdir(parents=True)

        with output_file.open("w") as fd:
            fd.write(md.convert_markdown_to_html(f"# {self.front_matter.title}\n" + self.body))


@define
class TagMap:

    tag_to_refs: dict[str, list[str]] = field(
        factory=lambda: collections.defaultdict(list)
    )
    section_to_refs: dict[str, list[str]] = field(
        factory=lambda: collections.defaultdict(list)
    )

    def add_post(self, post: Post):
        for tag in map(format_tag, post.tags):
            if post.ref not in self.tag_to_refs[tag]:
                self.tag_to_refs[tag].append(post.ref)

        if post.ref not in self.section_to_refs[post.section]:
            self.section_to_refs[post.section].append(post.ref)


@click.command()
@click.option(
    "--data",
    "data_dir",
    type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path),
    default=Path("./data"),
    help="Source of post files",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(writable=True, path_type=Path),
    default=Path("./data_out"),
    help="Output HTML location",
)
@click.option(
    "--post-ext",
    "post_ext",
    type=str,
    default="md",
    help="Post file extension (without dot)",
)
def cli(data_dir: Path, output_dir: Path, post_ext: str):

    tag_map = TagMap()
    post_listing = []

    for ff in data_dir.glob(f"**/*.{post_ext}"):
        post = Post.from_md(ff)
        if post.should_publish:
            post.build(output_dir)
            tag_map.add_post(post)
            post_listing.append(post.front_matter.as_dict())

    post_listing.sort(key=lambda p: p["date"], reverse=True)

    with (output_dir / "meta.json").open("w") as fd:
        json.dump(
            dict(
                posts=post_listing,
                tagRefs=tag_map.tag_to_refs,
                sectionRefs=tag_map.section_to_refs,
            ),
            fd,
            indent=4,
        )


if __name__ == "__main__":
    cli()

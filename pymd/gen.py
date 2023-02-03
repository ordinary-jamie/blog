import collections
import json
import re
import shutil
from pathlib import Path

import click
import yaml
from attrs import define

from pymd.frontmatter import FrontMatter


@define
class Post:

    _RE_MD_POST_FORMAT = re.compile(
        r"^\s*?-{3}\s+?(?P<frontmatter>(.|\s)*?)\s*?-{3}\s*?(?P<body>(.|\s)*)$"
    )

    source: Path
    front_matter: FrontMatter
    body: str

    @classmethod
    def from_md(cls, md_file: Path) -> "Post":
        with md_file.open("r") as fd:
            raw = fd.read()

        mch = cls._RE_MD_POST_FORMAT.fullmatch(raw)
        if not mch:
            raise ValueError(f"Invalid post format. Could not parse {md_file}")

        try:
            front_matter = FrontMatter.parse_obj(
                yaml.safe_load(mch.group("frontmatter"))
            ).__root__
        except Exception as exc:
            raise ValueError(f"Failed to parse front matter from {md_file}") from exc

        front_matter.check_against_source(md_file)

        return cls(
            source=md_file,
            front_matter=front_matter,
            body=mch.group("body"),
        )

    def publish_and_build_meta_dict(self, output_dir: Path, meta: dict = {}) -> dict:

        if self.front_matter.should_publish:
            output_file = self.front_matter.get_asset_path(base_path=output_dir)
            if not output_file.parent.exists():
                output_file.parent.mkdir(parents=True)

            with output_file.open("w") as fd:
                fd.write(self.front_matter.render(self.body))

            self.front_matter.update_meta(meta)


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
    default=Path("./tmp"),
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

    if output_dir.exists():
        shutil.rmtree(output_dir)

    meta = {}
    for ff in data_dir.glob(f"**/*.{post_ext}"):
        Post.from_md(ff).publish_and_build_meta_dict(
            output_dir=output_dir,
            meta=meta,
        )

    with (output_dir / "meta.json").open("w") as fd:
        json.dump(meta, fd, indent=4)

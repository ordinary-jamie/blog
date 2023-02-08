import abc
import collections
import re
import typing
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, validator
from slugify import slugify

import pymd.md as md


class _FrontMatterBaseModel(BaseModel):
    date: date
    draft: bool = True

    @property
    def should_publish(self) -> bool:
        return not self.draft

    @abc.abstractmethod
    def check_against_source(self, source: Path) -> None:
        """Validate the front matter is consistent with the source file.

        This method is important for code maintenance.

        Args:
            source (Path): Origin file of the front matter
        """
        ...

    @abc.abstractmethod
    def get_asset_path(self, base_path: Path = Path(".")) -> Path:
        """The path to the rendered asset

        Args:
            base_path (Path, optional): The base path of all assets.
                Defaults to Path(".").

        Returns:
            Path: The path to the rendered asset
        """
        ...

    @abc.abstractmethod
    def update_meta(self, meta: dict) -> None:
        ...

    @abc.abstractmethod
    def render(self, body: typing.Any) -> str:
        """Render the asset into HTML string

        Args:
            body (typing.Any): Body of the post

        Returns:
            str: Rendered asset
        """
        ...


class BlogFrontMatter(_FrontMatterBaseModel):
    type: str = Field("blog", const=True)
    section: str
    id: int
    title: str
    preview: str
    tags: list[str]

    @validator("title", "preview")
    def normalise(cls, v):
        v = v.strip()
        v = v[0].upper() + v[1:]
        if not v.endswith("."):
            v += "."
        return v

    @validator("section", "tags", each_item=True)
    def slugify(cls, v):
        v = v.strip()
        assert v != "", "Tag cannot be empty"
        return slugify(v)

    def check_against_source(self, source: Path) -> None:
        # Admin control, make sure file name and front matter are consistent
        path_section = source.parent.name
        if path_section != self.section:
            raise ValueError(
                f"Post file '{source}' was saved in the {path_section} directory, but the front matter suggests it should be in the {self.section} directory."
            )
        path_id_mch = re.match(r"(?P<id>\d*).*", source.name)
        if not path_id_mch:
            raise ValueError(
                f"Post file '{source}' name is not correctly labelled with an identifier prefix. Please rename and try again."
            )

        if (path_id := int(path_id_mch.group("id"))) != self.id:
            raise ValueError(
                f"Post '{source}' front matter requires an ID={self.id} but file name is prefixed with {path_id}."
            )

    def get_asset_path(self, base_path: Path = Path(".")) -> Path:
        return base_path / self.section / f"{self.id}.html"

    def update_meta(self, meta: dict) -> None:
        if "posts" not in meta:
            meta["posts"] = []
        meta["posts"].append(
            {
                "ref": f"{self.section}/{self.id}",
                "title": self.title,
                "preview": self.preview,
                "date": self.date.isoformat(),
                "section": self.section,
                "tags": self.tags,
            }
        )

        if "tagRefs" not in meta:
            meta["tagRefs"] = collections.defaultdict(list)

        for tag in self.tags:
            meta["tagRefs"][tag].append(f"{self.section}/{self.id}")

        if "sectionRefs" not in meta:
            meta["sectionRefs"] = collections.defaultdict(list)

        meta["sectionRefs"][self.section].append(f"{self.section}/{self.id}")

    def render(self, body: typing.Any) -> str:
        return self._render_header() + md.convert_markdown_to_html(body)

    def _render_header(self) -> str:
        return f"<h1>{self.title}</h1>\n"


class AboutFrontMatter(_FrontMatterBaseModel):
    type: str = Field("about", const=True)

    def get_asset_path(self, base_path: Path = Path(".")) -> Path:
        return base_path / "about.html"

    def check_against_source(self, source: Path) -> None:
        ...

    def update_meta(self, meta: dict) -> None:
        ...

    def render(self, body: typing.Any) -> str:
        return md.convert_markdown_to_html(f"# About Me.\n" + body)


class FrontMatter(BaseModel):
    __root__: typing.Union[
        BlogFrontMatter,
        AboutFrontMatter,
    ]

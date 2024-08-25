from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Concept:
    id: int
    name: str
    description: Optional[str] = None

    @classmethod
    def from_notion_db_row(cls, row: dict) -> Concept:
        properties = row["properties"]
        id = properties["ID"]["number"]
        name = properties["Name"]["title"][0]["plain_text"]

        if properties["Description"]["rich_text"]:
            description = properties["Description"]["rich_text"][0]["plain_text"]
        else:
            description = None

        return cls(id, name, description)

    @classmethod
    def from_sqlite_db_row(cls, row: dict) -> Concept:
        id = row["concept_id"]
        name = row["name"]
        description = row["description"]
        return Concept(id, name, description)


@dataclass
class Screenshot:
    cloud_link: str

    @property
    def img_link(self) -> str:
        xxxx, yyyyyyyyy = self.cloud_link.split('/')[-2:]
        return f"https://thumb.cloud.mail.ru/weblink/thumb/xw1/{xxxx}/{yyyyyyyyy}"


@dataclass
class Info:
    concept_id: int
    type: str
    source_link: Optional[str] = None
    source_name: Optional[str] = None
    text: Optional[str] = None
    screenshot: Optional[Screenshot] = None

    @classmethod
    def from_notion_db_row(cls, row: dict) -> Info:
        properties = row["properties"]
        type = properties["Type"]["select"]["name"]
        source_link = properties["Link"]["url"]
        concept_id = properties["Concept"]["number"]

        if properties["Text"]["rich_text"]:
            text = properties["Text"]["rich_text"][0]["plain_text"]
        else:
            text = None

        if properties["Screenshot"]["url"]:
            screenshot_url = properties["Screenshot"]["url"]
            screenshot = Screenshot(screenshot_url)
        else:
            screenshot = None

        if properties["Name"]["title"]:
            source_name = properties["Name"]["title"][0]["plain_text"]
        else:
            source_name = None

        return Info(concept_id, type, source_link, source_name, text, screenshot)

    @classmethod
    def from_sqlite_db_row(cls, row: dict) -> Info:
        concept_id = row["concept_id"]
        type = row["type"]
        source_link = row["source_link"]
        source_name = row["source_name"]
        text = row["text"]
        screenshot_link = row["screenshot_link"]
        screenshot = Screenshot(screenshot_link) if screenshot_link else None
        return Info(concept_id, type, source_link, source_name, text, screenshot)

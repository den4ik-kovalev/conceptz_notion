from __future__ import annotations
from typing import Optional

from dirs import DATA
from src.models import Concept, Info
from src.utils.sqlite import SQLite


# запрос для инициализации таблиц БД
INIT_STMT = """
CREATE TABLE IF NOT EXISTS concept (
    concept_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);
CREATE TABLE IF NOT EXISTS info (
    concept_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    source_link TEXT,
    source_name TEXT,
    `text` TEXT,
    screenshot_link TEXT,
    FOREIGN KEY (concept_id) REFERENCES concept(concept_id)
);
"""


class Database(SQLite):

    @classmethod
    def instance(cls, project_name: str) -> Database:
        return Database(
            filepath=(DATA / f"{project_name}.db"),
            init_stmt=INIT_STMT
        )

    def sync(self, concepts: list[Concept], infos: list[Info]):
        with self.connection() as conn:
            conn.execute("BEGIN TRANSACTION")
            try:
                conn.execute("DELETE FROM concept")
                conn.execute("DELETE FROM info")
                for concept in concepts:
                    stmt = """
                    INSERT INTO concept(concept_id, name, description)
                    VALUES (?, ?, ?)
                    """
                    values = (concept.id, concept.name, concept.description)
                    conn.execute(stmt, values)
                for info in infos:
                    stmt = """
                    INSERT INTO info(concept_id, type, source_link, source_name, `text`, screenshot_link)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    values = (
                        info.concept_id,
                        info.type,
                        info.source_link,
                        info.source_name,
                        info.text,
                        info.screenshot.cloud_link if info.screenshot else None
                    )
                    conn.execute(stmt, values)
            except:
                conn.execute("ROLLBACK")
                raise
            else:
                conn.execute("COMMIT")

    def get_concept_by_name(self, concept_name: str) -> Optional[Concept]:
        with self.connection() as conn:
            stmt = "SELECT * FROM concept WHERE LOWER(name) = ?"
            values = (concept_name.lower(), )
            cur = conn.execute(stmt, values)
            row = cur.fetchone()
        return Concept.from_sqlite_db_row(row) if row else None

    def get_info_by_concept(self, concept_id: int) -> list[Info]:
        with self.connection() as conn:
            stmt = "SELECT * FROM info WHERE concept_id = ?"
            values = (concept_id, )
            cur = conn.execute(stmt, values)
            rows = cur.fetchall()
        return [Info.from_sqlite_db_row(row) for row in rows]

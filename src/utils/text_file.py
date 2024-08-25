from pathlib import Path
from typing import Union


class TextFile:

    def __init__(self, path: Union[str, Path], auto_create=True) -> None:
        path = Path(path)
        self._path = path
        if auto_create and not self.exists():
            self.write("")

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def read(self) -> str:
        with open(self._path, "r", encoding="utf-8") as file:
            return file.read()

    def write(self, data: str) -> None:
        with open(self._path, "w", encoding="utf-8") as file:
            file.write(data)

    def delete(self) -> None:
        self._path.unlink()

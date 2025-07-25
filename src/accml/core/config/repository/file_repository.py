import json
from pathlib import Path
from typing import List, Type, TypeVar

import yaml

from .base import Repository

T = TypeVar("T")


class FileRepository(Repository[T]):
    def __init__(self, model_cls: Type[T], path: str):
        self.model_cls = model_cls
        self.path = path

    def load(self) -> List[T]:
        ext = Path(self.path).suffix
        with open(self.path, "r") as f:
            raw = yaml.safe_load(f) if ext in [".yaml", ".yml"] else json.load(f)
        return [self.model_cls(**item) for item in raw]

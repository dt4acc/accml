from uuid import uuid4

from accml_lib.core.interfaces.utils.storage import StorageInterface


class SimpleDataStorage(StorageInterface):
    def __init__(self):
        self.data = dict()

    def add(self, data) -> str:
        uuid = uuid4()
        self.data[uuid] = data
        return uuid

    def clear(self):
        self.data.clear()

    def keys(self):
        return self.data.keys()

    def get(self, uuid: str):
        return self.data.get(uuid)

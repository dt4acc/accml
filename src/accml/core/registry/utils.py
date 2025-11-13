""" Module for registry utility functionality. """

from collections import UserDict
import fnmatch
from typing import List

class WildcardDict(UserDict):
    """
    Dictionary where keys can be found using wildcards.
    """

    def __getitem__(self, pattern: str) -> List:
        return [v for k, v in self.data.items() if fnmatch.fnmatch(str(k), pattern)]
__version__ = "0.3.0"

from .api import Data, Expression, Scoreboard
from .plugin import beet_default

__all__ = ["beet_default", "Data", "Expression", "Scoreboard"]


def __monkey_patch():
    from nbtlib import Compound, List

    def __patched_hash(self):
        return hash(str(self))

    Compound.__hash__ = __patched_hash
    List.__hash__ = __patched_hash


__monkey_patch()

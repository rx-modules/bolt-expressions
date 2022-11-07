__version__ = "0.9.0"

from .api import Data as _Data
from .api import Expression as _Expression
from .api import Scoreboard as _Scoreboard
from .plugin import beet_default

__all__ = ["beet_default", "Data", "Expression", "Scoreboard"]


def __monkey_patch():
    from nbtlib import Compound, List

    def __patched_hash(self):
        return hash(str(self))

    Compound.__hash__ = __patched_hash
    List.__hash__ = __patched_hash


__monkey_patch()

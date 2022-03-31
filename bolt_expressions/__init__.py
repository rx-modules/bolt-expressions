__version__ = "0.2.1"

from .api import Data as _Data, Expression as _Expression, Scoreboard as _Scoreboard
from .plugin import beet_default

__all__ = ["beet_default", "Data", "Expression", "Scoreboard"]

def __monkey_patch():
    from nbtlib import Compound, List

    def __patched_hash(self):
        return hash(str(self))

    Compound.__hash__ = __patched_hash
    List.__hash__ = __patched_hash


__monkey_patch()

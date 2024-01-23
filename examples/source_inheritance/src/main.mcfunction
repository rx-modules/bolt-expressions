from bolt_expressions import Scoreboard, Data, DataSource
from dataclasses import dataclass, replace
from contextlib import contextmanager


temp = Scoreboard("obj.temp")

strg = Data.storage(example:main)

@dataclass(order=False)
class ExtendedDataSource(DataSource):
    __annotations__ = {
        "_inverted": bool
    }
    _inverted = False

    @contextmanager
    def __branch__(self):
        if not self._inverted:
            if data var self:
                yield True
        else:
            unless data var self:
                yield True
    
    def __not__(self):
        return replace(self, _inverted=not self._inverted)

    def increment(self):
        self += 1


storage = ExtendedDataSource("storage", example:main, _inverted=True, ctx=ctx)

storage.b.index[0].named["! 3  - b#2a"].a({x:1}).b[{y:2}].c[] = 3

storage.value.increment()


temp["$a"] = temp["$value"] - storage.a
storage.a = temp["$a"]


if storage({a: 0}):
    say It's 0!
else:
    say It's not 0...
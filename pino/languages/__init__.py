
from . import py
from . import lua
from . import vim

languages = [py, lua, vim]

name_chars = {}
keywords = {}
for l in languages:
    if hasattr(l, "name_chars"):
        for name in l.names:
            name_chars[name] = l.name_chars
    if hasattr(l, "keywords"):
        for name in l.names:
            keywords[name] = keywords




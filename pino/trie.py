

class Trie(object):

    trie_n = 0

    __slots__ = ("parent", "tvalues", "name", "list")

    def __init__(self, levels, parent = None, name = "", level = 0):
        Trie.trie_n += 1
        levels.setdefault(level, []).append(self)

        self.parent = parent
        self.list = None
        self.tvalues = None
        self.name = name

    def node_name(self):
        s = self.name
        t = self.parent
        while t:
            s += t.name
            t = t.parent
        return s[::-1]

    #==========================================================

    def add_name(self, name, value, levels):
        # TODO merge (file_id, line)
        new = False
        root = self
        for i, char in enumerate(name):
            t = root.get(char)
            if t is None:
                t = Trie(levels, root, char, i + 1)
                root.force_set(char, t)
            root = t
        if root.tvalues is None:
            root.tvalues = [value]
            new = True
        else:
            root.tvalues.append(value)
        return new

    def get_name(self, name, real=True):
        root = self
        for char in name:
            root = root.get(char)
            if root is None:
                return None
        if not real or root.tvalues:
            return root

    def all_children(self):
        l = []
        if self.tvalues:
            l.append(self)
        for v in self.values():
            l.extend(v.all_children())
        return l

    def match_name(self, part, maxn, levels):
        l = []
        for lv in sorted(levels.keys()):
            for root in levels[lv]:
                v = root.get_name(part, False)
                if v:
                    l.extend(v.all_children())
                    if len(l) >= maxn:
                        return l
        return l

    def get(self, k, defv=None):
        if self.list is None:
            return defv
        for tk, v in self.list:
            if tk == k:
                return v
        return defv

    def force_set(self, k, v):
        if self.list is None:
            self.list = ((k, v), )
        else:
            self.list = self.list + ((k, v), )

    # unuse
    def set0(self, k, v):
        if self.list is None:
            self.list = []
        for i, (tk, _) in enumerate(self.list):
            if tk == k:
                self.list[i] = v
                break
        else:
            self.list.append((k, v))

    def values(self):
        if self.list:
            return [v for _, v in self.list]
        else:
            return []

    def keys(self):
        if self.list:
            return [k for k, _ in self.list]
        else:
            return []

    def items(self):
        if self.list:
            return [(k, v) for k, v in self.list]
        else:
            return []



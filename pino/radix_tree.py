

def pre(a, b):
    i = 0
    try:
        while a[i] == b[i]:
            i += 1
    except IndexError:
        pass
    return i

class RadixTree(object):

    n = 0

    __slots__ = ("parent", "tvalues", "list", "name")

    def __init__(self, parent, name, value):
        RadixTree.n += 1

        self.parent = parent
        self.name = name
        self.list = None
        self.tvalues = value

    def __getstate__(self):
        return {"parent": self.parent, "tvalues": self.tvalues, "name": self.name, "list": self.list}

    def __setstate__(self, state):
        self.parent = state["parent"]
        self.tvalues = state["tvalues"]
        self.name = state["name"]
        self.list = state["list"]

    def node_name(self):
        l = [self.name]
        t = self.parent
        while t:
            l.append(t.name)
            t = t.parent
        return "".join(l[::-1])

    #==========================================================

    def add_value(self, value):
        if self.tvalues is None:
            self.tvalues = (value, )
        else:
            self.tvalues += (value, )

    def add_sub(self, t):
        if self.list is None:
            self.list = (t, )
        else:
            self.list += (t, )

    def add_name(self, name, value, levels, lv = 1, pre = pre):
        if self.list is None:
            t = RadixTree(self, name, (value, ))
            self.list = (t, )
            # levels.setdefault(lv, set()).add(t)
            return 

        l = len(name)
        for t in self.list:
            p = pre(name, t.name)
            if p == 0:
                continue

            if p == l == len(t.name):
                if name == t.name:
                    t.add_value(value)
                    return 
            elif l > p and len(t.name) > p:

                new = RadixTree(self, name[:p], ())
                self.list = self.list + (new, )
                self.list = tuple(x for x in self.list if x is not t)

                t.name = t.name[p:]
                new.add_sub(t)
                t.parent = new

                # s = levels.setdefault(lv, set())
                # s.add(new)

                # def f(t, lv):
                #     levels[lv].remove(t)
                #     levels.setdefault(lv + 1, set()).add(t)
                #     if t.list is not None:
                #         for sub in t.list:
                #             f(sub, lv + 1)

                # f(t, lv)

                new.add_name(name[p:], value, levels, lv + 1)
                return 

            elif l > p:
                t.add_name(name[p:], value, levels, lv + 1)
                return 

            else:
                new = RadixTree(self, name, (value, ))
                self.list = self.list + (new, )
                self.list = tuple(x for x in self.list if x is not t)

                t.name = t.name[l:]
                new.add_sub(t)
                t.parent = new

                # s = levels.setdefault(lv, set())
                # s.add(new)

                # def f(t, lv):
                #     levels[lv].remove(t)
                #     levels.setdefault(lv + 1, set()).add(t)
                #     if t.list is not None:
                #         for sub in t.list:
                #             f(sub, lv + 1)

                # f(t, lv)
                return 

        t = RadixTree(self, name, (value, ))
        self.list = self.list + (t, )
        # levels.setdefault(lv, set()).add(t)

    def get_name(self, name):
        if self.list is None:
            return 
        l = len(name)
        for t in self.list:
            if l > len(t.name):
                if name.startswith(t.name):
                    return t.get_name(name[len(t.name):])
            elif l == len(t.name):
                if name == t.name:
                    return t
            elif t.name.startswith(name):
                return 

    def prefix(self, name, *args, **kw):
        if self.list is None:
            return 
        
        l = len(name)
        for t in self.list:
            if l > len(t.name):
                if name.startswith(t.name):
                    return t.prefix(name[len(t.name):])
            elif l == len(t.name):
                if name == t.name:
                    return t
            elif t.name.startswith(name):
                return t

    def all_children(self):
        if self.list is None:
            return [self]
        l = [self]
        for t in self.list:
            l.extend(t.all_children())
        return l

    def printf(self, lv=0):
        if self.list is None:
            return 
        for t in self.list:
            print("  " * lv + t.name + " " + str(t.tvalues), t.node_name())
            t.printf(lv + 1)

    def match(self, part, maxn, levels):
        l = []
        for lv in sorted(levels.keys()):
            for root in levels[lv]:
                v = root.prefix(part)
                if v:
                    l.extend(v.all_children())
                    if len(l) >= maxn:
                        return l
        return l

def main():
    lvs = {}

    a = RadixTree(None, "", ())
    lvs[0] = set([a])

    a.add_name("software", 1, lvs)
    a.add_name("sublicense", 1, lvs)

    a.add_name("a", 1, lvs)
    a.add_name("ab", 1, lvs)

    a.add_name("cb", 1, lvs)
    a.add_name("c", 1, lvs)

    # a.add_name("sell", 1, lvs)
    # a.add_name("so", 1, lvs)
    # a.add_name("sobject", 1, lvs)
    # a.add_name("shall", 1, lvs)
    # a.add_name("substantial", 1, lvs)
    # a.add_name("self", 1, lvs)
    # a.add_name("server", 1, lvs)
    # a.add_name("s", 1, lvs)
    # a.add_name("s", 1, lvs)
    a.printf()

    1/0

    a.add_name("abc", 1, lvs)
    a.add_name("efg", 1, lvs)
    a.add_name("efg", 2, lvs)
    a.printf()
    print
    a.add_name("mn", 1, lvs)
    a.printf()
    a.add_name("mnn", 11, lvs)
    
    a.add_name("xyz", 1, lvs)
    a.printf()
    print
    a.add_name("xy", 1, lvs)
    a.printf()
    print
    a.add_name("x", 1, lvs)
    a.add_name("server", 1, lvs)
    a.add_name("s", 1, lvs)
    a.add_name("s", 1, lvs)
    a.printf()
    print
    a.add_name("x11111111111", 1, lvs)
    a.add_name("xyzw", 1, lvs)
    from pprint import pprint
    # pprint(a.__getstate__())
    a.printf()

    # print a.get_name("x").node_name()
    # print a.get_name("xy").node_name()
    # print a.get_name("xyz").node_name()

    # for x in a.get_name("x").all_children():
    #     print x.node_name(), 999


    for x in a.match("y", 1000, lvs):
        print 88, x.node_name()
    print
    print
    print

    for x in a.match("e", 1000, lvs):
        print 81, x.node_name()

    for k, l in lvs.items():
        for v in l:
            print  k, v.node_name()

    print a.get_name("x11").node_name()

if __name__ == "__main__":
    main()


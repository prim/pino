
def uri_to_path(uri):
    if uri.startswith(r"file:///"):
        return uri[8:].replace("%3A", ":\\").replace("%5C", "\\")
    return uri

def path_to_uri(path):
    if not path.startswith(r"file:///"):
        return r"file:///" + path
    return path

def memory_profile(self, f):
    import tracemalloc
    tracemalloc.start()
    snap1 = tracemalloc.take_snapshot()
    f()
    snap2 = tracemalloc.take_snapshot()
    stat = snap2.compare_to(snap1, 'lineno')
    for x in stat[:24]:
        print(x)




from utils import uri_to_path, path_to_uri

class Document(object):

    __slots__ = ("uri", "content")

    def __init__(self, uri):
        self.uri = uri
        with open(self.path, "rb") as file:
            binary = file.read()
            try:
                self.content = binary.decode("utf8")
            except UnicodeDecodeError:
                # TODO
                self.content = ""

    def lines(self):
        b = e = 0
        lines = []
        for i, char in enumerate(self.content):
            if char == "\n":
                lines.append(self.content[b:i])
                b = e = i
        return lines

    @property
    def path(self):
        return uri_to_path(self.uri)


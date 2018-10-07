

root = Trie()
root.add_name("abchina", 1)
root.add_name("abxx", 1)
root.add_name("abxxx", 1)
root.add_name("abzxy", 1)
root.add_name("abziyx", 1)
print(root)
print(root.get_name("abchina").tvalues)
print(root.levels)
for v in root.match_name("bx"):
    print("---", v.name)

print("888")
for v in root.match_name("z"):
    print("---", v.name)
1/0

    def parse_file(self, type_, path):
        # if path != r"E:\netease\g58\server\hmt20180716\MobileServer\mobilerpc\TcpClient.py":
        #     return 
        log.debug("%s parse_file %s", self, path)
        self.file_id += 1
        file_id = self.file_id
        self.file_pathes[file_id] = path

        name_chars = languages.name_chars.get(type_, default_name_chars)
        # print(type_, name_chars, languages.name_chars.keys())
        language_keywords = languages.keywords.get(type_, default_name_chars)

        definition = self.definition
        code_index = self.code_index
        definition_setdefault = definition.setdefault
        code_index_setdefault = code_index.setdefault

        with open(path, 'rb') as rf:
            binary = rf.read()
            source = self.bytes_to_string(binary)
            if not source:
                log.debug("%s parse_file encoding error %s", self, path)
                return 
            line = 1
            word = ""
            words = set()
            count = 0
            first = ""
            for char in source:
                if char in name_chars or ord(char) > 0xff:
                    word += char
                else:
                    if word:
                        words.add(word)
                        if count == 0:
                            first = word
                        word = ""
                        count += 1

                    if char == "\n":
                        # print(line, words)
                        for t in words:
                            if t in language_keywords:
                                continue
                            if first in ("def", "class"):
                                definition_setdefault(t, set()).add((file_id, line))
                            l = code_index_setdefault(t, [])
                            for fid, flines in l:
                                if fid == file_id:
                                    flines.append(line)
                                    break
                            else:
                                l.append((file_id, [line]))

                        count = 0
                        first = ""
                        line += 1
                        words.clear()

    def parse_file(self, type_, path):
        # if path != r"E:\netease\g58\server\hmt20180716\MobileServer\mobilerpc\TcpClient.py":
        #     return 
        log.debug("%s parse_file %s", self, path)
        self.file_id += 1
        file_id = self.file_id
        self.file_pathes[file_id] = Document(path_to_uri(path))

    def get_name(self, params):
        uri = params['textDocument']['uri']
        position = params['position']
        path = uri_to_path(uri)
        _, file_extension = splitext(path)
        name_chars = languages.name_chars.get(file_extension, default_name_chars)

        content = self.get_file_content(path)

        # begin from 0
        linenum = 0
        c = 0
        word = ""
        for char in content:
            # print("--- %s %s" % (char, linenum))
            if linenum == position['line']:
                if char in name_chars or ord(char) > 0xff:
                    # print("------- %s" % word)
                    word += char
                else:
                    if c > position['character']:
                        return word
                    word = ""
            if char == "\n":
                c = 0
                linenum += 1
                word = ""
            c += 1




    def updateFile(self, fpath):
        if not self.inited: self.init_or_load()
        log.debug("%s updateFile %s", self, fpath)

        # check under my sources dict
        white_list = self.file_white_list
        black_list = self.file_black_list
        from os.path import splitext
        _, file_extension = splitext(fpath)
        if black_list and file_extension in black_list:
            log.debug("%s updateFile %s", self, fpath)
            return 
        if white_list and file_extension in white_list:
            self.parse_file(file_extension, fpath)



    def cache_file_content(self, params):
        uri = params['textDocument']['uri']
        path = uri_to_path(uri)
        old_content = self.get_file_content(path)
        for change in params["contentChanges"]:
            text = change["text"]
            range = change.get("range")
            if not range:
                self.contents[path] = text
                log.info("%s cache_file_content %s", self, path)
            # TODO

    def get_file_content(self, path):
        content = self.contents.get(path)
        if content:
            return content
        with open(path, 'rb') as rfile:
            content = rfile.read()
            content = content.decode('utf8')
            return content


    def test(self):
        for v in self.root.match_name("socket"):
            print("---", v.node_name())
            for k, v in v.tvalues:
                print("~", self.file_pathes[k], v)
        for v in self.root.match_name("server"):
            print("---", v.node_name(), v.tvalues)
            for k, v in v.tvalues:
                print("~", self.file_pathes[k], v)
        for v in self.root.match_name("http"):
            print("---", v.node_name(), v.tvalues)
            for k, v in v.tvalues:
                print("~", self.file_pathes[k], v)


    def back():
        file = open(result_file_path, "w+")
        file.write('[Search results for pattern: "%s"]\n' % pattern)
        file.write("".join(ret))
        file.close()

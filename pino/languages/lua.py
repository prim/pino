
names = [".lua"]

def _():
    return set("""
    and       break     do        else      elseif
    end       false     for       function  if
    in        local     nil       not       or
    repeat    return    then      true      until     while
""".split())

keywords = _()

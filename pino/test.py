

from core import init_project
import core

def main():
    init_project()
    print(core.projects)

    p = core.projects['py27stdlib']
    p.reinit(' ')
    p.stat()
    print(p)
    input()


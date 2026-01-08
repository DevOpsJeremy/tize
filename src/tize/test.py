from pathlib import Path
from clinit.scaffolding.builder import Builder

dir = Path("src/clinit/scaffolding/scaffolds/python")

builder = Builder(dir, tags=["ci"])
def list_paths(paths: list[Path]):
    for p in paths:
        if isinstance(p, list):
            list_paths(p)
        else:
            print(p.path)

list_paths(builder.tree)

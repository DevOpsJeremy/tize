#!/usr/bin/env python
import sys
from pathlib import Path

dest = Path(
    sys.argv[1] if len(sys.argv) > 1 else "."
).resolve()
print(dest)
exit()
import yaml
import textwrap
import re
from os import listdir
from pathlib import Path
import json

#region functions
def get_file_config(path: Path) -> dict:
    if not path.is_file():
        raise Exception(f"Invalid path: {path}. NOT a file.")
    
    config = default_config.copy()
    comment_regex = r"^(\#-{3,}scaffolding\n(?P<scaffold_config>(\#.*\n)*)\#-{3,}\n?)?(?P<content>(.*\n?)*)"
    if path.suffix in [".md", ".markdown", ".html"]:
        comment_regex = r"^(<!\-\-( *\n)*-{3,}scaffolding\n(?P<scaffold_config>(.*\n)*)-{3,}\n?(.*\n)*\-\->)?(?P<content>(.*\n?)*)"
    pattern = re.compile(
        comment_regex,
        re.MULTILINE
    )
    file_content = path.read_text()
    matches = pattern.search(file_content)
    print(f"Getting file config for: {path}")
    print(matches)
    print(matches.groupdict())
    config_text_raw = matches.group("scaffold_config")
    if not config_text_raw:
        print("No config text found, returning default config")
        return config
    config_text = config_text_raw
    if path.suffix not in [".md", ".markdown", ".html"]:
        config_text = re.sub(r"^\#", "", config_text_raw, flags=re.MULTILINE)
    print(f"Config text:\n{config_text}")
    config_text_cleaned = textwrap.dedent(config_text).strip()
    print(f"Config text cleaned:\n{config_text_cleaned}")
    try:
        file_config = yaml.safe_load(config_text_cleaned)
        print(f"Config loaded:\n{file_config}")
        merge_dicts(config, file_config)
        print(f"Config merged:\n{config}")
    except Exception as e:
        raise e
    return config

def merge_dicts(a: dict, b: dict):
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            merge_dicts(a[key], b[key])
        else:
            a[key] = b[key]
    return a

def should_process(enable_tags: list[str], item_tags: list[str], path: Path | None = None) -> bool:
    print(f"Running SHOULD_PROCESS")
    print(f"Enable tags: {enable_tags}")
    print(f"Item tags: {item_tags}")
    print(f"Path: {path}")
    if path is not None and path.is_file() and path.name == scaffold_config_file:
        print(f"NOT processing: {path.name}")
        return False

    if "all" in enable_tags or "all" in item_tags:
        print(f"processing: {path.name}")
        return True
    
    comparison = set(enable_tags) & set(item_tags)
    if len(comparison) > 0:
        print(f"processing: {path.name}")
        return True

    print(f"NOT processing: {path.name}")
    return False

def assemble_files(dir: Path, tags: list = []):
    children = []
    for i in listdir(dir):
        print(i)
        path = dir / i
        is_dir = path.is_dir()
        print(f"Path: {path}")
        print(f"Is dir: {is_dir}")
        if is_dir:
            config_path = path / scaffold_config_file
            print(f"config_path: {config_path}")
            print(f"Config exists: {config_path.exists()}")
            config_full = default_config.copy()
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print(config)
                print("Merging dicts")
                merge_dicts(config_full, config)
            print(f"Config full: {config_full}")
            if should_process(tags, config_full.get("tags", []), path):
                print(f"PROCESS Directory: {path.name}")
                nested_children = assemble_files(path, tags)
                if len(nested_children) > 0:
                    children.extend(nested_children)
                elif keep_empty_dirs:
                    children.append(path / ".gitkeep")
        else:
            print(f"File: {path.name}")
            file_config = get_file_config(path)
            if should_process(tags, file_config.get("tags", []), path):
                print(f"PROCESS File: {path.name}")
                children.append(path)
    return children
#endregion functions

#region Classes
class Scaffold: 
    def __init__(self):
        pass

class ScaffoldItem: 
    def __init__(self):
        pass

class ScaffoldConfig:
    def __init__(self):
        pass
#endregion Classes

scaffold_config_file = ".scaffolding.json"
dir = Path("src/clinit/scaffolding/scaffolds/python")
default_config_path = Path("src/clinit/scaffolding/configs/scaffold.defaults.json")
with open(default_config_path, 'r') as f:
    default_config = json.load(f)
print(f"defualt config: {default_config}")
tags = ["defaults"]
keep_empty_dirs = True

c = assemble_files(dir, tags)
print("\n---\nFinal children:\n---\n")
print(c)

for i in c:
    print(i)

print("\n\n")

for i in c:
    print(i.relative_to(dir))

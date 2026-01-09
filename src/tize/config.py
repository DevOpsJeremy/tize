from pathlib import Path
import re
import json
from tize import utils
import textwrap
import yaml

def get_file_config(path: Path) -> dict:
    default_config_path = utils.get_file("config.defaults.json")
    with open(default_config_path, 'r') as f:
        default_config = json.load(f)

    if not path.is_file():
        raise Exception(f"Invalid path: {path}. NOT a file.")
    
    config = default_config.copy()
    comment_regex = r"^(\#-{3,}tize\n(?P<scaffold_config>(\#.*\n)*)\#-{3,}\n?)?(?P<content>(.*\n?)*)"
    if path.suffix in [".md", ".markdown", ".html"]:
        comment_regex = r"^(<!\-\-( *\n)*-{3,}tize\n(?P<scaffold_config>(.*\n)*)-{3,}\n?(.*\n)*\-\->)?(?P<content>(.*\n?)*)"
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
        utils.merge_dicts(config, file_config)
        print(f"Config merged:\n{config}")
    except Exception as e:
        raise e
    return config

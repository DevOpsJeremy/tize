import os
import re
from pathlib import Path
from tize import config as tize_config


class Tree:
    def __init__(self, root: Path, tags: list = ["all"]):
        if not root.is_dir():
            raise Exception(f"Invalid path: {root}. Not a directory.")

        self.tags = tags
        children = self.get_children(root)

    def get_children(self):
        children = []
        for child in os.listdir(root):
            child_path = root / child
            config_class = tize_config.ConfigFactory.get_config_class(child_path)
            config_obj = config_class(child_path)
            # if not self.should_process(config_obj):

    def should_process(self, cfg: tize_config.Base) -> bool:
        if (
            cfg.path is not None
            and cfg.path.is_file()
            and re.match(tize_config.Directory.CONFIG_FILE_REGEX, cfg.path.name)
        ):
            return False

        if "all" in self.tags or "all" in cfg.config["tags"]:
            return True

        return True


def should_process(
    enable_tags: list[str], item_tags: list[str], path: Path | None = None
) -> bool:
    if path is not None and path.is_file() and path.name == scaffold_config_file:
        return False

    if "all" in enable_tags or "all" in item_tags:
        return True

    comparison = set(enable_tags) & set(item_tags)
    if len(comparison) > 0:
        return True

    return False


def assemble_files(dir: Path, tags: list = []):
    children = []
    for i in listdir(dir):
        path = dir / i
        is_dir = path.is_dir()
        if is_dir:
            config_path = path / scaffold_config_file
            config_full = default_config.copy()
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = json.load(f)
                merge_dicts(config_full, config)
            if should_process(tags, config_full.get("tags", []), path):
                nested_children = assemble_files(path, tags)
                if len(nested_children) > 0:
                    children.extend(nested_children)
                elif keep_empty_dirs:
                    children.append(path / ".gitkeep")
        else:
            file_config = get_file_config(path)
            if should_process(tags, file_config.get("tags", []), path):
                children.append(path)
    return children

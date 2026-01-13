import os
import re
from pathlib import Path
from tize import config as tize_config


class Tree:
    DEFAULT_TAGS = ["all"]

    def __init__(self, root: Path, tags: list = DEFAULT_TAGS):
        if not root.is_dir():
            raise Exception(f"Invalid path: {root}. Not a directory.")

        self.tags = tags
        self.children = self.get_children(root)

    def get_children(self, root: Path):
        children = []
        for child in os.listdir(root):
            child_path = root / child
            config_class = tize_config.ConfigFactory.get_config_class(child_path)
            config_obj = config_class(child_path)
            if not self.should_process(config_obj):
                continue
            if child_path.is_file():
                children.append(child_path)
                continue
            nested_children = self.get_children(child_path)
            children.extend(nested_children)
        return children

    def should_process(self, cfg: tize_config.Base) -> bool:
        if (
            cfg.path is not None
            and cfg.path.is_file()
            and re.match(tize_config.Directory.CONFIG_FILE_REGEX, cfg.path.name)
        ):
            return False

        enable_tags = self.tags
        item_tags = cfg.config.get("tags", [])

        if "all" in enable_tags or "all" in item_tags:
            return True

        comparison = set(enable_tags) & set(item_tags)
        if len(comparison) > 0:
            return True

        return False

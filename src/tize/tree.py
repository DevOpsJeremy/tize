import jinja2
import os
import re
from pathlib import Path
from tize import config as tize_config
from tize import utils


class Tree:
    DEFAULT_TAGS = ["all"]

    def __init__(self, root: Path, tags: list = DEFAULT_TAGS, env: jinja2.Environment = None):
        self.tags = tags
        self.children = self.get_children(root)

        if not env:
            env = jinja2.Environment()
            env.globals = dict(
                tags=self.tags,
                children=self.children
            )
        self.env = env

    def get_children(self, root: Path) -> list:
        cfg = tize_config.ConfigFactory.get_config_class(root)
        config_obj = cfg(root)

        children = []
        if not self.should_process(config_obj):
            return children

        if root.is_file():
            children.append(root)
            return children

        children = []
        for child in os.listdir(root):
            child_path = root / child
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

        if "all" in enable_tags:
            return True

        if cfg.path.is_file() and cfg.binary:
            if "binaries" in enable_tags:
                return True

            return False

        item_tags = cfg.config.get("tags", [])

        if "all" in item_tags:
            return True

        comparison = set(enable_tags) & set(item_tags)
        if len(comparison) > 0:
            return True

        return False

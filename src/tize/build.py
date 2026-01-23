import jinja2
import os
import re
import shutil
from pathlib import Path
from tize import config as tize_config
from tize import utils


class Tree:
    DEFAULT_TAGS = ["all"]

    def __init__(self, root: Path, tags: list = DEFAULT_TAGS, **kwargs):
        self.root = root
        self.tags = tags
        self.children = self.get_children(self.root)

    def get_children(self, root: Path) -> list:
        cfg = tize_config.ConfigFactory.get_config_class(root)
        config_obj = cfg(root)

        children = []
        if not self.should_process(config_obj):
            return children

        if root.is_file():
            children.append(config_obj)
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


class Build:
    def __init__(
        self,
        # destination: Path,
        source: Path = Path(os.getcwd()),
        variables: dict = {},
        env: jinja2.Environment = None,
        **kwargs,
    ):
        # self.destination = destination
        self.source = source
        self.tree = Tree(self.source, **kwargs)
        self.variables = {
            "tags": self.tree.tags,
            "children": self.tree.children,
        } | variables

        if not env:
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.tree.root))
        self.env = env

    def render(self, destination: Path):
        for child in self.tree.children:
            self.render_item(child, destination)

    def render_item(self, item: tize_config.File, root: Path):
        relative_path = item.path.relative_to(self.source)
        destination = root / relative_path
        os.makedirs(destination.parent, exist_ok=True)

        if utils.is_binary(self.source / item.path):
            shutil.copyfile(self.source / item.path, destination)
            return

        template = self.env.get_template(str(relative_path))

        with open(destination, "w") as f:
            destination_content = template.render(self.variables)
            f.write(destination_content)

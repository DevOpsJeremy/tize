from pathlib import Path
import re
import json
from tize import utils
import textwrap
import yaml


class Base:
    _default = None

    def __init__(self):
        pass

    @classmethod
    def get_default(cls):
        if cls._default is None:
            with open(utils.get_file("config.defaults.json"), "r") as f:
                cls._default = json.load(f)
        return cls._default


class File(Base):
    def __init__(self, path: Path):
        if not path.is_file():
            raise Exception(f"Invalid path: {path}. Not a file.")
        self.path = path
        parser_cls = ParserFactory.get_parser(self.path)
        self.parser = parser_cls(self.path)
        self.config = self.get_config()

    def get_config(self):
        defaults = self.get_default()
        return utils.merge_dicts(defaults.copy(), self.parser.config)


class Parser:
    REGEX_OPTIONS = re.MULTILINE
    CONFIG_GROUP = "config"
    CONTENT_GROUP = "content"
    CONFIG_START = r"-{3,}"
    CONFIG_END = r"-{3,}"

    PREFIXES = {
        ".py": "#",
        ".toml": "#",
        ".yaml": "#",
        ".yml": "#",
        ".sh": "#",
        ".md": "<!--",
        ".html": "<!--",
    }
    DEFAULT_PREFIX = "#"

    def __init__(self, path: Path):
        self.path = path
        self.update()

    def update(self):
        self.prefix = self.get_prefix(self.path)
        self.content = self.path.read_text()
        self.pattern = self.get_pattern()
        self.matches = self.search_content()
        self.config, self.pruned_content = self.get_config()

    def assemble_pattern(self):
        prefix = re.escape(self.prefix)

        return "".join(
            [
                r"^(",
                prefix,
                self.CONFIG_START,
                r"\n(?P<",
                self.CONFIG_GROUP,
                r">(",
                prefix,
                r".*\n)*)",
                prefix,
                self.CONFIG_END,
                r"\n?)?(?P<",
                self.CONTENT_GROUP,
                r">(.*\n?)*)",
            ]
        )

    def get_pattern(self):
        return re.compile(self.assemble_pattern(), self.REGEX_OPTIONS)

    @classmethod
    def get_prefix(cls, path: Path):
        return Parser.PREFIXES.get(path.suffix, Parser.DEFAULT_PREFIX)

    def search_content(self):
        return self.pattern.search(self.content)

    def clean_config(self, config_string: str):
        return textwrap.dedent(
            re.sub(r"^" + self.prefix, "", config_string, flags=re.MULTILINE)
        ).strip()

    def get_config(self):
        config_comment = self.matches.group(self.CONFIG_GROUP)
        cleaned_config = self.clean_config(config_comment)

        return (yaml.safe_load(cleaned_config), self.matches.group(self.CONTENT_GROUP))


class HtmlParser(Parser):
    REGEX = r"^(<!\-\-( *\n)*-{3,}\n(?P<config>(.*\n)*)-{3,}\n?(.*\n)*\-\->)?(?P<content>(.*\n?)*)"

    DEFAULT_PREFIX = "<!--"
    SUFFIXES = {
        ".md": "-->",
        ".html": "-->",
    }
    DEFAULT_SUFFIX = "-->"

    def __init__(self, path: Path):
        self.suffix = HtmlParser.get_suffix(path)
        super().__init__(path)

    @classmethod
    def get_suffix(cls, path: Path):
        return HtmlParser.SUFFIXES.get(path.suffix, HtmlParser.DEFAULT_SUFFIX)

    def assemble_pattern(self):
        prefix = re.escape(self.prefix)
        suffix = re.escape(self.suffix)

        return "".join(
            [
                r"^(",
                prefix,
                r"( *\n)*",
                self.CONFIG_START,
                r"\n(?P<",
                self.CONFIG_GROUP,
                r">(.*\n)*)",
                self.CONFIG_END,
                r"\n?( *\n)*",
                suffix,
                r")?(?P<",
                self.CONTENT_GROUP,
                r">(.*\n?)*)",
            ]
        )


class ParserFactory:
    PARSERS = {
        "#": Parser,
        "<!--": HtmlParser,
    }
    DEFAULT_PARSER = Parser

    def get_parser(path: Path):
        prefix = Parser.get_prefix(path)

        return ParserFactory.PARSERS.get(prefix, ParserFactory.DEFAULT_PARSER)


def get_file_config(path: Path) -> dict:
    file = File(path)

    config = file.config
    comment_regex = r"^(\#-{3,}tize\n(?P<scaffold_config>(\#.*\n)*)\#-{3,}\n?)?(?P<content>(.*\n?)*)"
    if path.suffix in [".md", ".markdown", ".html"]:
        comment_regex = r"^(<!\-\-( *\n)*-{3,}tize\n(?P<scaffold_config>(.*\n)*)-{3,}\n?(.*\n)*\-\->)?(?P<content>(.*\n?)*)"
    pattern = re.compile(comment_regex, re.MULTILINE)
    file_content = path.read_text()
    matches = pattern.search(file_content)
    config_text_raw = matches.group("scaffold_config")
    if not config_text_raw:
        return config
    config_text = config_text_raw
    if path.suffix not in [".md", ".markdown", ".html"]:
        config_text = re.sub(r"^\#", "", config_text_raw, flags=re.MULTILINE)
    config_text_cleaned = textwrap.dedent(config_text).strip()
    try:
        file_config = yaml.safe_load(config_text_cleaned)
        utils.merge_dicts(config, file_config)
    except Exception as e:
        raise e
    return config

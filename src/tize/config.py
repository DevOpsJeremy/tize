# ---
# {"tags":["something"]}
# ---
import json
import jsonschema
import re
import textwrap
import yaml
from pathlib import Path
from tize import utils


class Base:
    DEFAULTS = {"tags": ["all"]}
    SCHEMA = {"properties": {"tags": {"type": "array"}}}

    def __init__(self, defaults: dict = None, schema: dict = None):
        self.path = None
        self.parser = None
        self.config = None
        self.binary = None

        if defaults:
            self.DEFAULTS = defaults

        if schema:
            self.SCHEMA = schema

    @classmethod
    def merge_config(cls, config: dict):
        return utils.merge_dicts(cls.DEFAULTS.copy(), config)

    def validate_config(self):
        jsonschema.validate(self.config, self.SCHEMA)


class File(Base):
    def __init__(self, path: Path, defaults: dict = None, schema: dict = None):
        super().__init__(defaults=defaults, schema=schema)

        if not path.is_file():
            raise Exception(f"Invalid path: {path}. Not a file.")
        self.path = path
        parser_cls = ParserFactory.get_parser(self.path)
        self.parser = parser_cls(self.path)

        self.binary = utils.is_binary(self.path)
        if self.binary:
            return

        self.config = self.merge_config(self.parser.config)
        self.validate_config()


class Directory(Base):
    CONFIG_FILE_BASE = "tize"
    CONFIG_FILE_EXTS = (
        ".json",
        ".jsonc",
        ".yaml",
        ".yml",
    )
    CONFIG_FILE_REGEX = r"\." + CONFIG_FILE_BASE + r"\.(jsonc?|ya?ml)"

    def __init__(self, path: Path, defaults: dict = None, schema: dict = None):
        super().__init__(defaults=defaults, schema=schema)

        if not path.is_dir():
            raise Exception(f"Invalid path: {path}. Not a directory.")
        self.path = path
        self.configuration_file = self.get_config_file()
        base_config = {}
        if self.configuration_file:
            with open(self.configuration_file, "r") as f:
                base_config = json.load(f)
        self.config = self.merge_config(base_config)
        self.validate_config()

    def get_config_file(self):
        configuration_file = None

        for ext in self.CONFIG_FILE_EXTS:
            filepath = self.path / self.assemble_config_filename(ext)
            if filepath.exists():
                configuration_file = filepath
                break

        return configuration_file

    @classmethod
    def assemble_config_filename(cls, extension: str = CONFIG_FILE_EXTS[0]):
        ext = extension
        if not extension.startswith("."):
            ext = "." + extension
        return f".{cls.CONFIG_FILE_BASE}{ext}"


class ConfigFactory:
    def get_config_class(path: Path):
        if not path.exists():
            raise FileNotFoundException(f"Invalid path: {path}. Path does not exist.")

        if path.is_dir():
            return Directory
        elif path.is_file():
            return File


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
        self.prefix = None
        self.content = None
        self.pattern = None
        self.matches = None
        self.config = None
        self.pruned_content = None

        self.path = path
        self.update()

    def update(self):
        self.prefix = self.get_prefix(self.path)
        if utils.is_binary(self.path):
            return

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
        re_pattern = r"^" + self.prefix
        sub = re.sub(re_pattern, "", config_string, flags=re.MULTILINE)
        dedent_strip = textwrap.dedent(sub).strip()
        return dedent_strip

    def get_config(self):
        config_comment = self.matches.group(self.CONFIG_GROUP)
        try:
            cleaned_config = self.clean_config(config_comment)
            config = yaml.safe_load(cleaned_config)
        except:
            config = Base.DEFAULTS

        return (config, self.matches.group(self.CONTENT_GROUP))


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

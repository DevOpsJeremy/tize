import pytest
import textwrap
from tize import config
import os


@pytest.mark.parametrize(
    "filename,content",
    [
        (
            "sample_yaml.py",
            """
            #---
            # tags:
            #   - tag1
            #---
            def sample_func():
                return "Hello world"
            """,
        ),
        (
            "sample_json.py",
            """
            #---
            # {"tags": ["tag1"]}
            #---
            def sample_func():
                return "Hello world"
            """,
        ),
        (
            "sample_yaml.md",
            """
            <!--
            ---
            tags:
              - tag1
            ---
            -->
            # Overview

            Hello world
            """,
        ),
        (
            "sample_json.md",
            """
            <!--
            ---
            {"tags": ["tag1"]}
            ---
            -->
            # Overview

            Hello world
            """,
        ),
    ],
)
def test_parser(filename, content, tmp_path, compare_config={"tags": ["tag1"]}):
    os.makedirs(tmp_path, exist_ok=True)
    file_path = tmp_path / filename
    file_path.write_text(textwrap.dedent(content).strip())
    file_config = config.ParserFactory.get_parser(file_path)(file_path).config

    assert file_config == compare_config


@pytest.mark.parametrize(
    "filename,content,compare_config",
    [
        (
            "sample_yaml.py",
            """
            #---
            # tags:
            #   - tag1
            #---
            def sample_func():
                return "Hello world"
            """,
            {"tags": ["tag1"]},
        ),
        (
            "sample_yaml.md",
            """
            <!--
            ---
            description: Dummy description
            ---
            -->
            # Overview

            Hello world
            """,
            {"tags": ["all"], "description": "Dummy description"},
        ),
    ],
)
def test_file_config(filename, content, compare_config, tmp_path):
    os.makedirs(tmp_path, exist_ok=True)
    file_path = tmp_path / filename
    file_path.write_text(textwrap.dedent(content).strip())
    file_config = config.File(file_path).config

    assert file_config == compare_config


def test_missing_config_file(tmp_path):
    test_dir = tmp_path / "test_path"
    os.makedirs(test_dir, exist_ok=True)
    dir = config.Directory(test_dir)
    assert dir.configuration_file is None
    assert dir.config == dir.DEFAULTS


def test_multiple_config_files(tmp_path):
    config_extensions = (".jsonc", ".yaml", ".yml")
    test_dir = tmp_path / "test_path"
    os.makedirs(test_dir, exist_ok=True)
    for ext in config_extensions:
        config_filename = config.Directory.assemble_config_filename(ext)
        config_path = test_dir / config_filename
        config_path.write_text("{}")
    dir = config.Directory(test_dir)
    assert dir.configuration_file is not None
    assert dir.configuration_file.name == config.Directory.assemble_config_filename(
        ".jsonc"
    )

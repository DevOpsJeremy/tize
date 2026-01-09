import pytest
import textwrap
from tize import config
from pathlib import Path
import os

VALID_CONFIG = {
    'tags': ['tag1', 'tag2']
}

INVALID_CONFIG = {
    'tags': 'not-a-list'
}

@pytest.mark.parametrize(
    "filename,content",
    [
        (
            "sample_yaml.py",
            """
            #---tize
            # tags:
            #   - tag1
            #---
            def sample_func():
                return "Hello world"
            """
        ),
        (
            "sample_json.py",
            """
            #---tize
            # {"tags": ["tag1"]}
            #---
            def sample_func():
                return "Hello world"
            """
        ),
        (
            "sample_yaml.md",
            """
            <!--
            ---tize
            tags:
              - tag1
            ---
            -->
            # Overview

            Hello world
            """
        ),
        (
            "sample_json.md",
            """
            <!--
            ---tize
            {"tags": ["tag1"]}
            ---
            -->
            # Overview

            Hello world
            """
        )
    ]
)
def test_file_config(filename, content, tmp_path, compare_config={'tags': ['tag1']}):
    os.makedirs(tmp_path, exist_ok=True)
    file_path = tmp_path / filename
    file_path.write_text(textwrap.dedent(content).strip())
    print(file_path.read_text())
    file_config = config.get_file_config(file_path)
    print(file_config)
    assert file_config == compare_config

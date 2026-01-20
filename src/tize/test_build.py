import os
import textwrap
from pathlib import Path
from tize import config, build


def test_binary_file(tmp_path):
    test_dir = tmp_path / "test_path"
    os.makedirs(test_dir, exist_ok=True)
    filename = "test_script.py"
    file = test_dir / filename

    with open(file, "wb") as f:
        f.write(bytearray())

    build.Tree(Path(test_dir))

def test_render(tmp_path):
    dest_dir = tmp_path / "dest_path"

    source_dir = tmp_path / "source_path"
    sub_dir = source_dir / "subdir"
    for dir in (source_dir, sub_dir):
        os.makedirs(dir, exist_ok=True)
    file1 = source_dir / "file1.py"
    file2 = sub_dir / "config.json"

    content = """
    import os

    os.getcwd()
    """

    for file in (file1, file2):
        with open(file, "w") as f:
            f.write(textwrap.dedent(content).strip())

    build.Build(source_dir).render(dest_dir)


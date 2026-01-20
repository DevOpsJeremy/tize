import os
import textwrap
from pathlib import Path
from tize import build


def test_tree_binary_file(tmp_path):
    test_dir = tmp_path / "test_tree_binary_file"
    os.makedirs(test_dir, exist_ok=True)
    filename = "test_script.py"
    file = test_dir / filename

    with open(file, "wb") as f:
        f.write(bytearray())

    build.Tree(test_dir)

def test_build_binary_file(tmp_path):
    test_dir = tmp_path / "test_build_binary_file_src"
    test_dir_dest = tmp_path / "test_build_binary_file_dest"
    os.makedirs(test_dir, exist_ok=True)
    filename = "test_script.py"
    file = test_dir / filename

    with open(file, "wb") as f:
        f.write(bytearray())

    build.Build(test_dir).render(test_dir_dest)

def test_render(tmp_path):
    dest_dir = tmp_path / "dest_path"
    source_dir = tmp_path / "source_path"

    sub_dir_rel = "subdir"
    sub_dir = source_dir / sub_dir_rel
    for dir in (source_dir, sub_dir):
        os.makedirs(dir, exist_ok=True)

    file1_rel = "file1.py"
    file1 = source_dir / file1_rel
    file2_rel = f"{sub_dir_rel}/config.json"
    file2 = source_dir / file2_rel

    content = """
    import os

    os.getcwd()
    """

    for file in (file1, file2):
        with open(file, "w") as f:
            f.write(textwrap.dedent(content).strip())

    build.Build(source_dir).render(dest_dir)

    dest_file1 = dest_dir / file1_rel
    dest_file2 = dest_dir / file2_rel

    with open(file1) as f:
        file1_source_content = f.read().strip()

    with open(file2) as f:
        file2_source_content = f.read().strip()

    with open(dest_file1) as f:
        file1_dest_content = f.read().strip()

    with open(dest_file2) as f:
        file2_dest_content = f.read().strip()

    assert file1_source_content == file1_dest_content
    assert file2_source_content == file2_dest_content

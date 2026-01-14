import os
from pathlib import Path
from tize import config, build


def test_binary_file(tmp_path):
    test_dir = tmp_path / "test_path"
    os.makedirs(test_dir, exist_ok=True)
    filename = "test_script.py"
    file = test_dir / filename

    with open(file, "wb") as f:
        f.write(bytearray())

    print(build.Tree(Path(test_dir)))

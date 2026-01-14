from pathlib import Path


def get_file(filename: str, files_dir: str = "files") -> Path:
    files_path = Path(__file__).parent / files_dir
    file = files_path / filename
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file}")
    return file


def merge_dicts(a: dict, b: dict):
    for key in b:
        if key in a and isinstance(a[key], dict) and isinstance(b[key], dict):
            merge_dicts(a[key], b[key])
        else:
            a[key] = b[key]
    return a

def is_binary_string(bytes):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    return bool(bytes.translate(None, textchars))

def is_binary(path: Path):
    with open(path, 'rb') as file:
        return is_binary_string(file.read(1024))


#!/usr/bin/env python
# ruff: noqa

from pathlib import Path
from tize import config, build

b = build.Build()
destination = Path('/tmp')
b.render(destination)

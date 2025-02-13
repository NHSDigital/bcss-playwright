#!/bin/bash

ruff --fix
mypy tests/*.py pages/*.py utils/*.py --disallow-untyped-defs --explicit-package-bases
pytest
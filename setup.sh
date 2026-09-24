#!/usr/bin/env sh
set -eu
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/nabla doctor
printf '%s\n' 'Pronto. Execute .venv/bin/nabla run "(x+x)/x" --value x=3'

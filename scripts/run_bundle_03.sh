#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=src python -m unittest discover -s tests -v

PYTHONPATH=src python -m cogniverse_framework.cli.main

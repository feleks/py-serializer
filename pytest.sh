#!/bin/bash

SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )/source"
(export PYTHONPATH="$SOURCE_DIR:$PYTHONPATH"; pytest -vv $*)

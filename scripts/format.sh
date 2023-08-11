#!/bin/bash

set -eu

ruff_fix=("--fix")
if [[ ${1-} == "--check" ]]; then
    ruff_fix=("--diff")
    black_options=("--check" "--diff")
fi

EXIT_CODE=0

ruff --select I001,I002 "${ruff_fix[@]}" . || EXIT_CODE=1
black . "${black_options[@]}" || EXIT_CODE=1

exit "$EXIT_CODE"

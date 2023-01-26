#!/bin/sh

set -eu

if [ "${1:-}" = "--check" ]; then
    black_args="--check --diff"
    isort_args="--check --diff --quiet"
fi

EXIT_CODE=0

# shellcheck disable=2086
black ${black_args:-} . || EXIT_CODE=1
# shellcheck disable=2086
isort ${isort_args:-} . || EXIT_CODE=1

exit "$EXIT_CODE"

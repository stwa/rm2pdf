#!/bin/sh

set -eu

usage() {
    cat <<EOF
usage: $0 [major|minor|patch]
    Script to help with release creation and automation of the tasks surrounding
    a release. Mainly, raising the version numbers and correctly tagging the
    versions.

    The script will also immediately push the tags and commits.

    So this works correctly it can only be executed with a clean working-tree
    and the 'main' branch.

    The script will give you the version change you requested (if possible).
EOF
}

verify_main_branch() {
    current_branch=$(git branch --show-current)

    [ "$current_branch" = "main" ]
}

verify_clean_working_tree() {
    git diff --quiet
}

release() {
    rule=$1

    poetry version "$rule"
    tag_version=$(poetry version --short)

    git add pyproject.toml
    git commit -m "Prepare release: $tag_version"
    git tag "$tag_version" -m "Release version: $tag_version"
}

prerelease() {
    poetry version "prerelease"

    git add pyproject.toml
    git commit -m "Prepare for next development iteration"
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 1
fi

verify_main_branch || {
    echo "Releases can only be created on main branch!" >&2
    exit 1
}

verify_clean_working_tree || {
    echo "You have unstaged changes, please commit or stash them." >&2
    exit 1
}

rule="${1:-}"

if [ -z "$rule" ]; then
    usage
    exit 1
fi

printf "\n\tReleasing %s\n" "$rule"

release "$rule"
prerelease

echo "Don't forget to run \"git push && git push --tags\"!"

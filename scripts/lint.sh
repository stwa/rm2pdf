#!/bin/sh

set -eu

pylint --fail-under 9 src

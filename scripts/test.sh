#!/bin/sh

set -eu

pytest \
    --cov-branch \
    --cov-report=term \
    --cov-report=html \
    --cov-report=xml \
    --cov=src \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests "$@"

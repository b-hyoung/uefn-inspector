#!/usr/bin/env bash
# Deprecated wrapper — use: node bin/cli.js install
exec node "$(dirname "$0")/bin/cli.js" "${1:-skills}"

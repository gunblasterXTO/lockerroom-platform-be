#!/bin/bash
# allow to be executable `chmod +x run_mypy.sh`
mypy app/ --disallow-untyped-defs

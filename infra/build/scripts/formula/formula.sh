#!/usr/bin/env bash
#^ Dynamically find bash path

# Make sure the script is being run from the root of the project
if [ ! -f "./infra/build/scripts/tarball.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi


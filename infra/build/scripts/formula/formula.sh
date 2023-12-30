#!/usr/bin/env bash
#^ Dynamically find bash path

# Make sure the script is being run from the root of the project
if [ ! -f "./infra/build/scripts/tarball.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Run the tarball script and capture the last line of output
./infra/build/scripts/tarball.sh

# Get sha from the file ./infra/build/formula/$temp_sha_name
sha=$(cat ./infra/build/formula/sha)

# Run the codegen script and give it the sha as an argument
./env/bin/python3 ./infra/build/scripts/formula/codegen.py --sha="$sha"

# Check if the codegen script ran successfully
if [ -f "./infra/build/formula/out/trapp.rb" ]; then
    echo "Formula generated successfully."
else
    echo "Error: Formula generation failed."
    exit 1
fi

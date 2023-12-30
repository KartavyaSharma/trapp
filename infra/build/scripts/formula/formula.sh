#!/usr/bin/env bash
#^ Dynamically find bash path

# Make sure the script is being run from the root of the project
if [ ! -f "./infra/build/scripts/tarball.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Run the tarball script and capture the last line of output
output=$(./infra/build/scripts/tarball.sh)
sha=$(echo "$output" | tail -n 1)

# Check if the length of the last line is equal to 256
if [ ! ${#sha} -eq 256 ]; then
    echo "Error: The length of the last line of output is not equal to 256."
    exit 1
fi

# Run the codegen script and give it the sha as an argument
./infra/build/scripts/codegen.sh --sha="$sha"

# Check if the codegen script ran successfully
if [ -f "./infra/build/formula/out/trapp.rb" ]; then
    echo "Formula generated successfully."
else
    echo "Error: Formula generation failed."
    exit 1
fi

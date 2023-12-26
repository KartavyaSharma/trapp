#!/usr/bin/env bash

# This script is used to build the dependencies for the project.
# It is intended to be run from the root of the project.

# Check if the script is being run from the root of the project
if [ ! -f "./scripts/shell/build_dependencies.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Create the build directory if it doesn't exist
if [ ! -d "./build" ]; then
    mkdir ./build
fi

# Create the dependencies directory if it doesn't exist
if [ ! -d "./build/dependencies" ]; then
    mkdir ./build/dependencies
fi

# Download pip3 dependencies into the dependencies directory
./env/bin/pip download -r ./requirements.txt -d ./build/dependencies

cd ./build

# Create a tarball of the dependencies directory
arch=$(uname -sm)
arch=${arch// /_}
tar -czvf dependencies.tar.$arch.gz dependencies

# Clean up the dependencies directory
rip dependencies

cd .. 

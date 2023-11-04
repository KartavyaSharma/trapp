#!/usr/bin/env bash

# This script loads all the pip3 dependencies for the project.
# It is intended to be run from the root of the project.

# Check if the script is being run from the root of the project
if [ ! -f "./scripts/shell/build_dependencies.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Check if the build directory exists
if [ ! -d "./build" ]; then
    echo "The build directory does not exist. Run build_dependencies.sh first."
    exit 1
fi

# Check if the dependencies tarball exists
if [ ! -f "./build/dependencies.tar.pip3.gz" ]; then
    echo "The dependencies tarball does not exist. Run build_dependencies.sh first."
    exit 1
fi

# Extract the dependencies tarball
tar -xzvf ./build/dependencies.tar.pip3.gz -C ./build

# Install the dependencies
pip3 install --no-index --find-links=./build/dependencies -r ./requirements.txt

# Clean up the dependencies directory
rm -rf ./build/dependencies
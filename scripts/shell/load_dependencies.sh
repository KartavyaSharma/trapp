#!/usr/bin/env bash

# This script loads all the pip3 dependencies for the project.
# It is intended to be run from the root of the project.

# Check if the script is being run from the root of the project
if [ ! -f "$TRAPP_HOME/scripts/shell/build_dependencies.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Check if the build directory exists
if [ ! -d "$TRAPP_HOME/build" ]; then
    echo "The build directory does not exist. Run build_dependencies.sh first."
    exit 1
fi

arch=$(uname -sm)
arch=${arch// /_}

# Check if the dependencies tarball exists
if [ ! -f "$TRAPP_HOME/build/dependencies.tar.$arch.gz" ]; then
    echo "The dependencies tarball does not exist. Running build_dependencies.sh."
    $TRAPP_HOME/scripts/shell/build_dependencies.sh
fi

# Extract the dependencies tarball
tar -xzvf $TRAPP_HOME/build/dependencies.tar.$arch.gz -C ./build

# Install the dependencies
$TRAPP_HOME/env/bin/pip install --no-index --find-links=$TRAPP_HOME/build/dependencies -r $TRAPP_HOME/requirements.txt

# Clean up the dependencies directory
rip $TRAPP_HOME/build/dependencies
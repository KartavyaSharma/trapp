#!/usr/bin/env bash

# This script loads all the pip3 dependencies for the project.
# It is intended to be run from the root of the project.

artifact_home_dir=$TRAPP_HOME/infra/artifacts

# Check if the script is being run from the root of the project
if [ ! -f "$TRAPP_HOME/scripts/shell/build_dependencies.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Check if the build directory exists
if [ ! -d "$artifact_home_dir" ]; then
    echo "The artifact home directory does not exist. Creating it."
    mkdir -p $artifact_home_dir
fi

arch=$(uname -sm)
arch=${arch// /_}

# Check if the dependencies tarball exists
if [ ! -f "$artifact_home_dir/dependencies.tar.$arch.gz" ]; then
    echo "The dependencies tarball does not exist. Running build_dependencies.sh."
    $TRAPP_HOME/scripts/shell/build_dependencies.sh
fi

# Extract the dependencies tarball
tar -xzvf $artifact_home_dir/dependencies.tar.$arch.gz -C $artifact_home_dir

# Install the dependencies
$TRAPP_HOME/env/bin/pip install --no-index --find-links=$artifact_home_dir/dependencies -r $TRAPP_HOME/requirements.txt

# Clean up the dependencies directory
rip $artifact_home_dir/dependencies
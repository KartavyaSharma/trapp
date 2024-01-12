#!/usr/bin/env bash

# This script is used to build the dependencies for the project.
# It is intended to be run from the root of the project.

artifact_home_dir=$TRAPP_HOME/infra/artifacts

# If $artifact_home_dir doesn't exist, create it
if [ ! -d "$artifact_home_dir" ]; then
    mkdir -p $artifact_home_dir
fi

# Check if the script is being run from the root of the project
if [ ! -f "$TRAPP_HOME/scripts/shell/build_dependencies.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

# Create the build directory if it doesn't exist
if [ ! -d "$artifact_home_dir" ]; then
    echo "The artifact home directory does not exist. Creating it."
    mkdir $artifact_home_dir
fi

# Create the dependencies directory if it doesn't exist
if [ ! -d "$artifact_home_dir/dependencies" ]; then
    mkdir $artifact_home_dir/dependencies
fi

# Download pip3 dependencies into the dependencies directory
$TRAPP_HOME/env/bin/pip download -r $TRAPP_HOME/requirements.txt -d $artifact_home_dir/dependencies

cd $artifact_home_dir

# Create a tarball of the dependencies directory
arch=$(uname -sm)
arch=${arch// /_}
tar -czvf dependencies.tar.$arch.gz dependencies

# Clean up the dependencies directory
rip dependencies

cd $TRAPP_HOME 

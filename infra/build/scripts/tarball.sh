#!/usr/bin/env bash
#^ Dynamically find bash path

github_url="https://github.com/KartavyaSharma/trapp.git"
branch="master"
tar_name="trapp-v1.0.0.tar.gz"

while [[ $# -gt 0 ]]
do
    case $1 in
    -b | --branch)
        branch="$2"
        ;;
    -h | --help)
        echo "Usage: $0 [-b | --branch <branch>]"
        exit 0
        ;;
    *)
        echo "Invalid argument: $1"
        exit 1
        ;;
    esac
    shift
done

# Create a temporary directory
tmp_dir=$(mktemp -d)

# Clone the repository
git clone --depth 1 --branch $branch $github_url $tmp_dir

# Create tarball from the files in the temporary directory
tar -czvf $tar_name -C $tmp_dir .

# Clean up the temporary directory
rip $tmp_dir

echo "Created tarball: $tar_name"

exit 0
#!/usr/bin/env bash
#^ Dynamically find bash path

if [ ! -f "./infra/build/scripts/tarball.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

github_url="https://github.com/KartavyaSharma/trapp.git"
branch="master"
tar_name="trapp-v1.0.0.tar.gz"

if [ -f "./infra/build/$tar_name" ]; then
    rip "./infra/build/$tar_name"
fi

message="The following files were changed:\n $(git diff --name-only)\n"

OPTS=$(getopt -o b:m:h --long branch:,message:,help -n 'tarball.sh' -- "$@")
if [ $? != 0 ]; then
    echo "Failed to parse command line arguments."
    exit 1
fi

eval set -- "$OPTS"

while true; do
    case "$1" in
    -b | --branch)
        branch="$2"
        shift 2
        ;;
    -m | --message)
        message="$2"
        shift 2
        ;;
    -h | --help)
        echo "Usage: $0 [-b | --branch <branch>] [-m | --message <msg>]"
        exit 0
        ;;
    --)
        shift
        break
        ;;
    *)
        echo "Invalid argument: $1"
        exit 1
        ;;
    esac
done

# Ask for confirmation if the user wants to commit the changes
echo "Committing the following changes:\n"
echo -e "$message"
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting."
    exit 1
fi

git add .
git commit -m "$message"
git push origin $branch

tmp_dir=$(mktemp -d)

git clone --depth 1 --branch $branch $github_url $tmp_dir

rip $tmp_dir/.git
rip $tmp_dir/infra
rip $tmp_dir/docs/assets
rip $tmp_dir/docs/README.md

tar -czvf $tar_name -C $tmp_dir . > /dev/null 2>&1

rip $tmp_dir

mv $tar_name ./infra/build

sha=$(shasum -a 256 ./infra/build/$tar_name | awk '{print $1}')

echo "$sha" > ./infra/build/formula/sha
echo "$sha"

exit 0
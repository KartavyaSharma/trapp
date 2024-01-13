#!/usr/bin/env bash
#^ Dynamically find bash path

# Make sure the script is being run from the root of the project
if [ ! -f "./infra/build/scripts/tarball.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

brew_formula_repo="KartavyaSharma/homebrew-trapp"
brew_formula_repo_url="https://github.com/$brew_formula_repo.git"

trapp_repo="KartavyaSharma/trapp"
trapp_release_tag="Production"
trapp_asset_name="trapp-v1.0.0.tar.gz"
trapp_new_asset_path="./infra/build/$trapp_asset_name"

./infra/build/scripts/tarball.sh

sha=$(cat ./infra/build/formula/sha)

rip ./infra/build/formula/sha

./env/bin/python3 ./infra/build/scripts/formula/codegen.py --sha="$sha"

# Check if the codegen script ran successfully
if [ -f "./infra/build/formula/out/trapp.rb" ]; then
    echo "Formula generated successfully."
else
    echo "Error: Formula generation failed."
    exit 1
fi

temp_dir=$(mktemp -d)

git clone --depth 1 --branch master "$brew_formula_repo_url" "$temp_dir"

# Delete the old formula
rip "$temp_dir/Formula/trapp.rb"

# Move the generated formula to the formula repo overwriting the old formula
mv ./infra/build/formula/out/trapp.rb "$temp_dir/Formula/trapp.rb"

curr_dir=$(pwd)

# Commit the changes
cd "$temp_dir" || exit 1
git add .
git commit -m "Update trapp formula to version $sha"
git push origin master
cd "$curr_dir" || exit 1

rip "$temp_dir"

echo "Formula update complete."

# Upload the new tarball to the release
./infra/github/scripts/new_release.sh --tag="$trapp_release_tag" --asset-name="$trapp_asset_name" --path="$trapp_new_asset_path" --repo="$trapp_repo"

rip "$trapp_new_asset_path"

echo -e "To reinstall trapp run the following command:\n"
echo "curr_dir=$(pwd) && cd $(brew --repo KartavyaSharma/homebrew-trapp) && git pull origin master && cd $curr_dir && brew reinstall trapp"
#!/usr/bin/env bash
#^ Dynamically find bash path

# Make sure the script is being run from the root of the project
if [ ! -f "./infra/build/scripts/tarball.sh" ]; then
    echo "This script must be run from the root of the project."
    exit 1
fi

brew_formula_repo="KartavyaSharma/homebrew-trapp"
brew_formula_repo_url="https://github.com/$brew_formula_repo.git"

# Run the tarball script and capture the last line of output
./infra/build/scripts/tarball.sh

# Get sha from the file ./infra/build/formula/$temp_sha_name
sha=$(cat ./infra/build/formula/sha)

# Remove the sha file
rip ./infra/build/formula/sha

# Run the codegen script and give it the sha as an argument
./env/bin/python3 ./infra/build/scripts/formula/codegen.py --sha="$sha"

# Check if the codegen script ran successfully
if [ -f "./infra/build/formula/out/trapp.rb" ]; then
    echo "Formula generated successfully."
else
    echo "Error: Formula generation failed."
    exit 1
fi

# Create a temporary directory to clone the formula repo
temp_dir=$(mktemp -d)

# Clone the formula repo
git clone --depth 1 --branch master "$brew_formula_repo_url" "$temp_dir"

# Delete the old formula
rip "$temp_dir/Formula/trapp.rb"

# Move the generated formula to the formula repo overwriting the old formula
mv ./infra/build/formula/out/trapp.rb "$temp_dir/Formula/trapp.rb"

# Commit the changes
cd "$temp_dir" || exit 1
git add .
git commit -m "Update trapp formula to version $sha"
git push origin master

# Remove the temporary directory
rip "$temp_dir"

echo "Formula update complete."
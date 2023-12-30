#!/usr/bin/env bash

# Initialize variables
RELEASE_TAG=""
OLD_ASSET_NAME=""
NEW_FILE_PATH=""
REPO_PATH=""

# Function to show usage
usage() {
    echo "Usage: $0 --tag=<tag> --asset-name=<name> --path=<new_path> --repo=<repo_path>"
    exit 1
}

# Parse command line arguments
while [ "$1" != "" ]; do
    case $1 in
        --tag=*)
            RELEASE_TAG="${1#*=}"
            ;;
        --asset-name=*)
            OLD_ASSET_NAME="${1#*=}"
            ;;
        --path=*)
            NEW_FILE_PATH="${1#*=}"
            ;;
        --repo=*)
            REPO_PATH="${1#*=}"
            ;;
        *)
            usage
            ;;
    esac
    shift
done

# Check if all parameters are set
if [ -z "$RELEASE_TAG" ] || [ -z "$OLD_ASSET_NAME" ] || [ -z "$NEW_FILE_PATH" ]; then
    echo "Error: Missing argument."
    usage
fi

# Rest of the script follows
echo "Updating release with tag: $RELEASE_TAG"
echo "Replacing asset: $OLD_ASSET_NAME"
echo "With new file at path: $NEW_FILE_PATH"

# Step 1: Delete the old asset
echo "Deleting the old asset..."
gh release delete-asset "$RELEASE_TAG" "$OLD_ASSET_NAME" -R "$REPO_PATH" -y

sleep 2

# Step 2: Upload the new file
echo "Uploading the new file..."
gh release upload "$RELEASE_TAG" "$NEW_FILE_PATH" -R "$REPO_PATH" --clobber

echo "Release update complete."
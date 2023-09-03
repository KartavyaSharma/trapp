#!/bin/bash

# Dictionary to maintain gum binary links
declare -A gum_binary_links

gum_binary_links["Darwin arm64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Darwin_arm64.tar.gz"
gum_binary_links["Darwin x86_64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Darwin_x86_64.tar.gz"
gum_binary_links["Linux arm64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Linux_arm64.tar.gz"
gum_binary_links["Linux x86_64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Linux_x86_64.tar.gz"

# Check if we are in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Not in a virtual environment"
    # Check if env file exists in current directory
    echo "Checking if env file exists..."
    if test -d env; then
        if test -f ./env/bin/activate; then
            echo "Environment directory exists. Activating environment..."
            source ./env/bin/activate
        else
            echo "`env` folder exists, but activate file missing."
        fi
    else
        echo "Environment directory does not exist. Creating a new environment..."
        python3 -m venv env
        echo "New virtual environment created. Activating..."
        source ./env/bin/activate
    fi
else
    echo "Virtual environment found!"
fi

# Check if requirements are satisfied in virtual environment
output=$(python3 ./tests/test_requirements.py)
if [ $? -ne 0 ]; then
    echo "Error: python3 ./tests/test_requirements.py failed with output:"
    echo "$output"
    echo "Dependency requirements not satisfied. Installing dependencies..."
    pip3 install -r requirements.txt
else
    echo "All dependencies are present!"
fi

# Check if gum is installed
if ! command -v ./gum &> /dev/null; then
    echo "charmbracelet/gum was not found. Installing"
    echo "Determining system architecture"
    arch=$(uname -s -m)
    if test "${gum_binary_links["$arch"]+isset}"; then
        url="${gum_binary_links["$arch"]}"
    else
        echo "Invalid architecture: $arch. trapp is only supported on Darwin and Linux x86_64 and arm64."
        exit 1
    fi
    echo "Fetching gum binary..."
    wget "$url"
    tar -xzf $(basename "$url") gum
    chmod +x $(basename "$url")
    echo "Installed gum!"
    echo "Cleaning up..."
    rm $(basename "$url")
else
    if ! test -d "cache"; then
        echo "WOW, you already have the gum library you SHELL fiend!"
    else
        echo "Gum library detected. Onward!"
    fi
fi

# Set a flag so that the "WOW, ..." print does not run every time.
if ! test -d "cache"; then
    echo "Creating cache file..."
    mkdir cache && touch ./cache/gum.flag && echo "1" >> ./cache/gum.flag
fi

echo
echo "Running program..."
ARGFLAG=0
for arg in "$@"
do
    case $arg in
        -b | --wbkp)
        python3 runner.py wbkp
        ARGFLAG=1
        ;;
        -h | --help)
        echo "Usage: ./start.sh [OPTION]"
        echo "Options:"
        echo "  -b, --wbkp      Run and start backup process"
        echo "  -h, --help      Print help and exit"
        ;;
        *)
        echo "Invalid option: $arg"
        exit 1
        ;;
    esac
done
if [ $ARGFLAG -eq 0 ]; then
    python3 runner.py 
fi
echo "Program exited. Deactivating virtual environment..."
deactivate

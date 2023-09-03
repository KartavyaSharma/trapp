#!/bin/bash

# Check if we are in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Not in a virtual environment"
    # Check if env file exists in current directory
    echo "Checking if env file exists..."
    if test -d "env" && test -f "/env/bin/activate"; then
        echo "Environment directory exists. Activating environment..."
        source ./env/bin/activate
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
if ! command -v gum &> /dev/null; then
    echo "charmbracelet/gum was not found. Installing"
    go install github.com/charmbracelet/gum@latest
    echo "Installed gum!"
else
    if ! test -f "/cache/gum.flag"; then
        echo "WOW, you already have the gum library you SHELL fiend!"
    else
        echo "Gum library detected. Onward!"
    fi
fi

# Set a flag so that the "WOW, ..." print does not run every time.
mkdir cache && touch cache/gum.flag && echo "1" >> cache/gum.flag

echo
echo "Running program..."
python3 runner.py
    

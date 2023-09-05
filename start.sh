#!/bin/bash

# Make a temporary alias for echo
alias cecho="./echo.sh"

# Dictionary to maintain gum binary links
declare -A gum_binary_links

gum_binary_links["Darwin arm64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Darwin_arm64.tar.gz"
gum_binary_links["Darwin x86_64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Darwin_x86_64.tar.gz"
gum_binary_links["Linux arm64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Linux_arm64.tar.gz"
gum_binary_links["Linux x86_64"]="https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Linux_x86_64.tar.gz"

# Check if we are in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    cecho -c yellow -t "Not in a virtual environment"
    # Check if env file exists in current directory
    cecho -c yellow -t "Checking if env file exists..."
    if test -d env; then
        if test -f ./env/bin/activate; then
            cecho -c green -t "Environment directory exists. Activating environment..."
            source ./env/bin/activate
        else
            cecho -c red -t "$(env) folder exists, but activate file missing."
        fi
    else
        cecho -c yellow -t "Environment directory does not exist. Creating a new environment..."
        python3 -m venv env
        cecho -c green -t "New virtual environment created. Activating..."
        source ./env/bin/activate
    fi
else
    cecho -c green -t "Virtual environment found!"
fi

# Check if requirements are satisfied in virtual environment
output=$(python3 ./tests/test_requirements.py)
if [ $? -ne 0 ]; then
    cecho -c red -t "Error: python3 ./tests/test_requirements.py failed with output^"
    cecho -c red -t "Dependency requirements not satisfied. Installing dependencies..."
    pip3 install -r requirements.txt
else
    cecho -c green -t "All dependencies are present!"
fi

# Check if gum is installed
if ! command -v ./gum &>/dev/null; then
    cecho -c yellow -t "charmbracelet/gum was not found. Installing..."
    echo "Determining system architecture..."
    arch=$(uname -s -m)
    if test "${gum_binary_links["$arch"]+isset}"; then
        url="${gum_binary_links["$arch"]}"
    else
        cecho -c red -t "Invalid architecture: $arch. trapp is only supported on Darwin and Linux x86_64 and arm64."
        return
    fi
    cecho -c yellow -t "Fetching gum binary..."
    wget "$url"
    tar -xzf $(basename "$url") gum
    chmod +x $(basename "$url")
    cecho -c green -t "Installed gum!"
    echo "Cleaning up..."
    rm $(basename "$url")
else
    if ! test -d "cache"; then
        cecho -c green -t "WOW, you already have the gum library you SHELL fiend!"
    else
        cecho -c green -t "Gum library detected. Onward!"
    fi
fi

# Set a flag so that the "WOW, ..." print does not run every time.
if ! test -d "cache"; then
    echo "Creating cache file..."
    mkdir cache && touch ./cache/gum.flag && echo "1" >>./cache/gum.flag
fi

echo
ARGFLAG=0
for arg in "$@"; do
    case $arg in
    -b | --wbkp)
        echo "Running program..."
        python3 runner.py wbkp
        ARGFLAG=1
        ;;
    -h | --help)
        echo "Usage: ./start.sh [OPTION]"
        echo "Options:"
        echo "  -b, --wbkp      Run and start backup daemon"
        echo "  -c, --clean     Clean up cache and daemon files"
        echo "  -s, --stop      Stop backup daemon"
        echo "  -r, --restart   Restart backup daemon"
        echo "  -t, --test      Test if backup daemon is running"
        echo "  -h, --help      Print help and exit"
        ARGFLAG=2
        ;;
    -c | --clean)
        echo "Cleaning up..."
        echo "Removing cache\nRemoving pid\nRemoving logs\nRemoving TRAPP-DAEMON.pid\nRemoving bkp.out"
        rm -rf cache bkp/pid bkp/logs bkp/bkp.out bkp
        echo
        ARGFLAG=3
        ;;
    -s | --stop)
        ./bkp_daemon.sh stop
        ARGFLAG=4
        ;;
    -r | --restart)
        # Stop and start daemon
        ./bkp_daemon.sh stop
        # Start daemon as a background process
        cecho -c green -t "Starting backup daemon..."
        nohup ./bkp_daemon.sh start > bkp/bkp.out &
        ARGFLAG=5
        ;;
    -t | --test)
        ./bkp_daemon.sh status
        ARGFLAG=6
        ;;
    *)
        cecho -c red -t "Invalid option: $arg"
        return
        ;;
    esac
done
if [ $ARGFLAG -eq 0 ]; then
    cecho -c green -t "Running program..."
    python3 runner.py
elif [ $ARGFLAG -eq 1 ]; then
    chmod +x ./bkp_daemon.sh
    echo "=========================="
    echo "Starting backup daemon..."
    if ! test -d "bkp"; then
        cecho -c yellow -t "Creating bkp directory..."
        mkdir bkp
    fi
    nohup ./bkp_daemon.sh start > bkp/bkp.out &
    cecho -c green -t "Backup daemon started!"
    echo
    echo "Usage: ./start.sh [OPTION]"
    echo "For more options, run ./start.sh --help"
    echo
    echo "You can view daemon logs in ./bkp/logs/TRAPP-DAEMON.log"
    echo "You can view any daemon output in ./bkp/bkp.out"
    echo "=========================="
fi
cecho -c green -t "Program exited. Deactivating virtual environment..."
deactivate
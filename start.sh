#!/usr/bin/env bash

# Make a temporary alias for echo
alias cecho="./scripts/shell/echo.sh"

# Check system architecture
arch=$(uname -s)
if [[ "$arch" == "Linux" ]]; then
    cecho -c yellow -t "You are on Linux. Performing check for required Python packages..."
    if command -v pip3 &> /dev/null; then
        cecho -c green -t "pip3 found!"
    elif command -v pip &> /dev/null; then
        cecho -c green -t "pip found!"
        alias pip3=pip
    else
        cecho -c red -t "pip3 or pip not found. Likely because of a missing `ensurepip` module. This is required to create a virtual environment."
        cecho -c yellow -t "Prepare to provide sudo password to install required virtual environment packages..."
        sudo apt-get install python3-venv python3-pip
    fi
fi

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
if ! command -v ./bin/gum &>/dev/null; then
    cecho -c yellow -t "charmbracelet/gum was not found. Installing..."
    echo "Determining system architecture..."
    arch=$(uname -s -m)
    if test "${gum_binary_links["$arch"]+isset}"; then
        url="${gum_binary_links["$arch"]}"
    else
        cecho -c red -t "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
        return
    fi
    cecho -c yellow -t "Fetching gum binary..."
    mkdir bin && cd bin
    wget "$url"
    tar -xzf $(basename "$url") gum
    chmod +x $(basename "$url")
    cecho -c green -t "Installed gum!"
    echo "Cleaning up..."
    rm $(basename "$url")
    cd ..
else
    if ! test -d "cache"; then
        cecho -c green -t "WOW, you already have the gum library you SHELL fiend!"
    else
        cecho -c green -t "Gum library detected"
    fi
fi

# Bat binary path
bat_path="bin/bat/bin/bat"
bat_commit="fc95468" # Latest commit trapp is tested with
# Check if sharkdp/bat is installed
if ! command -v ./$bat_path &>/dev/null; then
    cecho -c yellow -t "sharkdp/bat was not found. Installing..."
    # Check if system has rust installed
    if ! command -v rustc &>/dev/null; then
        cecho -c yellow -t "Rust not found. Trapp requires rust to work. Installing..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        cecho -c green -t "Rust installed!"
        source $HOME/.cargo/env
    else
        cecho -c green -t "Rust found!"
    fi
    # Pull bat from github 
    git clone https://github.com/sharkdp/bat.git
    cd bat
    # Switch to stable commit
    git reset --hard $bat_commit
    # Build bat
    mkdir ../bin/bat
    cargo install --root ../bin/bat --locked bat
    cd ..
    cecho -c green -t "Installed bat!"
fi

# Check if docker is installed and running
if ! (command -v docker) > /dev/null
then
    echo 'You must have docker installed before running this script! (See https://www.docker.com)' 1>&2
    exit 1
fi

colima_ver=v0.5.6
# Check if colima is installed
if ! (command -v colima) > /dev/null
then
    cecho -c yellow -t "colima was not found. Installing..."
    # download binary
    mkidir bin/colima
    cd bin/colima
    curl -LO https://github.com/abiosoft/colima/releases/download/${colima_ver}/colima-$(uname)-$(uname -m)
    # if usr/local/bin requires sudo, prompt for password
    if [ -w "/usr/local/bin" ]
    then
        cecho -c yellow -t "Installing colima to /usr/local/bin..."
        # install in $PATH
        install colima-$(uname)-$(uname -m) /usr/local/bin/colima
    else
        cecho -c yellow -t "usr/local/bin requires sudo to install Colima. Prepare to provide sudo password..." 
        sleep 2
        # install in $PATH
        sudo install colima-$(uname)-$(uname -m) /usr/local/bin/colima
    fi
else
    cecho -c green -t "Colima found!"
fi

if [[ "$(docker info 2>&1)" =~ "Cannot connect to the Docker daemon" ]]
then
    cecho -c yellow -t "Docker runtime not detected. Starting runtime (colima)..."
    # start colima
    colima start
else
    cecho -c green -t "Docker runtime found!"
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
        echo "Running program with backup option..."
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
        echo "Removing preview files..."
        # Delete any preview files with the .preview extension
        find . -type f -name "*.preview" -delete
        # Removing all dependencies
        echo "Removing dependencies..."
        rm -rf env
        rm -rf bin
        rm -rf bat
        echo
        ARGFLAG=3
        ;;
    -s | --stop)
        ./scripts/shell/bkp_daemon.sh stop
        ARGFLAG=4
        ;;
    -r | --restart)
        # Stop and start daemon
        ./scripts/shell/bkp_daemon.sh stop
        # Start daemon as a background process
        cecho -c green -t "Starting backup daemon..."
        nohup ./scripts/shell/bkp_daemon.sh start > bkp/bkp.out &
        ARGFLAG=5
        ;;
    -t | --test)
        ./scripts/shell/bkp_daemon.sh status
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
    chmod +x ./scripts/shell/bkp_daemon.sh
    echo "=========================="
    echo "Starting backup daemon..."
    if ! test -d "bkp"; then
        cecho -c yellow -t "Creating bkp directory..."
        mkdir bkp
    fi
    nohup ./scripts/shell/bkp_daemon.sh start > bkp/bkp.out &
    cecho -c green -t "Backup daemon started!"
    echo
    echo "Usage: ./start.sh [OPTION]"
    echo "For more options, run ./start.sh --help"
    echo
    echo "You can view daemon logs in ./bkp/logs/TRAPP-DAEMON.log"
    echo "You can view any daemon output in ./bkp/bkp.out"
    echo "=========================="
fi
# Unset all variables
unset arch
unset bat_path
unset gum_binary_links
unset url
unset ARGFLAG
# Exit program
cecho -c green -t "Program exited. Deactivating virtual environment..."
unalias cecho
deactivate

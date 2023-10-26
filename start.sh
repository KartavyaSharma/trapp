#!/usr/bin/env bash
#^ Dynamically find bash path

# Print welcome message
python3 ./scripts/utils/welcome.py

cecho_path=$(realpath ./scripts/shell/echo.sh)
chmod +x $cecho_path
cecho () {
    ${cecho_path} "$@"
}

quit () {
    error=$@
    # Unset all variables
    unset arch
    unset bat_path
    unset gum_binary_links
    unset url
    unset ARGFLAG
    deactivate
    if [[ "$error" != "" ]]; then
        cecho -c red -t "Program exited with error. Deactivating virtual environment..."
        cecho -c red -t "Error: $error"
    else
        # Exit program
        cecho -c green -t "Program exited. Deactivating virtual environment..."
    fi
    return
}

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
            quit "$(env) folder exists, but activate file missing. Please delete the env folder and run ./start.sh again."
            return
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
    cecho -c yellow -t "Dependency requirements not satisfied. Installing dependencies..."
    pip3 install -r requirements.txt
else
    cecho -c green -t "All dependencies are present!"
fi

# Check if logs directory exists
if ! test -d "logs"; then
    cecho -c yellow -t "Creating logs directory..."
    mkdir logs
fi

# Check if gum is installed
if ! command -v ./bin/gum &>/dev/null; then
    cecho -c yellow -t "charmbracelet/gum was not found. Installing..."
    echo "Determining system architecture..."
    arch=$(uname -s -m)
    if test "${gum_binary_links["$arch"]+isset}"; then
        url="${gum_binary_links["$arch"]}"
    else
        quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
        return
    fi
    cecho -c yellow -t "Fetching gum binary..."
    mkdir bin && cd bin
    wget "$url"
    tar -xzf $(basename "$url") gum
    chmod 755 $(basename "$url" | awk -F'.' '{print $1}' | awk -F'_' '{print $1}')
    cecho -c green -t "Installed gum!"
    echo "Cleaning up..."
    rm $(basename "$url")
    find . ! -name 'gum' -type f -exec rm -f {} +
    find . ! -name 'gum' -name '.' -name '..' -type d -exec rm -rf {} +
    cd ..
else
    if ! test -d ".cache"; then
        cecho -c green -t "WOW, you already have the gum library you SHELL fiend!"
    else
        cecho -c green -t "Gum library detected!"
    fi
fi

# If arch is Darwin check if brew is installed
arch=$(uname -s)
if [[ $arch == "Darwin" ]]
then
    if ! (command -v brew) > /dev/null
    then
        cecho -c yellow -t "brew was not found. Do you want to install it? (Y/n)"
        install_brew_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_brew_choice" == "YES" ]];
        then
            cecho -c yellow -t "Installing brew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            cecho -c yellow -t "brew was not installed. Please install brew manually to use trapp."
        fi
    else
        cecho -c green -t "Homebrew found!"
    fi

    check_openssl=$(brew list openssl@1.1)
    if [[ "$check_openssl" == "" ]]
    then
        cecho -c yellow -t "openssl@1.1 was not found. Do you want to install it? (Y/n)"
        install_openssl_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_openssl_choice" == "YES" ]];
        then
            cecho -c yellow -t "Installing openssl@1.1..."
            brew install openssl@1.1
        else
            cecho -c yellow -t "openssl@1.1 was not installed. Please install openssl@1.1 manually to use trapp."
        fi
    else
        cecho -c green -t "OPENSSL@1.1 found!"
    fi
fi

# Check if wget is installed
if ! (command -v wget) > /dev/null
then
    cecho -c red -t "wget was not found. Do you want to install it? (Y/n)"
    install_wget_choice=$(./bin/gum choose "YES" "NO")
    if [[ "$install_wget_choice" == "YES" ]];
    then
        cecho -c yellow -t "Installing wget..."
        if [[ $arch == "Darwin" ]]
        then
            brew install wget
        elif [[ $arch == "Linux" ]]
        then
            sudo apt-get install wget
        else
            quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
            return
        fi
    else
        cecho -c yellow -t "wget was not installed. Please install wget manually to use trapp."
    fi
else
    cecho -c green -t "WGET found!"
fi

# Set a flag so that the "WOW, ..." print does not run every time.
if ! test -d ".cache"; then
    echo "Creating cache file..."
    mkdir .cache && touch ./.cache/gum.flag && echo "1" >>./.cache/gum.flag
fi

# Bat binary path
bat_path="./bin/bat/bin/bat"
bat_commit="fc95468" # Latest commit trapp is tested with
# Check if sharkdp/bat is installed
if ! command -v $bat_path &>/dev/null; then
    cecho -c yellow -t "sharkdp/bat was not found. Installing..."
    # Check if system has rust installed
    if ! command -v rustc &>/dev/null; then
        cecho -c yellow -t "Rust not found. Trapp requires rust to work. Installing..."
        sleep 3
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
    echo "Cleaning up..."
    rm -rf bat
fi

# Check if docker is installed and running
if ! (command -v docker) > /dev/null
then
    cecho -c yellow -t "Docker was not found."
    arch=$(uname -s)
    if [[ $arch == "Darwin" ]]; then
        # Ask user to install Docker
        cecho -c yellow -t "Docker was not found, do you want to install it using Homebrew?"
        install_docker_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_docker_choice" == "YES" ]];
        then
            cecho -c yellow -t "Installing Docker..."
            brew install --cask docker
        else
            quit "Docker was not installed. Please install Docker manually to use trapp."
            return
        fi
        cecho -c green -t "Docker installed!"
        # Check if colima is installed
        colima_ver="0.5.6"
        if ! (command -v colima) > /dev/null
        then
            cecho -c yellow -t "colima was not found. Installing..."
            # download binary
            mkdir bin/colima && cd bin/colima
            curl -LO https://github.com/abiosoft/colima/releases/download/v$colima_ver/colima-$(uname)-$(uname -m)
            # Check if usr/local/bin is exists, if not create it
            if ! test -d "/usr/local/bin"; then
                cecho -c yellow -t "Creating /usr/local/bin..."
                sudo mkdir /usr/local/bin
            fi
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
            cd ..
        else
            cecho -c green -t "Colima found!"
        fi
    elif [[ $arch == "Linux" ]]; then
        # Installing docker using the convenience script
        curl -fsSL https://get.docker.com -o ./bin/get-docker.sh
        cecho -c yellow -t "Installing docker... (This requires sudo)"
        sleep 3
        sudo sh ./bin/get-docker.sh
        sudo groupadd docker
        sudo usermod -aG docker ${USER}
        su - ${USER} # Refresh user group
        if [ ! $(groups) =~ "docker" ]; then
            quit "Failed to add user to docker group!"
            return
        fi
        # Test if docker is working as it should
        docker run hello-world
        if [ $? -ne 0 ]; then
            quit "Docker failed hello-world test!"
            return
        fi
        cecho -c green -t "Docker installed!"
    else
        quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
        return
    fi
fi

if [[ "$(docker info 2>&1)" =~ "Cannot connect to the Docker daemon" ]]
then
    arch=$(uname -s)
    if [[ $arch == "Darwin" ]]
    then
        cecho -c yellow -t "Docker runtime not detected. Starting runtime (colima)..."
        # start colima
        colima start
    elif [[ $arch == "Linux" ]]
    then
        cecho -c yellow -t "Docker runtime not detected. Starting runtime (docker engine)..."
        sudo service docker start
    else
        quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
        return
    fi
else
    cecho -c green -t "Docker runtime found!"
fi

# Check if Google Chrome is installed on system (only required for autofill)
# Check if arch is linux
arch=$(uname -s)
if [[ "$arch" == "Linux" ]]; then
    chrome_ver=$(google-chrome --version)
    if [[ "$chrome_ver" == "" ]];
    then
        # Ask user to install Google Chrome
        cecho -c yellow -t "Google Chrome was not found, do you want to install it using Homebrew?"
        install_chrome_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_chrome_choice" == "YES" ]];
        then
            cecho -c yellow -t "Google Chrome was not found. Installing..."
            sudo apt update
            sudo apt install -y unzip xvfb libxi6 libgconf-2-4
            sudo apt install default-jdk
            sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add 
            sudo bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list" 
            sudo apt -y update 
            sudo apt -y install google-chrome-stable
            chrome_ver=$(google-chrome --version)
        else
            cecho -c yellow -t "Google Chrome was not installed. Please install Google Chrome manually to use autofill."
        fi
    else
        export TRAPP_CHROME_VER=$chrome_ver
        cecho -c green -t "Google Chrome found!"
    fi
elif [[ "$arch" == "Darwin" ]]; then
    chrome_ver=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version)
    if [[ "$chrome_ver" == "" ]];
    then
        # Ask user to install Google Chrome
        cecho -c yellow -t "Google Chrome was not found, do you want to install it using Homebrew?"
        install_chrome_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_chrome_choice" == "YES" ]];
        then
            cecho -c yellow -t "Installing Google Chrome..."
            brew install --cask google-chrome
            chrome_ver=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version)
        else
            cecho -c yellow -t "Google Chrome was not installed. Please install Google Chrome manually to use autofill."
        fi
    else
        export TRAPP_CHROME_VER=$chrome_ver
        cecho -c green -t "Google Chrome found!"
    fi
else
    quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
    return
fi

# Check post-install
if [[ "$chrome_ver" == "" ]];
then
    # Ask user to install Google Chrome
    cecho -c yellow -t "Google Chrome was not installed. Please install Google Chrome manually to use autofill."
else
    export TRAPP_CHROME_VER=$chrome_ver
    cecho -c green -t "Chrome installed successfully!"
fi

# Check if chrome-driver is installed in bin/chrome-driver
if [ -d "bin/chrome-driver" ]; then
    cecho -c green -t "Chrome driver found!"
else
    cecho -c yellow -t "Chrome driver not found. Installing..."
    mkdir bin/chrome-driver
    python3 scripts/utils/install_chrome_driver.py
    # Check if the script ran successfully
    if [ $? -ne 0 ]; then
        # rm -rf bin/chrome-driver
        quit "scripts/utils/install_chrome_driver.py failed. Please check the logs for more information."
        return
    fi
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
        echo -e "Removing .cache\nRemoving pid\nRemoving logs\nRemoving TRAPP-DAEMON.pid\nRemoving bkp.out"
        rm -rf .cache bkp/pid bkp/logs bkp/bkp.out bkp 
        echo "Removing preview files..."
        # Delete any preview files with the .preview extension
        find . -type f -name "*.preview" -delete
        # Removing all dependencies
        echo "Removing dependencies..."
        rm -rf env
        rm -rf bin
        rm -rf bat
        rm -rf logs
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
        quit "Invalid option: $arg"
        return
        ;;
    esac
done
if [ $ARGFLAG -eq 0 ]; then
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

quit

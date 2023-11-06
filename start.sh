#!/usr/bin/env bash
#^ Dynamically find bash path

help() {
    cat <<EOF

trapp 1.0.0
A tracker for your job applications

Usage: ./start.sh [OPTIONS]

OPTIONS:
    -b, --wbkp
        Run and start backup daemon
    
    -c, --clean
        Clean up cache and daemon files

    -s, --stop
        Stop backup daemon
    
    -r, --restart
        Restart backup daemon
    
    -t, --test
        Test if backup daemon is running
    
    -f, --fix <service>
        Fix any broken trapp service. Currently supported services:
            colima
            redis
    
    --build-dependencies
        Build pip3 dependencies for trapp on the current system
    
    -h, --help
        Print help and exit

EOF
}

# Check if --help or -h is passed as an argument
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    help
    exit 0
fi

# Print welcome message
python3 ./scripts/utils/welcome.py

cecho_path=$(realpath ./scripts/shell/echo.sh)
chmod +x $cecho_path
cecho() {
    ${cecho_path} "$@"
}

clean() {
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
}

# Check if --clean or -c is passed as an argument
if [[ "$1" == "-c" ]] || [[ "$1" == "--clean" ]]; then
    clean
    exit 0
fi

# Check if --build-dependencies is passed as an argument
if [[ "$1" == "--build-dependencies" ]]; then
    ./scripts/shell/build_dependencies.sh
    exit 0
fi

quit() {
    error=$@
    # Unset all variables
    unset arch
    unset bat_path
    unset gum_binary_links
    unset url
    unset ARGFLAG
    # deactivate
    if [[ "$error" != "" ]]; then
        cecho -c red -t "Program exited with error. Deactivating virtual environment..."
        cecho -c red -t "Error: $error"
        help
        exit 1
    else
        # Exit program
        cecho -c green -t "Program exited. Deactivating virtual environment..."
    fi
    exit 0
}

# Create logs, .cache, bkp, and bin directories in one go if none exist
if ! test -d "logs" || ! test -d ".cache" || ! test -d "bkp" || ! test -d "bin"; then
    cecho -c yellow -t "Creating directories..."
    mkdir -p logs .cache bkp bin
fi

# Check system architecture
arch=$(uname -s)
if [[ "$arch" == "Linux" ]]; then
    linux_required_packages=("wget" "unzip" "build-essential" "python3-pip" "python3-venv" "tar")
    missing_linux_packages=()

    # Check if required packages are installed
    for package in "${linux_required_packages[@]}"; do
        if ! dpkg -s "$package" >/dev/null 2>&1; then
            missing_linux_packages+=("$package")
        else
            cecho -c green -t "$package found!"
        fi
    done

    # Prompt user to install missing packages
    if [[ "${#missing_linux_packages[@]}" -ne 0 ]]; then
        cecho -c yellow -t "The following packages are required to run trapp: ${missing_linux_packages[*]}"
        read -p "Do you want to install them? (Y/n)" install_packages_choice
        if [[ "$install_packages_choice" == "Y" ]]; then
            cecho -c yellow -t "Installing packages..."
            sudo apt-get install "${missing_linux_packages[@]}"
        else
            quit "Required packages not installed. Please install them manually to use trapp."
        fi
    fi
elif [[ "$arch" == "Darwin" ]]; then
    # Make sure brew is installed
    if ! (command -v brew) >/dev/null; then
        cecho -c yellow -t "brew was not found. Do you want to install it? (Y/n)"
        install_brew_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_brew_choice" == "YES" ]]; then
            cecho -c yellow -t "Installing brew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            cecho -c yellow -t "brew was not installed. Please install brew manually to use trapp."
        fi
    else
        cecho -c green -t "Homebrew found!"
    fi

    darwin_required_packages=("wget" "unzip" "python3" "tar" "openssl@1.1" "coreutils" "docker")
    missing_darwin_packages=()

    # Check if required packages are installed
    for package in "${darwin_required_packages[@]}"; do
        # Check if not in brew AND not in command in single if statement
        if ! brew ls --versions "$package" >/dev/null 2>&1 && ! (command -v "$package") >/dev/null; then
            missing_darwin_packages+=("$package")
        else
            cecho -c green -t "$package found!"
        fi
    done

    # Prompt user to install missing packages
    if [[ "${#missing_darwin_packages[@]}" -ne 0 ]]; then
        cecho -c yellow -t "The following packages are required to run trapp: ${missing_darwin_packages[*]}"
        read -p "Do you want to install them? (Y/n)" install_packages_choice
        if [[ "$install_packages_choice" == "Y" ]]; then
            cecho -c yellow -t "Installing packages..."
            brew install "${missing_darwin_packages[@]}"
        else
            quit "Required packages not installed. Please install them manually to use trapp."
        fi
    fi
else
    quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
fi

# Check if we are in a virtual environment
# Check if python3 in virtual environment exists
if ! command -v ./env/bin/python3 &>/dev/null; then
    cecho -c yellow -t "Virtual environment not found. Creating a new environment..."
    python3 -m venv env
    cecho -c green -t "New virtual environment created!"
else
    cecho -c green -t "Virtual environment found!"
fi

py () {
    $(realpath ./env/bin/python3) "$@"
}

# Check if requirements are satisfied in virtual environment
output=$(py ./tests/test_requirements.py)
if [ $? -ne 0 ]; then
    cecho -c yellow -t "Error: python3 ./tests/test_requirements.py failed with output^"
    echo "Dependency requirements not satisfied. Installing dependencies..."
    ./scripts/shell/load_dependencies.sh
else
    cecho -c green -t "All dependencies are present!"
fi

# Check if gum is installed
if ! command -v ./bin/gum &>/dev/null; then
    cecho -c yellow -t "charmbracelet/gum was not found. Installing..."
    echo "Determining system architecture..."
    arch=$(uname -s -m)
    url=$(py -c "from constants import GUM_BINARY_LINKS as links; print(links['$arch']) if '$arch' in links else print('Invalid architecture')")
    if [[ "$url" == "Invalid architecture" ]]; then
        quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
    fi
    cecho -c yellow -t "Fetching gum binary..."
    cd bin
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

# Set a flag so that the "WOW, ..." print does not run every time.
if ! test -d ".cache"; then
    echo "Creating cache file..."
    touch ./.cache/gum.flag && echo "1" >>./.cache/gum.flag
fi

# On linux, don't build the bat binary, download it instead
arch=$(uname -s)
# Bat binary path
bat_path="./bin/bat/bat"
# Check if bat binary exists
if ! test -f "$bat_path"; then
    cecho -c yellow -t "bat was not found. Installing..."
    # Get binary from link in constants file
    if [[ $arch == "Linux" ]]; then
        bat_binary_link=$(py -c "from constants import BAT_LINUX_BINARY_LINK as link; print(link)")
    else
        bat_binary_link=$(py -c "from constants import BAT_AMD_DARWIN_BINARY_LINK as link; print(link)")
    fi
    cecho -c yellow -t "Fetching bat binary..."
    cd bin
    mkdir -p bat && cd bat
    wget $bat_binary_link
    tar -xzf $(basename "$bat_binary_link")
    cd $(basename "$bat_binary_link" | awk -F'.tar.gz' '{print $1}')
    mv bat ../ && cd ../
    chmod +x bat 
    cecho -c green -t "Installed bat!"
    echo "Cleaning up..."
    find . ! -name 'bat' -type f -exec rm -f {} +
    find . ! -name 'bat' -name '.' -name '..' -type d -exec rm -rf {} +
    cd ../..
else
    cecho -c green -t "Bat binary found!"
fi

# Check if docker is installed and running
if ! (command -v docker) >/dev/null; then
    if [[ $arch == "Linux" ]]; then
        cecho -c yellow -t "Docker was not found."
        # Installing docker using the convenience script
        curl -fsSL https://get.docker.com -o ./bin/get-docker.sh
        cecho -c yellow -t "Installing docker... (This requires sudo)"
        sleep 3
        sudo sh ./bin/get-docker.sh
        sudo groupadd docker
        sudo usermod -aG docker ${USER}
        if [ ! $(groups) =~ "docker" ]; then
            quit "Failed to add user to docker group!"
        fi
        # Test if docker is working as it should
        sudo docker run hello-world
        if [ $? -ne 0 ]; then
            quit "Docker failed hello-world test!"
        fi
        cecho -c green -t "Docker installed!"
        cecho -c yellow -t "Restarting trapp, run ./start.sh again..."
        newgrp docker
    else
        quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
    fi
fi

arch=$(uname -s)
if [[ $arch == "Darwin" ]]; then
    # Check if docker runtime is present
    if [[ "$(docker ps 2>&1)" =~ "Cannot connect to the Docker daemon" ]]; then
        # Check if colima is installed
        colima_ver="0.5.6"
        if ! (command -v colima) >/dev/null; then
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
            if [ -w "/usr/local/bin" ]; then
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
    fi
fi

if [[ "$(docker ps 2>&1)" =~ "Cannot connect to the Docker daemon" ]]; then
    arch=$(uname -s)
    if [[ $arch == "Darwin" ]]; then
        cecho -c yellow -t "Docker runtime not detected. Starting runtime (colima)..."
        # start colima
        colima start
    elif [[ $arch == "Linux" ]]; then
        cecho -c yellow -t "Docker runtime not detected. Starting runtime (docker engine)..."
        sudo service docker start
    else
        quit "Invalid architecture: $arch. trapp is only supported on x86_64 and arm64 versions of Darwin and Linux."
    fi
else
    cecho -c green -t "Docker runtime found!"
fi

# Check if Google Chrome is installed on system (only required for autofill)
# Check if arch is linux
arch=$(uname -s)
if [[ "$arch" == "Linux" ]]; then
    chrome_ver=$(google-chrome --version)
    if [[ "$chrome_ver" == "" ]]; then
        # Ask user to install Google Chrome
        cecho -c yellow -t "Google Chrome was not found, do you want to install it? Google Chrome is also required for Ubuntu Server users."
        install_chrome_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_chrome_choice" == "YES" ]]; then
            cecho -c yellow -t "Google Chrome was not found. Installing..."
            wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
            sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
            sudo apt update
            sudo apt -y install google-chrome-stable
            chrome_ver=$(google-chrome --version)
        else
            quit "Google Chrome was not installed. Please install Google Chrome manually to use autofill."
        fi
    else
        export TRAPP_CHROME_VER=$chrome_ver
        cecho -c green -t "Google Chrome found!"
    fi
elif [[ "$arch" == "Darwin" ]]; then
    chrome_ver=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version)
    if [[ "$chrome_ver" == "" ]]; then
        # Ask user to install Google Chrome
        cecho -c yellow -t "Google Chrome was not found, do you want to install it using Homebrew?"
        install_chrome_choice=$(./bin/gum choose "YES" "NO")
        if [[ "$install_chrome_choice" == "YES" ]]; then
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
fi

# Check post-install
if [[ "$chrome_ver" == "" ]]; then
    # Ask user to install Google Chrome
    cecho -c yellow -t "Google Chrome was not installed. Please install Google Chrome manually to use autofill."
else
    export TRAPP_CHROME_VER=$chrome_ver
fi

# Check if chrome-driver is installed in bin/chrome-driver
if [ -d "bin/chrome-driver" ]; then
    cecho -c green -t "Chrome driver found!"
else
    cecho -c yellow -t "Chrome driver not found. Installing..."
    mkdir bin/chrome-driver
    py scripts/utils/install_chrome_driver.py
    # Check if the script ran successfully
    if [ $? -ne 0 ]; then
        # rm -rf bin/chrome-driver
        quit "scripts/utils/install_chrome_driver.py failed. Please check the logs for more information."
    fi
fi

echo
ARGFLAG=0
# for arg in "$@"; do
while [[ $# -gt 0 ]]; do
    case $1 in
    -b | --wbkp)
        echo "Running program with backup option..."
        py runner.py wbkp
        ARGFLAG=1
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
        nohup ./scripts/shell/bkp_daemon.sh start >bkp/bkp.out &
        ARGFLAG=5
        ;;
    -t | --test)
        ./scripts/shell/bkp_daemon.sh status
        ARGFLAG=6
        ;;
    -f | --fix)
        shift # Remove the --fix argument
        service=$1
        if [[ "$service" == "" ]]; then
            quit "No service specified!"
        fi
        cecho -c yellow -t "Fixing $service..."
        if [[ "$service" == "colima" ]]; then
            status=$(limactl list | grep colima | awk -F' ' '{print $2}')
            cecho -c yellow -t "Colima cotainer status: $status"
            if [[ "$status" == "Broken" ]]; then
                limactl factory-reset colima
                status=$(limactl list | grep colima | awk -F' ' '{print $2}')
                if [[ "$status" == "Broken" ]]; then
                    quit "Failed to fix colima!"
                else
                    cecho -c green -t "Colima fixed!"
                fi
            else
                cecho -c green -t "Colima is not broken!"
                quit
            fi
        elif [[ "$service" == "redis" ]]; then
            docker_redis_metadata=$(py -c "from constants import REDIS_CONTAINER_NAME, REDIS_DATA_DIR; print(REDIS_CONTAINER_NAME, REDIS_DATA_DIR)")
            container_name=$(echo $docker_redis_metadata | awk -F' ' '{print $1}')
            data_volume_name=$(echo $docker_redis_metadata | awk -F' ' '{print $2}')
            status=$(docker inspect -f '{{.State.Status}}' "$container_name" 2>&1)
            cecho -c yellow -t "Redis container status: $status"
            if [[ "$status" =~ "No such object" ]]; then
                quit "No redis service found to fix!"
            else
                # Stop and remove redis container
                docker rm -f $container_name 2>&1
                docker volume rm $data_volume_name 2>&1
                cecho -c green -t "Redis container removed!"
                cecho -c green -t "To restart redis, run trapp again."
            fi
            quit
        else
            quit "Invalid service: $service"
        fi
        ;;
    *)
        quit "Invalid option: $arg"
        ;;
    esac
    shift
done
if [ $ARGFLAG -eq 0 ]; then
    py runner.py
elif [ $ARGFLAG -eq 1 ]; then
    chmod +x ./scripts/shell/bkp_daemon.sh
    echo "=========================="
    echo "Starting backup daemon..."
    if ! test -d "bkp"; then
        cecho -c yellow -t "Creating bkp directory..."
        mkdir bkp
    fi
    nohup ./scripts/shell/bkp_daemon.sh start >bkp/bkp.out &
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

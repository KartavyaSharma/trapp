#!/usr/bin/env bash
#^ Dynamically find bash path

cecho_path=$(realpath $TRAPP_HOME/scripts/shell/echo.sh)
chmod +x $cecho_path
cecho() {
    ${cecho_path} "$@"
}

# Set architecture
arch=$(uname -s)

# Check if ~/.trapp exists
if ! test -d ~/.trapp; then
    cecho -c yellow -t "Creating ~/.trapp..."
    mkdir ~/.trapp
fi

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

clean() {
    echo "Cleaning up..."
    echo -e "Removing .cache\nRemoving pid\nRemoving logs\nRemoving TRAPP-DAEMON.pid\nRemoving bkp.out"
    rip $TRAPP_HOME/.cache $TRAPP_HOME/bkp/pid $TRAPP_HOME/bkp/logs $TRAPP_HOME/bkp/bkp.out bkp
    echo "Removing preview files..."
    # Delete any preview files with the .preview extension
    echo "The following files will be deleted:"
    find $TRAPP_HOME -type f -name "*.preview" -print
    # Ask user if they want to delete preview files
    read -p "Are you sure you want to delete these files? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find $TRAPP_HOME -type f -name "*.preview" -delete
        echo "Deleted preview files!"
    else
        echo "Preview files not deleted!"
    fi
    # Removing all dependencies
    echo "Removing dependencies..."
    rip $TRAPP_HOME/env
    rip $TRAPP_HOME/bin
    rip $TRAPP_HOME/logs
    rip $TRAPP_HOME/bkp
    rip $TRAPP_HOME/__pycache__
    echo
}

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
        cecho -c red -t "Program exited with error." 
        cecho -c red -t "Error: $error"
        help
        exit 1
    else
        # Exit program
        cecho -c green -t "Program exited." 
    fi
    exit 0
}

# Check if --help or -h is passed as an argument
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    help
    exit 0
fi

# Print welcome message
python3 $TRAPP_HOME/scripts/utils/welcome.py

# Check if --clean or -c is passed as an argument
if [[ "$1" == "-c" ]] || [[ "$1" == "--clean" ]]; then
    clean
    exit 0
fi

# Create logs, .cache, bkp, and bin directories in one go if none exist
if ! test -d "$TRAPP_HOME/logs" || ! test -d "$TRAPP_HOME/.cache" || ! test -d "$TRAPP_HOME/bkp" || ! test -d "$TRAPP_HOME/bin"; then
    cecho -c yellow -t "Creating directories..."
    mkdir -p $TRAPP_HOME/logs $TRAPP_HOME/.cache $TRAPP_HOME/bkp $TRAPP_HOME/bin
fi

# Check if we are in a virtual environment
# Check if python3 in virtual environment exists
if ! command -v $TRAPP_HOME/env/bin/python3 &>/dev/null; then
    cecho -c yellow -t "Virtual environment not found. Creating a new environment..."
    python3 -m venv $TRAPP_HOME/env
    cecho -c green -t "New virtual environment created!"
else
    cecho -c green -t "Virtual environment found!"
fi

# Check if --build-dependencies is passed as an argument
if [[ "$1" == "--build-dependencies" ]]; then
    $TRAPP_HOME/scripts/shell/build_dependencies.sh
    exit 0
fi

# Check if requirements are satisfied in virtual environment
output=$($TRAPP_HOME/env/bin/python3 $TRAPP_HOME/tests/test_requirements.py)
if [ $? -ne 0 ]; then
    cecho -c yellow -t "Error: python3 ./tests/test_requirements.py failed with output^"
    echo "Dependency requirements not satisfied. Installing dependencies..."
    $TRAPP_HOME/scripts/shell/load_dependencies.sh
else
    cecho -c green -t "All dependencies are present!"
fi


if [[ "$(docker ps 2>&1)" =~ "Cannot connect to the Docker daemon" ]]; then
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
        install_chrome_choice=$(gum choose "YES" "NO")
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
if [ -d "$TRAPP_HOME/bin/chrome-driver" ]; then
    cecho -c green -t "Chrome driver found!"
else
    cecho -c yellow -t "Chrome driver not found. Installing..."
    mkdir $TRAPP_HOME/bin/chrome-driver
    $TRAPP_HOME/env/bin/python3 $TRAPP_HOME/scripts/utils/install_chrome_driver.py
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
        $TRAPP_HOME/env/bin/python3 runner.py wbkp
        ARGFLAG=1
        ;;
    -s | --stop)
        $TRAPP_HOME/scripts/shell/bkp_daemon.sh stop
        ARGFLAG=4
        ;;
    -r | --restart)
        # Stop and start daemon
        $TRAPP_HOME/scripts/shell/bkp_daemon.sh stop
        # Start daemon as a background process
        cecho -c green -t "Starting backup daemon..."
        nohup $TRAPP_HOME/scripts/shell/bkp_daemon.sh start >bkp/bkp.out &
        ARGFLAG=5
        ;;
    -t | --test)
        $TRAPP_HOME/scripts/shell/bkp_daemon.sh status
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
            docker_redis_metadata=$(py -c "import sys; sys.path.append('$TRAPP_HOME'); from constants import REDIS_CONTAINER_NAME, REDIS_DATA_DIR; print(REDIS_CONTAINER_NAME, REDIS_DATA_DIR)")
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
    $TRAPP_HOME/env/bin/python3 runner.py
elif [ $ARGFLAG -eq 1 ]; then
    chmod +x $TRAPP_HOME/scripts/shell/bkp_daemon.sh
    echo "=========================="
    echo "Starting backup daemon..."
    if ! test -d "$TRAPP_HOME/bkp"; then
        cecho -c yellow -t "Creating bkp directory..."
        mkdir $TRAPP_HOME/bkp
    fi
    nohup $TRAPP_HOME/scripts/shell/bkp_daemon.sh start >bkp/bkp.out &
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

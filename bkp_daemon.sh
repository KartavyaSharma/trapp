#!/bin/bash

# Define the daemon name.
daemonName="TRAPP-DAEMON"

# Define pid and log directories
pidDir="./bkp/pid"
pidFile="$pidDir/$daemonName.pid"

logDir="./bkp/logs"

# To use a regular log file.
logFile="$logDir/$daemonName.log"

# Log maxsize in KB
logMaxSize=1024 # 1mb
runInterval=20 # In seconds

# TODO: In the future, add support to backup to S3 or Google Drive
# Define variables for remote backup here

# Define local directory to backup
trapp_local="${TRAPP_LOCAL:-$HOME/.trapp}"
trapp_local_dir="bkp"
trapp_local_path="$trapp_local/$trapp_local_dir"

# Define backup filename bkp-YYYY-MM-DD-HH-MM-SS.csv
trapp_bkp_file="bkp-$(date +"%Y-%m-%d-%H-%M-%S").csv"
# Define csv to tar filename <trapp_bkp_file>.tar.gz
trapp_tar_file="$trapp_bkp_file.tar.gz"

doCommands() {
    # This is where you put all the commands for the daemon.
    echo "Running commands."
}

myPid=$$

initDaemon() {
    # Run through the init script.
    cecho -c green -t "Starting init script..."
    python3 init.py # TODO
}

setupDaemon() {
    # Make sure that the directories work.
    if [ ! -d "$pidDir" ]; then
        mkdir "$pidDir"
    fi
    if [ ! -d "$logDir" ]; then
        mkdir "$logDir"
    fi
    if [ ! -f "$logFile" ]; then
        touch "$logFile"
    else
        # Check to see if we need to rotate the logs.
        size=$(($(ls -l "$logFile" | cut -d " " -f 8) / 1024))
        if [[ $size -gt $logMaxSize ]]; then
            mv $logFile "$logFile.old"
            touch "$logFile"
        fi
    fi
}

startDaemon() {
    # Start the daemon.
    setupDaemon # Make sure the directories are there.
    checkDaemon
    if [[ "$?" -eq 1 ]]; then
        echo -e " * \033[31;5;148mError\033[39m: $daemonName is already running."
        exit 1
    fi
    echo " * Starting $daemonName with PID: $myPid."
    echo "$myPid" > "$pidFile"
    log '*** '$(date +"%Y-%m-%d")": Starting up $daemonName."

    # Start the loop.
    loop
}

stopDaemon() {
    # Stop the daemon.
    checkDaemon
    if [[ "$?" -eq 0 ]]; then
        echo -e " * \033[31;5;148mError\033[39m: $daemonName is not running."
        exit 1
    fi
    echo " * Stopping $daemonName"

    if [[ ! -z $(cat $pidFile) ]]; then
        kill -9 $(cat "$pidFile") &>/dev/null
    fi

    log '*** '$(date +"%Y-%m-%d")": $daemonName stopped."
    echo " * Stopped $daemonName with PID: $(cat $pidFile)."
    echo
}

statusDaemon() {
    # Query and return whether the daemon is running.
    checkDaemon
    if [[ "$?" -eq 1 ]]; then
        echo " * $daemonName is running."
    else
        echo " * $daemonName isn't running."
    fi
    echo
    exit 0
}

restartDaemon() {
    # Restart the daemon.
    checkDaemon
    if [[ "$?" -eq 0 ]]; then
        # Can't restart it if it isn't running.
        echo "$daemonName isn't running."
        exit 1
    fi
    stopDaemon
    startDaemon
    echo

}

checkDaemon() {
    # Check to see if the daemon is running.
    # This is a different function than statusDaemon
    # so that we can use it other functions.
    if [ -z "$oldPid" ]; then
        return 0
    elif [[ $(ps aux | grep "$oldPid" | grep -v grep) > /dev/null ]]; then
        if [ -f "$pidFile" ]; then
            if [[ $(cat "$pidFile") = "$oldPid" ]]; then
                # Daemon is running.
                log "*** Found $daemonName with PID: $oldPid. Stopping..."
                return 1
            else
                # Daemon isn't running.
                log "*** No $daemonName found with PID: $oldPid."
                return 0
            fi
        fi
    elif [[ $(ps aux | grep "$daemonName" | grep -v grep | grep -v "$myPid" | grep -v "0:00.00") > /dev/null ]]; then
        # Daemon is running but without the correct PID. Restart it.
        log '*** '$(date +"%Y-%m-%d")": $daemonName running with invalid PID; restarting."
        restartDaemon
        return 1
    else
        # Daemon not running.
        return 0
    fi
    return 1
}

loop() {
    # This is the loop.
    now=$(date +%s)

    if [ -z $last ]; then
        last=$(date +%s)
    fi

    # Do everything you need the daemon to do.
    doCommands

    # Check to see how long we actually need to sleep for. If we want this to run
    # once a minute and it's taken more than a minute, then we should just run it
    # anyway.
    last=$(date +%s)

    # Set the sleep interval
    if [[ ! $((now - last + runInterval + 1)) -lt $((runInterval)) ]]; then
        sleep $((now - last + runInterval))
    fi

    # Startover
    loop
}

log() {
    # Generic log function.
    echo "$1" >>"$logFile"
}

################################################################################
# Parse the command.
################################################################################

if [ -f "$pidFile" ]; then
    oldPid=$(cat "$pidFile")
fi
# checkDaemon
case "$1" in
start)
    startDaemon
    ;;
stop)
    stopDaemon
    ;;
status)
    statusDaemon
    ;;
restart)
    restartDaemon
    ;;
init)
    initDaemon
    ;;
*)
    echo -e "\033[31;5;148mError\033[0m: usage $0 { start | stop | restart | status | init}"
    exit 1
    ;;
esac

exit 0

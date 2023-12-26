#!/usr/bin/env bash

# This script is used to execute a command in a running container.
# Usage: docker_exec.sh <container_name> <command>

cecho_path=$(realpath ./scripts/shell/echo.sh)
chmod +x $cecho_path
cecho () {
    ${cecho_path} "$@"
}

quit () {
    error=$@
    if [[ "$error" != "" ]]; then
        cecho -c red -t "Docker exec exited with error."
        cecho -c red -t "Error: $error"
    return
}

# Check if the container name is provided.
if [ -z "$1" ]; then
    quit "Please provide the container name."
    return
fi

# Check if the command is provided.
if [ -z "$2" ]; then
    quit "Please provide the command."
    return
fi

# Check if the container exists.
container_name=$1
container_id=$(docker ps -aqf "name=$container_name")
if [ -z "$container_id" ]; then
    quit "Container $container_name does not exist."
    return
fi

# Execute the command in the container.
command=$2
docker exec -it $container_id /bin/bash -c "$command"

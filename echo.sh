#!/bin/bash

# ANSI escape codes for text colors
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'

# Reset the text color to default
RESET='\033[0m'

# Parse command-line arguments
while getopts ":c:t:" opt; do
  case $opt in
  c)
    case "$OPTARG" in
    red) COLOR="$RED" ;;
    green) COLOR="$GREEN" ;;
    yellow) COLOR="$YELLOW" ;;
    *)
      echo "Invalid color specified. Use 'red', 'green', or 'yellow'." >&2
      exit 1
      ;;
    esac
    ;;
  t)
    TEXT="$OPTARG"
    ;;
  \?)
    echo "Usage: $0 -c {red|green|yellow} -t 'your text'"
    exit 1
    ;;
  esac
done

# Check if both color and text are provided
if [ -z "$COLOR" ] || [ -z "$TEXT" ]; then
  echo "Usage: $0 -c {red|green|yellow} -t 'your text'"
  exit 1
fi

# Print the text in the specified color
echo -e "${COLOR}${TEXT}${RESET}"

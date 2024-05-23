from pathlib import Path
import importlib.metadata
import warnings
import re

_REQUIREMENTS_PATH = Path(__file__).parent.with_name("requirements.txt")

with open(_REQUIREMENTS_PATH) as f:
    requirements = f.read().splitlines()

def extract_package_name(requirement):
    # Split by version specifiers and other extras
    main_part = re.split(r'[=<>!]', requirement)[0].strip()

    # Check for extras in square brackets
    if '[' in main_part and ']' in main_part:
        package, extras = main_part.split('[', 1)
        extras = extras.rstrip(']').split(',')
        return [package.strip()] + [extra.strip() for extra in extras]
    else:
        return [main_part]

# Function to check if a package is installed
def is_package_installed(package_name):
    for package in package_name:
        try:
            dist = importlib.metadata.distribution(package)
        except importlib.metadata.PackageNotFoundError:
            return False
    return True

# Filter out comments and empty lines
filtered_requirements = [
    req for req in requirements if req.strip() and not req.strip().startswith("#")
]

# Check if all requirements are satisfied
unsatisfied_requirements = [
    req for req in filtered_requirements if not is_package_installed(extract_package_name(req))
]

if unsatisfied_requirements:
    raise Exception(
        f"The following requirements are not satisfied: {', '.join(unsatisfied_requirements)}"
    )
else:
    print("All requirements are satisfied. Running the rest of the program...")

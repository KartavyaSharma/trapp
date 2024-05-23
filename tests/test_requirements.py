from pathlib import Path
import importlib.metadata
import warnings

_REQUIREMENTS_PATH = Path(__file__).parent.with_name("requirements.txt")

with open(_REQUIREMENTS_PATH) as f:
    requirements = f.read().splitlines()

# Function to check if a package is installed
def is_package_installed(package_name):
    try:
        importlib.metadata.version(package_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False

# Check if all requirements are satisfied
unsatisfied_requirements = [req for req in requirements if not is_package_installed(req)]

if unsatisfied_requirements:
    raise Exception(
        f"The following requirements are not satisfied: {', '.join(unsatisfied_requirements)}"
    )
else:
    print("All requirements are satisfied. Running the rest of the program...")

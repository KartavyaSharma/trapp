"""Test availability of required packages."""

from pathlib import Path

import warnings

with warnings.catch_warnings():
    # Ignore deprecated pkg_resources warning
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    import pkg_resources


_REQUIREMENTS_PATH = Path(__file__).parent.with_name("requirements.txt")

with open(_REQUIREMENTS_PATH) as f:
    requirements = f.read().splitlines()

# Check if all requirements are satisfied
unsatisfied_requirements = []
for requirement in requirements:
    try:
        pkg_resources.require(requirement)
    except pkg_resources.DistributionNotFound:
        unsatisfied_requirements.append(requirement)

if unsatisfied_requirements:
    raise Exception(
        f"The following requirements are not satisfied: {', '.join(unsatisfied_requirements)}")
else:
    print("All requirements are satisfied. Running the rest of the program...")

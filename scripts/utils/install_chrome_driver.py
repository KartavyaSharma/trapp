import constants
import httpx
import json
import os
import pathlib
import subprocess
import sys
import logging


# Make constants accessible to utils
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils import logger

# Determine system architecture
system_arch = subprocess.check_output(
    "uname -sm", shell=True
).decode("utf-8").strip()
# Get chrome-driver system architecture identifier using system_arch
system_arch_identifier = constants.CHROME_DRIVER_SYSTEM_ARCH_MAP[system_arch]


def set_chrome_driver_cache(versions_json: any = None, version_root: str = None) -> None:
    if not versions_json:
        # No cache file exists, create one
        print("No cache file exists, creating one...")
        subprocess.call(
            f"touch {constants.CHROME_DRIVER_VERSIONS_CACHE}", shell=True
        )
        empty_cache = {"timestamp": "", "url": ""}
        with open(constants.CHROME_DRIVER_VERSIONS_CACHE, "w") as cache:
            cache.write(json.dumps(empty_cache))
    else:
        print(
            f"Setting cache file with timestamp {versions_json['timestamp']}..."
        )
        possible_versions = [v['version'] for v in versions_json['versions'] if v['version'].startswith(version_root)]
        highest_version_suffix = sorted([int(v.split('.')[-1]) for v in possible_versions])[-1]
        resolved_version = f"{version_root}.{highest_version_suffix}"
        print(
            f"Setting cache file with chrome-driver version {resolved_version}..."
        )
        # Get chrome-driver url
        target_version_object = [v for v in versions_json['versions']
            if v['version'] == resolved_version
        ][0]['downloads']['chromedriver']
        target_version_url = [
            v for v in target_version_object if v['platform'] == system_arch_identifier
        ][0]['url']
        print(f"Setting cache file with chrome-driver url {target_version_url}...")
        constructed_cache = {
            "timestamp": versions_json['timestamp'], "url": target_version_url
        }
        # Overwrite cache file
        with open(constants.CHROME_DRIVER_VERSIONS_CACHE, "w") as cache:
            cache.write(json.dumps(constructed_cache))


def get_chrome_driver_url(version: str) -> str:
    r = httpx.get(constants.CHROME_DRIVER_VERSIONS_JSON)
    if r.status_code != 200:
        logger.LoggerBuilder\
            .build(log_level=logging.ERROR)\
            .error(f"Failed to get Chrome driver versions: returned status code: {r.status_code}")
        raise Exception("Failed to get Chrome driver versions")
    versions = json.loads(r.text)
    # Check if cache file exists
    if not os.path.exists(constants.CHROME_DRIVER_VERSIONS_CACHE):
        set_chrome_driver_cache()
    cache_file = json.loads(
        open(constants.CHROME_DRIVER_VERSIONS_CACHE, "r").read()
    )
    timestamp = versions['timestamp']
    cached_timestamp = cache_file['timestamp']
    if timestamp != cached_timestamp:
        set_chrome_driver_cache(versions, version)
        # Refresh cache file
        cache_file = json.loads(
            open(constants.CHROME_DRIVER_VERSIONS_CACHE, "r").read()
        )
        return cache_file['url']
    else:
        return cache_file['url']


def main():
    target_chrome_version = os.getenv('TRAPP_CHROME_VER')
    version = ".".join(target_chrome_version.split(' ')[2].split('.')[:-1])
    url = get_chrome_driver_url(version)
    # Download chrome-driver using wget into bin/chrome-driver/
    print(f"Downloading chrome-driver from {url}...")
    subprocess.call(
        f"wget -O {constants.PROJECT_ROOT}/bin/chrome-driver/chrome-driver.zip {url}",
        shell=True
    )
    # Unzip chrome-driver
    print("Unzipping chrome-driver...")
    subprocess.call(
        f"unzip {constants.PROJECT_ROOT}/bin/chrome-driver/chrome-driver.zip -d {constants.PROJECT_ROOT}/bin/chrome-driver/",
        shell=True
    )
    # Remove chrome-driver.zip
    print("Removing chrome-driver.zip...")
    subprocess.call(
        f"rm {constants.PROJECT_ROOT}/bin/chrome-driver/chrome-driver.zip",
        shell=True
    )
    # Make chrome-driver executable
    print("Making chrome-driver executable...")
    subprocess.call(
        f"chmod +x {constants.PROJECT_ROOT}/bin/chrome-driver/chromedriver-{system_arch_identifier}",
        shell=True
    )


if __name__ == '__main__':
    main()

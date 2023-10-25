import constants.constants as constants
import pathlib
import os
import re
import subprocess
import time

def has_gui() -> bool:
    """
    Check if running on a GUI

    @return: True if running on a GUI, False otherwise
    """
    # If system uname -s is Darwin, then we are on macOS
    if os.uname().sysname == "Darwin":
        return True
    check_xorg = subprocess.check_output(
        ["type", "Xorg"],
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        shell=True
    )
    if check_xorg == "Xorg is /usr/bin/Xorg\n":
        return True
    # Check /usr/share/xsessions
    try:
        check_xsessions = subprocess.check_output(
            ["\ls /usr/share/xsessions"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            shell=True
        )
    except Exception as e:
        return False
    # if not "No such file or directory" in check_xsessions:
    #     return True
    check_dir = subprocess.check_output(
        ["\ls", "/usr/bin/*session"],
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        shell=True
    )
    # If check_dir has only /usr/bin/byobu-select-session  /usr/bin/dbus-run-session, then we are on a server
    if check_dir == "/usr/bin/byobu-select-session  /usr/bin/dbus-run-session\n":
        return False
    elif "No such file or directory" not in check_dir:
        return True
    return False


def verify_headless_support() -> bool:
    """
    Check if xvfb is installed, if not, install it
    """
    if os.uname().sysname != "Darwin":
        print("Checking for xvfb...", end=' ')
        check_xvfb = subprocess.check_output(
            ["which xvfb-run"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            shell=True
        )
        if not "/usr/bin/xvfb-run\n" in check_xvfb:
            print("xvfb not installed, installing...")
            time.sleep(3)
            # Install xvfb
            subprocess.check_call(
                ["sudo", "apt-get", "install", "xvfb"],
                stderr=subprocess.DEVNULL,
            )
            # Install firefox dependency
            subprocess.check_call(
                ["sudo", "apt-get", "install", "firefox"],
                stderr=subprocess.DEVNULL,
            )
            # Verify xvfb installation
            check_xvfb = subprocess.check_output(
                ["which xvfb-run"],
                stderr=subprocess.DEVNULL,
                universal_newlines=True,
                shell=True
            )
        if "/usr/bin/xvfb-run\n" in check_xvfb:
            raise Exception("xvfb installation failed")
        else:
            print(f"{constants.OKGREEN}OK{constants.ENDC}")
        cache_file_path = pathlib.Path(constants.XVFB_CACHE_FLAG)
        if not cache_file_path.is_file():
            print(f"{constants.WARNING}You are running on an headless server, addtional dependencies are required{constants.ENDC}")
            print("The following packages will be installed:\nxserver-xephyr\ntigervnc-standalone-server\nx11-utils\ngnumeric")
            subprocess.check_call(
                ["sudo", "apt-get", "install", "xserver-xephyr",
                    "tigervnc-standalone-server", "x11-utils", "gnumeric"],
                stderr=subprocess.DEVNULL,
            )
            print(f"{constants.WARNING}Additional python dependencies are required.{constants.ENDC}")
            print("The following packages will be installed:\npyvirtualdisplay\npillow\nEasyProcess")
            subprocess.check_call(
                ["pip3", "install", "pyvirtualdisplay", "pillow", "EasyProcess"],
                stderr=subprocess.DEVNULL,
            )
            # Create xvfb cache file
            subprocess.check_call(
                ["touch", f"{constants.XVFB_CACHE_FLAG}"],
                stderr=subprocess.DEVNULL,
            )
    return True


def get_root_from_url(url: str) -> str:
    """
    Get root domain from URL

    @param url: URL to extract root domain from
    @return: Root domain of URL
    """
    regex = r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)"
    return re.findall(regex, url)[0]

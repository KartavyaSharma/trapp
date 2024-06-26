import constants
import curses
import datetime
import pathlib
import os
import re
import subprocess

from . import process as sp

OPTS = {"stderr": subprocess.DEVNULL, "universal_newlines": True, "shell": True}


def has_gui() -> bool:
    """
    Check if running on a GUI

    @return: True if running on a GUI, False otherwise
    """
    # If system uname -s is Darwin, then we are on macOS
    if os.uname().sysname == "Darwin":
        return True
    check_xorg = sp.SubprocessService(["type", "Xorg"], OPTS).check_output(output=True)
    if check_xorg == "Xorg is /usr/bin/Xorg\n":
        return True
    # Check /usr/share/xsessions
    try:
        check_xsessions = sp.SubprocessService(
            ["ls /usr/share/xsessions"], OPTS
        ).check_output(output=True)
    except Exception as e:
        return False
    # if not "No such file or directory" in check_xsessions:
    #     return True
    check_dir = sp.SubprocessService(["ls", "/usr/bin/*session"], OPTS).check_output(
        output=True
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
        check_xvfb = ""
        print("Checking for xvfb...", end=" ")
        try:
            check_xvfb = sp.SubprocessService(["which xvfb-run"], OPTS).check_output(
                output=True
            )
        except Exception as e:
            pass
        if not "/usr/bin/xvfb-run\n" in check_xvfb:
            print("xvfb not installed, installing...")
            # Install xvfb
            sp.SubprocessService(
                ["sudo", "apt-get", "install", "xvfb"], {"stderr": subprocess.DEVNULL}
            ).check_call()
            # Install firefox dependency
            sp.SubprocessService(
                ["sudo", "apt-get", "install", "firefox"],
                {"stderr": subprocess.DEVNULL},
            ).check_call()
            # Verify xvfb installation
            check_xvfb = sp.SubprocessService(["which xvfb-run"], OPTS).check_output(
                output=True
            )
        if not "/usr/bin/xvfb-run\n" in check_xvfb:
            raise Exception("xvfb installation failed")
        else:
            print(f"{constants.OKGREEN}OK{constants.ENDC}")
        cache_file_path = pathlib.Path(constants.XVFB_CACHE_FLAG)
        if not cache_file_path.is_file():
            print(
                f"{constants.WARNING}You are running on an headless server, addtional dependencies are required{constants.ENDC}"
            )
            print(
                "The following packages will be installed:\nxserver-xephyr\ntigervnc-standalone-server\nx11-utils\ngnumeric\nlibxi6\nlibgconf-2-4\ndefault-jdk"
            )
            sp.SubprocessService(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "xserver-xephyr",
                    "tigervnc-standalone-server",
                    "x11-utils",
                    "gnumeric",
                    "libxi6",
                    # "libgconf-2-4",
                    "default-jdk",
                ],
                {"stderr": subprocess.DEVNULL},
            ).check_call()
            # Create xvfb cache file
            sp.SubprocessService(
                ["touch", f"{constants.XVFB_CACHE_FLAG}"],
                {"stderr": subprocess.DEVNULL},
            ).check_call()
    return True


def get_root_from_url(url: str) -> str:
    """
    Get root domain from URL

    @param url: URL to extract root domain from
    @return: Root domain of URL
    """
    regex = r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)"
    return re.findall(regex, url)[0]


def file_preview(df, ptf_flag=False):
    with open("output.tmp", "w") as outF:
        df_string = df.to_string(header=True, index=False)
        outF.write(df_string)
    outF.close()
    # bat the file without wrapping
    print(f"{constants.OKGREEN}Written to file successfully!{constants.ENDC}")
    print(f"{constants.OKGREEN}Here is a file preview:{constants.ENDC}")
    # Bad way to run commands, but bat doesn't work with subprocess
    os.system("sleep 1")
    os.system(f"{constants.BAT} --wrap=never --color=never output.tmp")
    if not ptf_flag:
        os.remove("output.tmp")
    else:
        # Change file name with format job_applications_<timestamp>.preview
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        os.rename("output.tmp", f"job_applications_{timestamp}.preview")
        print(f"File renamed to job_applications_{timestamp}.preview")


def load_urls_from_file():
    editor = os.environ.get("EDITOR", "vim")
    initial_message = "# Enter URLs here, one per line. Save and exit to continue.\n"
    with open(".cache/urls.tmp", "w") as outF:
        outF.write(initial_message)
    outF.close()
    urls = []
    os.system(f"{editor} .cache/urls.tmp")
    with open(".cache/urls.tmp", "r") as inF:
        for line in inF.readlines():
            if line[0] == "#":
                continue
            urls.append(line)
    inF.close()
    os.remove(".cache/urls.tmp")
    return ",".join(urls).replace("\n", "")


def get_terminal_width():
    try:
        curses.setupterm()
        size = curses.tigetnum("cols")
        if size == None:
            return None
        return size
    except curses.error:
        return None


def print_tabbed_doc_string(path: str) -> None:
    print()
    # Open target file
    lines = []
    with open(path, "r") as f:
        # Read file line by line
        lines = f.readlines()
    # Print each line with a tab
    print(f"[{constants.INFOBLUE}INFO{constants.ENDC}]:\t{lines[0].strip()}")
    for line in lines[1:]:
        print(f"\t{line.strip()}")
    print()


def get_class_from_tag(tag_w_class: str) -> str:
    """
    Get class from tag with class
    """
    return tag_w_class.split("=")[1].replace('"', "").strip()

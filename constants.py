import pathlib
import os

#### Project Root ####
PROJECT_ROOT = f"{pathlib.Path(__file__).parent.resolve()}"

##### Select Menu Constants #####
AUTO = "Automatically generate entry from url (beta)"
ADD = "Add new job application"
EDIT = "Edit existing job application"
VIEW = "View all job applications"
QUIT = "Quit"
BKP = "Start Backup Daemon"
PRT = "Print to file"

CHOICE_MAP = {
    "Automatically generate entry from url (beta)": "auto",
    "Add new job application": "add",
    "Edit existing job application": "edit",
    "View all job applications": "view",
    "Quit": "quit",
    "Start Backup Daemon": "bkp",
    "Print to file": "print",
}

##### File Constants #####
SOURCE_CSV = "job_applications.csv"
COLUMN_NAMES = ["Company", "Position", "Date Applied", "Status", "Portal Link", "Notes"]

##### Input Constants #####
INPUT_COMPANY_NAME = "Input company name"
INPUT_POSITION = "Input position"
INPUT_DATE_APPLIED = "Input date applied (DD/MM/YYYY)"
INPUT_PORTAL_LINK = "Input portal link"
INPUT_NOTES = "Input notes"
INPUT_JOB_POSTING_URL = "Enter upto 5 comma separated urls."
INPUT_QUIT = "Type Q to quit."
INPUT_MASS_ADD = "Type M for > 5 urls."

##### Status Constants #####
STATUS_INIT = "Applied"
STATUS_ASSESSMENT = "Assessment"
STATUS_INTERVIEW = "Interview"
STATUS_OFFER = "Offer"
STATUS_REJECTED = "Rejected"

##### Date Constants #####
DATE_NOW = "Today"
DATE_CUSTOM = "Custom"

##### Flag Constants #####
BKP_FLAG = "wbkp"

##### Default Choices #####
DEFAULT_COLUMN_CHOOSE = "Default"

##### COLORS #####
OKGREEN = "\033[1;32m"
INFOBLUE = "\033[1;34m"
WARNING = "\033[1;33m"
FAIL = "\033[1;31m"
ENDC = "\033[0m"

GUM_BINARY_LINKS = {}
GUM_BINARY_LINKS[
    "Darwin arm64"
] = "https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Darwin_arm64.tar.gz"
GUM_BINARY_LINKS[
    "Darwin x86_64"
] = "https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Darwin_x86_64.tar.gz"
GUM_BINARY_LINKS[
    "Linux arm64"
] = "https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Linux_arm64.tar.gz"
GUM_BINARY_LINKS[
    "Linux x86_64"
] = "https://github.com/charmbracelet/gum/releases/download/v0.11.0/gum_0.11.0_Linux_x86_64.tar.gz"

##### Command Constants #####
GUM_PATH = f"{PROJECT_ROOT}/bin/gum"
GUM_CHOOSE = ["./bin/gum", "choose"]
GUM_INPUT_W_PLACEHOLDER = ["./bin/gum", "input", "--placeholder"]
GUM_FILTER = ["./bin/gum", "filter", "--fuzzy", "--no-limit", "--sort"]

BAT = "./bin/bat/bin/bat"

YN = ["YES", "NO"]
NY = ["NO", "YES"]

##### Display Constants #####
MAX_COL_WIDTH = 40

#### Platform Constants ####
PLATFORM_MAP = {
    "linkedin": "linkedin",
    "joinhandshake": "handshake",
    "greenhouse": "greenhouse",
}

#### Auth Constants ####
VAULT_PATH = f"{PROJECT_ROOT}/.vault"

#### Redis Constants ####
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_CONTAINER_NAME = "redis-trapp"
REDIS_DATA_DIR = f"{REDIS_CONTAINER_NAME}-data"
REDIS_DOCKER_IMAGE_TAG = "redis:7.2.2-bookworm"
REDIS_USERNAME = "default"
REDIS_TEST_PWD = "test"
REDIS_CHARSET = "utf-8"
REDIS_ERRORS = "strict"
REDIS_LOG_FILE = f"{PROJECT_ROOT}/logs/redis.log"
REDIS_STATUS_TMP = f"{PROJECT_ROOT}/logs/redis_status.tmp"

#### Chrome Driver Constants ####
CHROME_DRIVER_VERSIONS_JSON = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
CHROME_DRIVER_VERSIONS_CACHE = f"{PROJECT_ROOT}/.cache/chrome_driver_versions.json"

CHROME_DRIVER_SYSTEM_ARCH_MAP = {
    "Darwin arm64": "mac-arm64",
    "Darwin x86_64": "mac-x64",
    "Linux x86_64": "linux64",
}

CHROME_DRIVER_EXECUTABLE = f"{PROJECT_ROOT}/bin/chrome-driver/chromedriver-{CHROME_DRIVER_SYSTEM_ARCH_MAP[f'{os.uname().sysname} {os.uname().machine}']}/chromedriver"

CHROME_DRIVER_DEFAULT_OPTS = ["--headless"]
CHROME_DRIVER_NO_HEADLESS_OPTS = ["--no-headless"]
CHROME_DRIVER_INCOGNITO_OPTS = ["--incognito"]
CHROME_DRIVER_SERVER_OPTS = [
    "--headless",
    "--no-sandbox",
    "start-maximized",
    "disable-infobars",
    "--disable-extensions",
]
CHROME_DRIVER_COOKIE_DIR = f"{PROJECT_ROOT}/.cache/chrome_driver_<platform>"

#### Selenium Constants ####
SELENIUM_TIMEOUT = 5

#### Vault Constants ####
VAULT_PATH = f"{PROJECT_ROOT}/.vault"

#### Multiprocessing Constants ####
MAX_WORKERS = 10

#### Logging Constants ####
LOG_FILENAME = f"{PROJECT_ROOT}/logs/trapp.log"
LOG_THREADED_FILENAME = f"{PROJECT_ROOT}/logs/trapp-threaded.log"
LOG_TMP_FILENAME = f"{PROJECT_ROOT}/logs/run_error.log"
LOG_FILEMODE = "a"
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

#### xvfb Constants ####
XVFB_CACHE_FLAG = f"{PROJECT_ROOT}/.cache/xvfb"

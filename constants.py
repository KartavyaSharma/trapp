##### Select Menu Constants #####
ADD = "Add new job application"
EDIT = "Edit existing job application"
VIEW = "View all job applications"
QUIT = "Quit"
BKP = "Start Backup Daemon"
PRT = "Print to file"

CHOICE_MAP = {
    "Add new job application": "add",
    "Edit existing job application": "edit",
    "View all job applications": "view",
    "Quit": "quit",
    "Start Backup Daemon": "bkp",
    "Print to file": "print"
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
OKGREEN = '\033[1;32m'
WARNING = '\033[1;33m'
FAIL = '\033[1;31m'
ENDC = '\033[0m'

##### Command Constants #####
GUM_CHOOSE = ['./gum', 'choose']
GUM_INPUT_W_PLACEHOLDER = ['./gum', 'input', '--placeholder']

##### Display Constants #####
MAX_COL_WIDTH = 40

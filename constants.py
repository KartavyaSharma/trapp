##### Select Menu Constants #####
ADD = "Add new job application"
EDIT = "Edit existing job application"
VIEW = "View all job applications"
QUIT = "Quit"
BKP = "Start Backup Daemon"

CHOICE_MAP = {
    "Add new job application": "add",
    "Edit existing job application": "edit",
    "View all job applications": "view",
    "Quit": "quit",
    "Start Backup Daemon": "bkp"
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

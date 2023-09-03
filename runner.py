import constants
import pandas as pd
import os
import subprocess
import validators

from datetime import date
from datetime import datetime


def filter(subprocess_output):
    return subprocess_output.stdout.decode('utf-8').strip()


def main():
    # Check if source CSV file exists
    if os.path.isfile(constants.SOURCE_CSV) == False:
        print("Source CSV file does not exist. Creating new file named job_applications.csv...")
        try:
            df = pd.DataFrame(columns=constants.COLUMN_NAMES)
            df.to_csv(constants.SOURCE_CSV, index=False)
        except Exception as e:
            print(e)
            return
    else:
        print("Source file job_applications.csv found. What do you want to do?")
    # Ask user what they want to do
    try:
        subprocess.run(
            ["echo", "Choose utility to run:"]
        )
        menuChoice = filter(subprocess.run(
            ["./gum", "choose", constants.VIEW, constants.ADD,
                constants.EDIT, constants.QUIT],
            stdout=subprocess.PIPE,
        ))
    except Exception as e:
        print(e)
        return
    try:
        menu_choice(constants.CHOICE_MAP[menuChoice])()
    except Exception as e:
        print(e)
        return


# Switch case for menu choice
def menu_choice(choice):
    switcher = {
        'view': view,
        'add': add,
        'edit': edit,
        'quit': quit
    }
    func = switcher.get(choice, lambda: "Invalid choice")
    return func


def view():
    try:
        df = pd.read_csv(constants.SOURCE_CSV)
    except Exception as e:
        print(e)
        return
    print(df)

    print("Do you want to sort by a column?")
    sort_choice = filter(subprocess.run(
        ["./gum", "choose", "Yes", "No"],
        stdout=subprocess.PIPE,
        shell=False
    ))
    if sort_choice == "Yes":
        sort_choice = filter(subprocess.run(
            ["./gum", "choose"] + constants.COLUMN_NAMES,
            stdout=subprocess.PIPE,
            shell=False
        ))
    else:
        return
    # Sort dataframe by column
    df = df.sort_values(by=[sort_choice])
    print(df)


def add():
    print("Adding new job application...")
    # Ask user for company name
    company_name = filter(subprocess.run(
        ["./gum", "input", "--placeholder", constants.INPUT_COMPANY_NAME],
        stdout=subprocess.PIPE,
        shell=False
    ))
    # Ask user for position
    position = filter(subprocess.run(
        ["./gum", "input", "--placeholder", constants.INPUT_POSITION],
        stdout=subprocess.PIPE,
        shell=False
    ))
    # Ask user for date applied
    print("Choose date applied:")
    date_choice = filter(subprocess.run(
        ["./gum", "choose", constants.DATE_NOW, constants.DATE_CUSTOM],
        stdout=subprocess.PIPE,
        shell=False
    ))
    formatted_date = ""
    if date_choice == constants.DATE_NOW:
        date_applied = date.today()
        formatted_date = date_applied.strftime("%m/%d/%Y")
    elif date_choice == constants.DATE_CUSTOM:
        date_applied = filter(subprocess.run(
            ["./gum", "input", "--placeholder", constants.INPUT_DATE_APPLIED],
            stdout=subprocess.PIPE,
            shell=False
        ))
        try:
            date_object = datetime.strptime(date_applied, "%m/%d/%Y")
            formatted_date = date_object.strftime("%m/%d/%Y")
        except Exception as e:
            print(e)
            return
    date_applied = formatted_date
    # Ask user for status
    print("Choose current status:")
    current_status = filter(subprocess.run(
        ["./gum", "choose", constants.STATUS_INIT, constants.STATUS_ASSESSMENT,
            constants.STATUS_INTERVIEW, constants.STATUS_OFFER, constants.STATUS_REJECTED],
        stdout=subprocess.PIPE,
        shell=False
    ))
    # Ask user for portal link
    success_flag = True
    while success_flag:
        portal_link = filter(subprocess.run(
            ["./gum", "input", "--placeholder", constants.INPUT_PORTAL_LINK],
            stdout=subprocess.PIPE,
            shell=False
        ))
        # Validate portal link
        if not validators.url(portal_link):
            print("Invalid URL. Please try again.")
            continue
        else:
            success_flag = False
    # Ask user for notes
    notes = filter(subprocess.run(
        ["./gum", "input", "--placeholder", constants.INPUT_NOTES],
        stdout=subprocess.PIPE,
        shell=False
    ))

    # Create dataframe from dictionary
    df_dict = {key: None for key in constants.COLUMN_NAMES}
    df_dict["Company"] = company_name
    df_dict["Position"] = position
    df_dict["Date Applied"] = date_applied
    df_dict["Status"] = current_status
    df_dict["Portal Link"] = portal_link
    df_dict["Notes"] = notes
    df = pd.DataFrame(df_dict, index=[0])
    # Append dataframe to CSV
    df.to_csv(constants.SOURCE_CSV, mode='a', header=False, index=False)
    print("Job entry added!")


def edit():
    print("Editing job application...")


def quit():
    print("Quitting...")

if __name__ == "__main__":
    main()

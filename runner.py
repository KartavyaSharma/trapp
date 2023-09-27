import constants
import pandas as pd
import os
import subprocess
import sys
import validators
import curses

from datetime import date
from datetime import datetime

global bkp_flag
bkp_flag = False


def filter(subprocess_output):
    return subprocess_output.stdout.decode('utf-8').strip()

def get_terminal_width():
    try:
        curses.setupterm()
        size = curses.tigetnum("cols")
        if size == None:
            return None
        return size
    except curses.error:
        return None

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
        if bkp_flag:
            menuChoice = filter(subprocess.run(
                [*constants.GUM_CHOOSE] + [constants.VIEW, constants.ADD,
                    constants.EDIT, constants.BKP, constants.QUIT],
                stdout=subprocess.PIPE,
            ))
        else:
            menuChoice = filter(subprocess.run(
                [*constants.GUM_CHOOSE] + [constants.VIEW, constants.ADD,
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
        'quit': quit,
        'bkp': bkp
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
        [*constants.GUM_CHOOSE] + ["Yes", "No"],
        stdout=subprocess.PIPE,
        shell=False
    ))
    if sort_choice == "Yes":
        sort_choice = filter(subprocess.run(
            [*constants.GUM_CHOOSE] + constants.COLUMN_NAMES,
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
        [*constants.GUM_CHOOSE] + [constants.DATE_NOW, constants.DATE_CUSTOM],
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
        [*constants.GUM_CHOOSE] + [constants.STATUS_INIT, constants.STATUS_ASSESSMENT,
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
    # Make sure job_applications.csv exists
    if os.path.isfile(constants.SOURCE_CSV) == False:
        print("Source CSV file does not exist. Please add a job entry first.")
        return
    success_flag = True
    check_out = constants.DEFAULT_COLUMN_CHOOSE
    while success_flag:
        # Ask user to choose job entry
        column = subprocess.Popen(
                ['column', '-s,', '-t', f'{constants.SOURCE_CSV}'],
                stdout=subprocess.PIPE,
                shell=False
        )
        less = subprocess.Popen(
                ['less', '-#2', '-N', '-S'],
                stdin=column.stdout,
                stdout=subprocess.PIPE
        )
        column.stdout.close()
        gum = subprocess.Popen(
                ['./gum', 'filter'],
                stdin=less.stdout,
                stdout=subprocess.PIPE
        )
        less.stdout.close()
        output = gum.communicate()[0].decode('utf-8')
        echo_output = subprocess.Popen(
                ['echo', f'{output}'],
                stdout=subprocess.PIPE
        )
        awk_check = subprocess.Popen(
                ['awk', '-F', '[[:space:]][[:space:]]+', '{print $1}'],
                stdin=echo_output.stdout,
                stdout=subprocess.PIPE
        )
        echo_output.stdout.close()
        check_out = awk_check.communicate()[0].decode('utf-8').strip()
        if check_out == "Company":
            print(f'{constants.FAIL}You cannot edit a column header!{constants.ENDC}')
            print('Do you want to try again?')
            retry_choice = filter(subprocess.run(
                [*constants.GUM_CHOOSE] + ["Yes", "No"],
                stdout=subprocess.PIPE,
                shell=False
            ))
            if retry_choice == "Yes":
                continue
            else:
                return
        elif check_out == constants.DEFAULT_COLUMN_CHOOSE:
            print(f'{constants.FAIL}No entry was chosen!{constants.ENDC}')
            continue
        else:
            success_flag = False
    # Get rows that match check_out
    df = pd.read_csv(constants.SOURCE_CSV)
    original_df = df.copy()
    # Get original index of matching rows
    # original_index = df.index[df['Company'] == check_out].tolist()[0]
    df = df.loc[df[constants.COLUMN_NAMES[0]] == check_out]
    original_index = df.index.values[0]
    print(f'{constants.OKGREEN}Here are the entries that match your search:{constants.ENDC}')
    # If there are multiple rows, ask user to choose one
    if len(df.index) > 1:
        print(df)
        print(f'{constants.WARNING}Multiple entries found. Please choose one:{constants.ENDC}')
        terminal_width = get_terminal_width()
        if terminal_width == None: 
            terminal_width = 80
        # Ask user to choose one row (show complete row)
        dup_companies = []
        for row in df.values.tolist():
            row_str = "\t".join(row[:4])
            trunc_row_str = row_str[:terminal_width]
            dup_companies.append(trunc_row_str)
        company_row = subprocess.Popen(
            [*constants.GUM_CHOOSE] + dup_companies,
            stdout=subprocess.PIPE,
            shell=False
        )
        position = subprocess.Popen(
            ['awk', '-F', '\t', '{print $2}'],
            stdin=company_row.stdout,
            stdout=subprocess.PIPE
        )
        company_row.stdout.close()
        position_output = position.communicate()[0].decode('utf-8').strip()
        intermidiate_index = df.index[df['Position'] == position_output].tolist()[0]
        df = df.loc[df['Position'] == position_output]
        original_index = original_index + intermidiate_index - 1
    elif len(df.index) == 0:
        print(f'{constants.FAIL}No entries found!{constants.ENDC}')
        return
    # print(original_df.iloc[[original_index]])
    old_df = df.copy()
    # Ask user if they want to update the status or any other column
    print("What do you want to update?")
    update_choice = filter(subprocess.run(
        [*constants.GUM_CHOOSE] + ["Status", "Other"],
        stdout=subprocess.PIPE,
        shell=False
    ))
    if update_choice == "Status":
        print("Choose new status:")
        current_status = filter(subprocess.run(
            [*constants.GUM_CHOOSE] + [constants.STATUS_INIT, constants.STATUS_ASSESSMENT,
                constants.STATUS_INTERVIEW, constants.STATUS_OFFER, constants.STATUS_REJECTED],
            stdout=subprocess.PIPE,
            shell=False
        ))
        df['Status'] = current_status
    elif update_choice == "Other":
        print("Choose column to update:")
        column_choice = filter(subprocess.run(
            [*constants.GUM_CHOOSE] + constants.COLUMN_NAMES,
            stdout=subprocess.PIPE,
            shell=False
        ))
        # Ask user for new value
        new_value = filter(subprocess.run(
            ["./gum", "input", "--placeholder", f"Input new {column_choice}"],
            stdout=subprocess.PIPE,
            shell=False
        ))
        df[column_choice] = new_value
    # Confirm changes
    print("Confirm changes?")
    confirm_choice = filter(subprocess.run(
        [*constants.GUM_CHOOSE] + ["Yes", "No"],
        stdout=subprocess.PIPE,
        shell=False
    ))
    if confirm_choice == "Yes":
        # Update CSV
        original_df.loc[original_index] = df.iloc[0]
        original_df.to_csv(constants.SOURCE_CSV, index=False)
        print("Entry updated!")
    else:
        print("Changes not saved.")
    # Print old and new entries
    print(f'{constants.OKGREEN}Old entry:{constants.ENDC}')
    print(old_df)
    print(f'{constants.OKGREEN}New entry:{constants.ENDC}')
    print(df)

def bkp():
    if not bkp_flag:
        raise Exception("Backup process flag was not passed. Invalid operation.")

def quit():
    print("Quitting...")

if __name__ == "__main__":
    # Check if bkp flag is set
    if len(sys.argv) > 1:
        if sys.argv[1] == constants.BKP_FLAG:
            bkp_flag = True
    main()

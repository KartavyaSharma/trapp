import constants
import os
import pandas as pd
import subprocess
import sys
import validators


from datetime import *
from rich.console import Console
from scripts.models import entry, status
from scripts.services.auto import AutoService
from scripts.utils.process import SubprocessService
from scripts.utils.gum import Gum
from scripts.utils.helpers import (
    get_terminal_width,
    file_preview,
    load_urls_from_file,
    print_tabbed_doc_string,
)

global bkp_flag
bkp_flag = False


def main():
    # Set pandas config to print columns with max width
    pd.set_option("display.max_colwidth", constants.MAX_COL_WIDTH)
    # Check if source CSV file exists
    if os.path.isfile(constants.SOURCE_CSV) == False:
        print(
            "Source CSV file does not exist. Creating new file named job_applications.csv..."
        )
        try:
            df = pd.DataFrame(columns=constants.COLUMN_NAMES)
            df.to_csv(constants.SOURCE_CSV, index=False)
        except Exception as e:
            print(e)
            return
    else:
        print(
            f"{constants.OKGREEN}Source file job_applications.csv found{constants.ENDC}.\nWhat do you want to do?"
        )
    # Ask user what they want to do
    try:
        opts = (
            [
                constants.VIEW,
                constants.ADD,
                constants.EDIT,
                constants.PRT,
                constants.AUTO,
                constants.QUIT,
            ]
            if f"{os.uname().sysname} {os.uname().machine}" != "Linux arm64"
            else [
                constants.VIEW,
                constants.ADD,
                constants.EDIT,
                constants.PRT,
                constants.QUIT,
            ]
        )
        choice = Gum.choose([*opts])
        menu_choice(constants.CHOICE_MAP[choice])()
    except Exception as e:
        print(e)
        raise
        # return


# Switch case for menu choice
def menu_choice(choice):
    switcher = {
        "view": view,
        "add": add,
        "edit": edit,
        "quit": quit,
        "bkp": bkp,
        "auto": auto,
        "print": print_to_file,
    }
    func = switcher.get(choice, lambda: "Invalid choice")
    return func


def view():
    if os.path.isfile(constants.SOURCE_CSV) == False:
        print("Source CSV file does not exist. Please add a job entry first.")
        return
    df = pd.read_csv(constants.SOURCE_CSV)
    # Ask user if they want to sort by column
    print("Do you want to sort output by a column?")
    print(f"Possible columns: {[*constants.COLUMN_NAMES]}")

    sort_choice = Gum.choose([*constants.NY])
    # Have a default sort option
    if sort_choice == "YES":
        print(
            f"{constants.OKGREEN}Choose option to sort by a specific column, if any. Otherwise, select `default`.{constants.ENDC}"
        )
        choices = constants.COLUMN_NAMES
        sort_column = Gum.choose([*choices])
        # Sort dataframe
        df = df.sort_values(by=[sort_column])
    # Print dataframe
    file_preview(df)


def add():
    print("Adding new job application...")
    # Ask user for company name
    company_name = Gum.input(placeholder=constants.INPUT_COMPANY_NAME)
    # Ask user for position
    position = Gum.input(placeholder=constants.INPUT_POSITION)
    # Ask user for date applied
    print("Choose date applied:")
    date_choice = Gum.choose([constants.DATE_NOW, constants.DATE_CUSTOM])
    formatted_date = ""
    if date_choice == constants.DATE_NOW:
        date_applied = date.today()
        formatted_date = date_applied.strftime("%m/%d/%Y")
    elif date_choice == constants.DATE_CUSTOM:
        date_applied = Gum.input(placeholder=constants.INPUT_DATE_APPLIED)
    # Ask user for status
    print("Choose current status:")
    current_status = Gum.choose(
        [
            constants.STATUS_INIT,
            constants.STATUS_ASSESSMENT,
            constants.STATUS_INTERVIEW,
            constants.STATUS_OFFER,
            constants.STATUS_REJECTED,
        ]
    )
    # Ask user for portal link
    success_flag = True
    while success_flag:
        portal_link = Gum.input(
            [constants.INPUT_PORTAL_LINK + f". {constants.INPUT_QUIT}"]
        )
        if portal_link == "Q":
            quit()
        # Validate portal link
        if not validators.url(portal_link):
            print("Invalid URL. Please try again.")
            continue
        else:
            success_flag = False
    # Ask user for notes
    notes = Gum.input(placeholder=constants.INPUT_NOTES)
    # Create entry
    new_entry = entry.Entry(
        company=company_name,
        position=position,
        date_applied=date_applied,
        status=status.Status(current_status),
        link=portal_link,
        notes=notes,
    )
    df = new_entry.create_dataframe()
    # Append dataframe to CSV
    df.to_csv(constants.SOURCE_CSV, mode="a", header=False, index=False)
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
            ["column", "-s,", "-t", f"{constants.SOURCE_CSV}"],
            stdout=subprocess.PIPE,
            shell=False,
        )
        less = subprocess.Popen(
            ["less", "-#2", "-N", "-S"], stdin=column.stdout, stdout=subprocess.PIPE
        )
        column.stdout.close()
        gum = subprocess.Popen(
            [*constants.GUM_FILTER], stdin=less.stdout, stdout=subprocess.PIPE
        )
        less.stdout.close()
        output = gum.communicate()[0].decode("utf-8")
        echo_output = subprocess.Popen(["echo", f"{output}"], stdout=subprocess.PIPE)
        awk_check = subprocess.Popen(
            ["awk", "-F", "[[:space:]][[:space:]]+", "{print $1}"],
            stdin=echo_output.stdout,
            stdout=subprocess.PIPE,
        )
        echo_output.stdout.close()
        check_out = awk_check.communicate()[0].decode("utf-8").strip()
        if check_out == "Company":
            print(f"{constants.FAIL}You cannot edit a column header!{constants.ENDC}")
            print("Do you want to try again?")
            retry_choice = Gum.choose([*constants.YN])
            if retry_choice == "YES":
                continue
            else:
                return
        elif check_out == constants.DEFAULT_COLUMN_CHOOSE:
            print(f"{constants.FAIL}No entry was chosen!{constants.ENDC}")
            continue
        elif check_out is None:
            print(f"{constants.FAIL}No entry was chosen!{constants.ENDC}")
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
    print(
        f"{constants.OKGREEN}Here are the entries that match your search:{constants.ENDC}"
    )
    # If there are multiple rows, ask user to choose one
    if len(df.index) > 1:
        print(df)
        print(
            f"{constants.WARNING}Multiple entries found. Please choose one:{constants.ENDC}"
        )
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
            [*constants.GUM_CHOOSE] + dup_companies, stdout=subprocess.PIPE, shell=False
        )
        position = subprocess.Popen(
            ["awk", "-F", "\t", "{print $2}"],
            stdin=company_row.stdout,
            stdout=subprocess.PIPE,
        )
        company_row.stdout.close()
        position_output = position.communicate()[0].decode("utf-8").strip()
        intermidiate_index = df.index[df["Position"] == position_output].tolist()[0]
        df = df.loc[df["Position"] == position_output]
        original_index = original_index + intermidiate_index - 1
    elif len(df.index) == 0:
        print(f"{constants.FAIL}No entries found!{constants.ENDC}")
        return
    # print(original_df.iloc[[original_index]])
    old_df = df.copy()
    # Ask user if they want to update or delete the entry
    print("What do you want to do?")
    update_choice = Gum.choose(["Update", "Delete"])
    if update_choice == "Update":
        update(df, original_df, original_index, old_df)
    elif update_choice == "Delete":
        delete(df, original_df, original_index)


def delete(df, original_df, original_index):
    print("Confirm deletion?")
    delete_choice = Gum.choose([*constants.YN])
    if delete_choice == "YES":
        # Delete row from dataframe
        original_df = original_df.drop(original_index)
        # Write to CSV
        original_df.to_csv(constants.SOURCE_CSV, index=False)
        print("Entry deleted!")
        print(df)
    else:
        print("Deletion not confirmed. Exiting...")


def update(df, original_df, original_index, old_df):
    # Ask user if they want to update the status or any other column
    print("What do you want to update?")
    update_choice = Gum.choose(["Status", "Other"])
    if update_choice == "Status":
        print("Choose new status:")
        current_status = Gum.choose(
            [
                constants.STATUS_INIT,
                constants.STATUS_ASSESSMENT,
                constants.STATUS_INTERVIEW,
                constants.STATUS_OFFER,
                constants.STATUS_REJECTED,
            ]
        )
        df["Status"] = current_status
    elif update_choice == "Other":
        print("Choose column to update:")
        column_choice = Gum.choose([*constants.COLUMN_NAMES])
        # Ask user for new value
        new_value = Gum.input(placeholder=f"Input new {column_choice}")
        new_value = SubprocessService(
            [*constants.GUM_INPUT_W_PLACEHOLDER] + [f"Input new {column_choice}"]
        ).run()
        df[column_choice] = new_value
    # Confirm changes
    print("Confirm changes?")
    confirm_choice = SubprocessService([*constants.YN]).run()
    if confirm_choice == "Yes":
        # Update CSV
        original_df.loc[original_index] = df.iloc[0]
        original_df.to_csv(constants.SOURCE_CSV, index=False)
        print("Entry updated!")
    else:
        print("Changes not saved.")
    # Print old and new entries
    print(f"{constants.OKGREEN}Old entry:{constants.ENDC}")
    print(old_df)
    print(f"{constants.OKGREEN}New entry:{constants.ENDC}")
    print(df)


def bkp():
    if not bkp_flag:
        print(
            f"{constants.FAIL}Backup process flag was not passed. Invalid operation.{constants.ENDC}"
        )
        sys.exit(1)
    print("Placeholder backup function. TODO")


def print_to_file():
    if os.path.isfile(constants.SOURCE_CSV) == False:
        print("Source CSV file does not exist. Please add a job entry first.")
        return
    df = pd.read_csv(constants.SOURCE_CSV)
    print("Printing to file...")
    file_preview(df, ptf_flag=True)


def auto():
    # breakpoint()
    service = AutoService()  # Initialize AutoService
    # Ask user for job posting URL
    success_flag = True
    while success_flag:
        url = Gum.input(
            placeholder=f"{constants.INPUT_JOB_POSTING_URL} "
            + f"{constants.INPUT_QUIT} "
            + f"{constants.INPUT_MASS_ADD}"
        )
        if url == "Q":
            quit()
        if url == "M":
            url = load_urls_from_file()
        # Check if there are multiple urls
        url.replace(" ", "")
        urls = url.split(",") if url.find(",") != -1 else [url]
        if not all(urls) or not all(validators.url(url) for url in urls):
            print("Invalid URL found. Please try again.")
            continue
        success_flag = False
        print(f"{constants.OKGREEN}Cooking...{constants.ENDC}", end=" ")
        Console().print(":man_cook:")
        dfs = []
        while True:
            try:
                df, failed_urls = service.batch_run(urls)
                dfs.append(df)
                if failed_urls:
                    print_tabbed_doc_string(
                        f"{constants.PROJECT_ROOT}/docs/shell/scrape_fail.txt"
                    )
                    print(f"Do you want to retry {len(failed_urls)} failed URL(s)?")
                    retry_choice = Gum.choose([*constants.YN])
                    if retry_choice == "YES":
                        urls = failed_urls
                        continue
                if df.empty:
                    return
                break
            except Exception as e:
                print(e)
                return
        finish_auto_service(pd.concat(dfs, ignore_index=True))


def quit():
    print(f"{constants.OKGREEN}Exiting...{constants.ENDC}")
    sys.exit(0)


def finish_auto_service(df):
    print("===== Scraper Results =====")
    print(f"{constants.OKGREEN}Scraped {len(df.index)} job(s)!{constants.ENDC}")
    print(df)
    print("===== End of Results =====")
    print("Does this look correct? Confirming will write entry to file.")
    confirm_choice = Gum.choose([*constants.YN])
    if confirm_choice == "YES":
        # Append to CSV
        df.to_csv(constants.SOURCE_CSV, mode="a", header=False, index=False)
        print("Entry written to file!")
    else:
        print(
            "Entry not written to file.\nIf you found errors in the generated entries, they can be manually edited after being committed to the CSV file."
        )


if __name__ == "__main__":
    # Check if bkp flag is set
    if len(sys.argv) > 1:
        if sys.argv[1] == constants.BKP_FLAG:
            bkp_flag = True
    main()

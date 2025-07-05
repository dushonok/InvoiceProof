import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'NotionAutomator')))
from na_settings import (
    VA_ASMAT_ID,
)
from notion_api import (
    get_page_property,
)
import argparse
from datetime import datetime
from ip_notion import *

        
def callback(message):
    """
    Callback function to print status messages.
    """
    print(message)

def add_invoices_to_tasks(invoice_title, start, end):

    #TODO: Eventually, add a param for the person the task is assigned to.

    person = VA_ASMAT_ID  # Assuming VA_ASMAT_ID is the ID of the person to whom tasks are assigned
    start_txt = start.strftime(DATE_PARSING_FORMAT)
    end_txt = end.strftime(DATE_PARSING_FORMAT)
    callback(f"Adding invoices to tasks from {start_txt} to {end_txt} for person with ID {person}...")

    tasks = get_tasks_for_period(start_txt, end_txt, person, status_callback=callback)
    if not tasks:
        callback("No tasks found for the specified date range.")
        return
    for i, task in enumerate(tasks):
        task_id = task.get("id")
        if not task_id:
            callback(f"Task {task} does not have a valid ID.")
            continue
        
        task_title = get_page_property(task, "Subtask")
        task_due_date = get_page_property(task, "Due")
        callback(f"Processing task {i+1}/{len(tasks)}: '{task_title}', due on {task_due_date}.")
        # Create a payment entry for the task
        invoice = add_payment_for_task(task_id, f"{invoice_title}-{i+1}", status_callback=callback, test=True)
    
    callback(f"Added invoices to {len(tasks)} tasks.")

def valid_date(date_str):
    """
    Validates and parses a date string in 'mm-dd-yyyy' format.
    Raises argparse.ArgumentTypeError if invalid.
    """
    try:
        return datetime.strptime(date_str, DATE_PARSING_FORMAT)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Not a valid date: '{date_str}'. Expected format: {DATE_PARSING_FORMAT}."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add invoices to tasks for a given date range.",
        epilog="Example: python script.py 'May Invoice' 01-01-2024 01-31-2024"
    )
    parser.add_argument(
        "invoice_title",
        type=str,
        help="Invoice title (e.g., 'May Invoice')"
    )
    parser.add_argument(
        "start",
        type=valid_date,
        help="Start date in mm-dd-yyyy format (e.g., 01-01-2024)"
    )
    parser.add_argument(
        "end",
        type=valid_date,
        help="End date in mm-dd-yyyy format (e.g., 01-31-2024)"
    )

    args = parser.parse_args()

    # Additional logical check: start <= end
    if args.start > args.end:
        print("Error: Start date must not be after end date.", file=sys.stderr)
        sys.exit(1)

    # Call the actual function with formatted date strings if needed
    add_invoices_to_tasks(
        args.invoice_title,
        args.start,
        args.end
    )
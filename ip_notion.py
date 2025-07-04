import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'NotionAutomator')))

from na_settings import (
    TASKS_SUBTASKS_DB_ID,
    PAYMENTS_PER_TASK_DB_ID,
    INVOICE_NUMBER_PROP,
    NOTION_DATE_TIME_FORMAT,
)
from notion_api import (
    get_db_entries,
    create_page,
    get_page_id,
)
from datetime import datetime

DATE_PARSING_FORMAT = "%m-%d-%Y"


def get_tasks_for_period(start_date, end_date, status_callback=None):
    """
    Fetches tasks from Notion for a given date range.
    
    :param start_date: Start date in 'mm-dd-yyyy' format.
    :param end_date: End date in 'mm-dd-yyyy' format.
    :param status_callback: Optional callback function to report status updates.
    :return: List of tasks within the specified date range.
    """
    if status_callback:
        status_callback(f"Fetching tasks from {start_date} to {end_date}...")

    if not start_date or not end_date:
        raise ValueError("Both start_date and end_date must be provided.")
    
    if start_date > end_date:
        raise ValueError("Start date must not be after end date.")

    start_txt = datetime.strptime(start_date, DATE_PARSING_FORMAT).strftime(NOTION_DATE_TIME_FORMAT)
    end_txt = datetime.strptime(end_date, DATE_PARSING_FORMAT).strftime(NOTION_DATE_TIME_FORMAT)
    print(f"Fetching tasks from {start_date} to {end_date}... Type of start_date: {type(start_date)}, end_date: {type(end_date)}")
    print(f"Converted start_txt: {start_txt}, end_txt: {end_txt}")
    filter = {
        "and": [
            {
                "property": "Due",
                "date": {"on_or_before": start_txt}
            },
            {
                "property": "Due",
                "date": {"on_or_after": end_txt}
            }
        ]
    }
    tasks = get_db_entries(TASKS_SUBTASKS_DB_ID, filter)
    
    if status_callback:
        status_callback(f"Found {len(tasks)} tasks.")

    return tasks

def add_payment_for_task(task_id, invoice_title, status_callback=None, test=False):
    """
    Adds a payment entry for a specific task.
    
    :param task_id: The ID of the task to add the payment for.
    :param amount: The amount to be added as payment.
    :param status_callback: Optional callback function to report status updates.
    :return: The created payment entry.
    """
    if status_callback:
        status_callback(f"Adding invoice '{invoice_title}' for task {task_id}...")

    # Here you would implement the logic to create a payment entry in Notion
    # This is a placeholder implementation
    properties = {
        "Invoice #": {
        "title": [
            {
            "type": "text",
            "text": {
                "content": invoice_title
            }
            }
        ]
        },
        "Task": {
        "relation": [
            {
            "id": task_id
            }
        ]
        }
    }

    if test:
        invoice_id = "test_invoice_id"
        invoice = properties
    else:
        invoice = create_page(PAYMENTS_PER_TASK_DB_ID, properties)
        if not invoice:
            raise Exception("Failed to create invoice record in Notion.")
        invoice_id = get_page_id(invoice)

    if status_callback:
        status_callback(f"Invoice with ID {invoice_id} added successfully.")
    
    return invoice
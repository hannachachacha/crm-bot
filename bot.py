import os
import requests
from zoho import group_overdue_tasks, build_invoice_report

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, json=payload)
    print(response.json())

if __name__ == "__main__":
    # Ранковий звіт по тасках
    report_tasks = group_overdue_tasks()
    send_message(report_tasks)

    # Вечірній звіт по інвойсах
    report_invoices = build_invoice_report()
    send_message(report_invoices)

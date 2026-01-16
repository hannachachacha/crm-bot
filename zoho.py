import requests
from datetime import datetime, date
from collections import defaultdict
from auth import get_access_token

# --- Tasks ---
def get_tasks():
    ZOHO_TOKEN = get_access_token()
    url = "https://www.zohoapis.com/crm/v8/HC_Tasks?fields=Name,Owner,Due_Date,Status"
    headers = {"Authorization": f"Zoho-oauthtoken {ZOHO_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json().get("data", [])

def group_overdue_tasks():
    tasks = get_tasks()
    today = date.today()
    grouped = defaultdict(int)

    for t in tasks:
        status = t.get("Status")
        due_date_str = t.get("Due_Date")
        owner = t.get("Owner", {}).get("name", "Без виконавця")

        if not due_date_str:
            continue

        due_date = datetime.strptime(due_date_str.split("T")[0], "%Y-%m-%d").date()

        if status not in ("Done", "Cancelled") and (due_date <= today):
            grouped[owner] += 1

    message = "🏃 Протерміновані таски:\n"
    for i, (owner, count) in enumerate(grouped.items(), start=1):
        message += f"\n{i}. {owner} - {count} шт.\n"

    return message

# --- Invoices ---
def get_invoices():
    ZOHO_TOKEN = get_access_token()
    url = "https://www.zohoapis.com/crm/v8/HC_Sales_Orders?fields=Name,Owner,Due_Date,Status,Grand_Total"
    headers = {"Authorization": f"Zoho-oauthtoken {ZOHO_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json().get("data", [])

def build_invoice_report():
    invoices = get_invoices()
    today = date.today()
    current_month = today.month
    current_year = today.year

    not_paid = defaultdict(float)
    overdue_count = defaultdict(int)
    overdue_sum = defaultdict(float)
    paid_sum_month = defaultdict(float)

    for inv in invoices:
        status = inv.get("Status")
        owner = inv.get("Owner", {}).get("name", "Без владельца")
        amount = float(inv.get("Grand_Total", 0))
        due_date_str = inv.get("Due_Date")

        due_date = None
        if due_date_str:
            due_date = datetime.strptime(due_date_str.split("T")[0], "%Y-%m-%d").date()

        if status != "Fully Paid":
            not_paid[owner] += amount

        if status != "Fully Paid" and due_date and due_date < today:
            overdue_count[owner] += 1
            overdue_sum[owner] += amount

        if status == "Fully Paid" and due_date and due_date.month == current_month and due_date.year == current_year:
            paid_sum_month[owner] += amount

    msg = "📊 Звіт по інвойсах:\n"

    msg += "\n1. Неоплачені рахунки:\n"
    for owner, total in not_paid.items():
        msg += f"- {owner}: {total:.2f}\n"

    msg += "\n2. Прострочені рахунки:\n"
    for owner in overdue_count:
        msg += f"- {owner}: {overdue_count[owner]} шт. / {overdue_sum[owner]:.2f}\n"

    msg += f"\n3. Рейтинг по оплачених ({today.strftime('%B %Y')}):\n"
    sorted_paid = sorted(paid_sum_month.items(), key=lambda x: x[1], reverse=True)
    for i, (owner, total) in enumerate(sorted_paid, start=1):
        msg += f"{i}. {owner} — {total:.2f}\n"

    return msg

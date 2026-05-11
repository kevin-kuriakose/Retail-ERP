import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Payment Mode"),    "fieldname": "payment_mode",      "fieldtype": "Data",     "width": 130},
        {"label": _("Date"),            "fieldname": "payment_date",      "fieldtype": "Date",     "width": 100},
        {"label": _("Entry No"),        "fieldname": "name",              "fieldtype": "Link", "options": "Retail Payment Entry", "width": 140},
        {"label": _("Customer"),        "fieldname": "customer",          "fieldtype": "Link", "options": "Retail Customer", "width": 130},
        {"label": _("Amount Received"), "fieldname": "amount_received",   "fieldtype": "Currency", "width": 130},
        {"label": _("Gateway Status"),  "fieldname": "payment_status",    "fieldtype": "Data",     "width": 110},
        {"label": _("Razorpay ID"),     "fieldname": "razorpay_payment_id","fieldtype": "Data",    "width": 150},
        {"label": _("Book Status"),     "fieldname": "status",            "fieldtype": "Data",     "width": 100},
    ]


def get_data(filters):
    conditions = []
    values = {}
    if filters.get("payment_mode"):
        conditions.append("payment_mode = %(payment_mode)s")
        values["payment_mode"] = filters["payment_mode"]
    if filters.get("from_date"):
        conditions.append("payment_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("payment_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = frappe.db.sql(f"""
        SELECT name, payment_date, payment_mode, customer,
               amount_received, payment_status, razorpay_payment_id, status
        FROM `tabRetail Payment Entry`
        {where}
        ORDER BY payment_date DESC
    """, values, as_dict=True)
    return [{
        "name": r.name, "payment_date": r.payment_date, "payment_mode": r.payment_mode,
        "customer": r.customer, "amount_received": flt(r.amount_received),
        "payment_status": r.payment_status, "razorpay_payment_id": r.razorpay_payment_id or "",
        "status": r.status,
    } for r in rows]

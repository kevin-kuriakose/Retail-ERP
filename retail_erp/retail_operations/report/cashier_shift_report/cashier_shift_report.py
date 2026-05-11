import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Store"),       "fieldname": "store",            "fieldtype": "Link", "options": "Store Profile", "width": 130},
        {"label": _("Cashier"),     "fieldname": "cashier",          "fieldtype": "Data", "width": 130},
        {"label": _("Open Time"),   "fieldname": "shift_open_time",  "fieldtype": "Datetime", "width": 140},
        {"label": _("Close Time"),  "fieldname": "shift_close_time", "fieldtype": "Datetime", "width": 140},
        {"label": _("Opening Cash"),"fieldname": "opening_cash",     "fieldtype": "Currency", "width": 110},
        {"label": _("Closing Cash"),"fieldname": "closing_cash",     "fieldtype": "Currency", "width": 110},
        {"label": _("Collections"), "fieldname": "total_collections","fieldtype": "Currency", "width": 110},
        {"label": _("Variance"),    "fieldname": "cash_variance",    "fieldtype": "Currency", "width": 100},
        {"label": _("Status"),      "fieldname": "status",           "fieldtype": "Data",     "width": 120},
    ]


def get_data(filters):
    conditions = []
    values = {}
    if filters.get("store"):
        conditions.append("store = %(store)s")
        values["store"] = filters["store"]
    if filters.get("from_date"):
        conditions.append("DATE(shift_open_time) >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("DATE(shift_open_time) <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = frappe.db.sql(f"""
        SELECT store, cashier, shift_open_time, shift_close_time,
               opening_cash, closing_cash, total_collections, cash_variance, status
        FROM `tabCashier Shift`
        {where}
        ORDER BY shift_open_time DESC
    """, values, as_dict=True)
    return [{
        "store": r.store, "cashier": r.cashier,
        "shift_open_time": r.shift_open_time, "shift_close_time": r.shift_close_time,
        "opening_cash": flt(r.opening_cash), "closing_cash": flt(r.closing_cash),
        "total_collections": flt(r.total_collections), "cash_variance": flt(r.cash_variance),
        "status": r.status,
    } for r in rows]

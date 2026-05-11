import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Return No"),     "fieldname": "name",              "fieldtype": "Link", "options": "Return Transaction", "width": 130},
        {"label": _("Date"),          "fieldname": "return_date",       "fieldtype": "Date",     "width": 100},
        {"label": _("Store"),         "fieldname": "store",             "fieldtype": "Link", "options": "Store Profile", "width": 120},
        {"label": _("Customer"),      "fieldname": "customer",          "fieldtype": "Link", "options": "Retail Customer", "width": 130},
        {"label": _("Item"),          "fieldname": "item",              "fieldtype": "Link", "options": "Product Item", "width": 130},
        {"label": _("Qty"),           "fieldname": "qty",               "fieldtype": "Float",    "width": 70},
        {"label": _("Refund Amt"),    "fieldname": "amount",            "fieldtype": "Currency", "width": 110},
        {"label": _("Reason"),        "fieldname": "reason",            "fieldtype": "Data",     "width": 150},
        {"label": _("Refund Mode"),   "fieldname": "refund_mode",       "fieldtype": "Data",     "width": 110},
    ]


def get_data(filters):
    conditions = []
    values = {}
    if filters.get("store"):
        conditions.append("rt.store = %(store)s")
        values["store"] = filters["store"]
    if filters.get("from_date"):
        conditions.append("rt.return_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("rt.return_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = frappe.db.sql(f"""
        SELECT rt.name, rt.return_date, rt.store, rt.customer, rt.refund_mode,
               rti.item, rti.qty, rti.amount, rti.reason
        FROM `tabReturn Transaction` rt
        JOIN `tabReturn Transaction Item` rti ON rti.parent = rt.name
        {where}
        ORDER BY rt.return_date DESC
    """, values, as_dict=True)
    return [{
        "name": r.name, "return_date": r.return_date, "store": r.store,
        "customer": r.customer, "item": r.item, "qty": flt(r.qty),
        "amount": flt(r.amount), "reason": r.reason or "", "refund_mode": r.refund_mode,
    } for r in rows]

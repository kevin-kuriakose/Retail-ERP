import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Store"),         "fieldname": "store",         "fieldtype": "Link",     "options": "Store Profile", "width": 140},
        {"label": _("Date"),          "fieldname": "posting_date",  "fieldtype": "Date",     "width": 100},
        {"label": _("Payment Mode"),  "fieldname": "payment_mode",  "fieldtype": "Data",     "width": 130},
        {"label": _("Invoices"),      "fieldname": "invoice_count", "fieldtype": "Int",      "width": 80},
        {"label": _("Net Total"),     "fieldname": "net_total",     "fieldtype": "Currency", "width": 120},
        {"label": _("Total Tax"),     "fieldname": "total_tax",     "fieldtype": "Currency", "width": 110},
        {"label": _("Grand Total"),   "fieldname": "grand_total",   "fieldtype": "Currency", "width": 120},
        {"label": _("Discount"),      "fieldname": "total_discount","fieldtype": "Currency", "width": 110},
    ]


def get_data(filters):
    conditions = ["status = 'Paid'"]
    values = {}
    if filters.get("store"):
        conditions.append("store = %(store)s")
        values["store"] = filters["store"]
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT store, posting_date, payment_mode,
               COUNT(name) as invoice_count,
               SUM(net_total) as net_total,
               SUM(total_tax) as total_tax,
               SUM(grand_total) as grand_total,
               SUM(total_discount) as total_discount
        FROM `tabPOS Invoice`
        {where}
        GROUP BY store, posting_date, payment_mode
        ORDER BY posting_date DESC, store
    """, values, as_dict=True)
    return [{
        "store": r.store, "posting_date": r.posting_date, "payment_mode": r.payment_mode,
        "invoice_count": r.invoice_count, "net_total": flt(r.net_total),
        "total_tax": flt(r.total_tax), "grand_total": flt(r.grand_total),
        "total_discount": flt(r.total_discount),
    } for r in rows]

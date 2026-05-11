import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Store"),          "fieldname": "store",          "fieldtype": "Link", "options": "Store Profile", "width": 130},
        {"label": _("Date"),           "fieldname": "posting_date",   "fieldtype": "Date",     "width": 100},
        {"label": _("Total Invoices"), "fieldname": "invoice_count",  "fieldtype": "Int",      "width": 100},
        {"label": _("Gross Revenue"),  "fieldname": "gross_revenue",  "fieldtype": "Currency", "width": 130},
        {"label": _("Total Discount"), "fieldname": "total_discount", "fieldtype": "Currency", "width": 120},
        {"label": _("Net Revenue"),    "fieldname": "net_revenue",    "fieldtype": "Currency", "width": 120},
        {"label": _("Discount %"),     "fieldname": "discount_pct",   "fieldtype": "Percent",  "width": 100},
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
        SELECT store, posting_date,
               COUNT(name) as invoice_count,
               SUM(net_total + total_discount) as gross_revenue,
               SUM(total_discount) as total_discount,
               SUM(net_total) as net_revenue
        FROM `tabPOS Invoice`
        {where}
        GROUP BY store, posting_date
        ORDER BY posting_date DESC
    """, values, as_dict=True)
    result = []
    for r in rows:
        gross = flt(r.gross_revenue)
        disc = flt(r.total_discount)
        result.append({
            "store": r.store, "posting_date": r.posting_date,
            "invoice_count": r.invoice_count, "gross_revenue": gross,
            "total_discount": disc, "net_revenue": flt(r.net_revenue),
            "discount_pct": (disc / gross * 100) if gross else 0,
        })
    return result

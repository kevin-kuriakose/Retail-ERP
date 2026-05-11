import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Rank"),         "fieldname": "rank",        "fieldtype": "Int",      "width": 60},
        {"label": _("Item"),         "fieldname": "item",        "fieldtype": "Link", "options": "Product Item", "width": 140},
        {"label": _("Item Name"),    "fieldname": "item_name",   "fieldtype": "Data",     "width": 180},
        {"label": _("Units Sold"),   "fieldname": "units_sold",  "fieldtype": "Float",    "width": 100},
        {"label": _("Revenue (Rs)"), "fieldname": "revenue",     "fieldtype": "Currency", "width": 120},
        {"label": _("Invoices"),     "fieldname": "invoice_count","fieldtype": "Int",     "width": 80},
    ]


def get_data(filters):
    conditions = ["pi.status = 'Paid'"]
    values = {}
    if filters.get("from_date"):
        conditions.append("pi.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("pi.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    if filters.get("store"):
        conditions.append("pi.store = %(store)s")
        values["store"] = filters["store"]
    where = "WHERE " + " AND ".join(conditions)
    limit = int(filters.get("top_n") or 20)
    rows = frappe.db.sql(f"""
        SELECT pii.item, pii.item_name,
               SUM(pii.qty) as units_sold,
               SUM(pii.amount) as revenue,
               COUNT(DISTINCT pi.name) as invoice_count
        FROM `tabPOS Invoice Item` pii
        JOIN `tabPOS Invoice` pi ON pi.name = pii.parent
        {where}
        GROUP BY pii.item, pii.item_name
        ORDER BY units_sold DESC
        LIMIT {limit}
    """, values, as_dict=True)
    return [{
        "rank": i + 1, "item": r.item, "item_name": r.item_name,
        "units_sold": flt(r.units_sold), "revenue": flt(r.revenue),
        "invoice_count": r.invoice_count,
    } for i, r in enumerate(rows)]

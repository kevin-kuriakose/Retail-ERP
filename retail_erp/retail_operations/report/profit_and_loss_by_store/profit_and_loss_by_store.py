import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Store"),        "fieldname": "store",       "fieldtype": "Link", "options": "Store Profile", "width": 140},
        {"label": _("Revenue"),      "fieldname": "revenue",     "fieldtype": "Currency", "width": 130},
        {"label": _("COGS"),         "fieldname": "cogs",        "fieldtype": "Currency", "width": 120},
        {"label": _("Gross Profit"), "fieldname": "gross_profit","fieldtype": "Currency", "width": 130},
        {"label": _("Gross Margin %"),"fieldname": "margin_pct", "fieldtype": "Percent",  "width": 120},
        {"label": _("Invoices"),     "fieldname": "invoice_count","fieldtype": "Int",     "width": 80},
    ]


def get_data(filters):
    conditions = ["rsi.status = 'Submitted'"]
    values = {}
    if filters.get("from_date"):
        conditions.append("rsi.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("rsi.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT rsi.store,
               SUM(rsi.grand_total) as revenue,
               SUM(rsii.qty * COALESCE(pi.cost_price, 0)) as cogs,
               COUNT(DISTINCT rsi.name) as invoice_count
        FROM `tabRetail Sales Invoice` rsi
        JOIN `tabRetail Sales Invoice Item` rsii ON rsii.parent = rsi.name
        LEFT JOIN `tabProduct Item` pi ON pi.name = rsii.item
        {where}
        GROUP BY rsi.store
        ORDER BY revenue DESC
    """, values, as_dict=True)
    result = []
    for r in rows:
        rev = flt(r.revenue)
        cogs = flt(r.cogs)
        gp = rev - cogs
        margin = (gp / rev * 100) if rev else 0
        result.append({
            "store": r.store, "revenue": rev, "cogs": cogs,
            "gross_profit": gp, "margin_pct": margin,
            "invoice_count": r.invoice_count,
        })
    return result

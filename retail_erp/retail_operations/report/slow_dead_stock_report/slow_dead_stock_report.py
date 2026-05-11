import frappe
from frappe import _
from frappe.utils import flt, add_days, today


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Item"),          "fieldname": "item",          "fieldtype": "Link", "options": "Product Item", "width": 140},
        {"label": _("Item Name"),     "fieldname": "item_name",     "fieldtype": "Data",     "width": 180},
        {"label": _("Category"),      "fieldname": "category",      "fieldtype": "Data",     "width": 120},
        {"label": _("Current Stock"), "fieldname": "current_stock", "fieldtype": "Float",    "width": 110},
        {"label": _("Last Movement"), "fieldname": "last_movement", "fieldtype": "Date",     "width": 110},
        {"label": _("Days No Movement"),"fieldname": "days_no_movement","fieldtype": "Int",  "width": 130},
        {"label": _("Stock Value"),   "fieldname": "stock_value",   "fieldtype": "Currency", "width": 110},
    ]


def get_data(filters):
    no_movement_days = int(filters.get("no_movement_days") or 30)
    cutoff_date = add_days(today(), -no_movement_days)
    rows = frappe.db.sql("""
        SELECT pi.name as item, pi.item_name, pi.category,
               pi.current_stock, pi.cost_price,
               MAX(il.posting_date) as last_movement
        FROM `tabProduct Item` pi
        LEFT JOIN `tabInventory Ledger` il
            ON il.item = pi.name AND il.transaction_type = 'Out'
        WHERE pi.is_active = 1 AND pi.current_stock > 0
        GROUP BY pi.name, pi.item_name, pi.category, pi.current_stock, pi.cost_price
        HAVING (last_movement IS NULL OR last_movement < %(cutoff)s)
        ORDER BY days_no_movement DESC
    """, {"cutoff": cutoff_date}, as_dict=True)

    from frappe.utils import date_diff
    result = []
    for r in rows:
        days = date_diff(today(), r.last_movement) if r.last_movement else 9999
        result.append({
            "item": r.item, "item_name": r.item_name, "category": r.category,
            "current_stock": flt(r.current_stock),
            "last_movement": r.last_movement,
            "days_no_movement": days,
            "stock_value": flt(r.current_stock) * flt(r.cost_price),
        })
    return sorted(result, key=lambda x: x["days_no_movement"], reverse=True)

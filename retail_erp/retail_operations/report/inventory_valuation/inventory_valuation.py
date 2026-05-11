import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Item"),          "fieldname": "name",          "fieldtype": "Link", "options": "Product Item", "width": 140},
        {"label": _("Item Name"),     "fieldname": "item_name",     "fieldtype": "Data",     "width": 180},
        {"label": _("Category"),      "fieldname": "category",      "fieldtype": "Data",     "width": 120},
        {"label": _("UOM"),           "fieldname": "uom",           "fieldtype": "Data",     "width": 70},
        {"label": _("Current Stock"), "fieldname": "current_stock", "fieldtype": "Float",    "width": 110},
        {"label": _("Cost Price"),    "fieldname": "cost_price",    "fieldtype": "Currency", "width": 110},
        {"label": _("Stock Value"),   "fieldname": "stock_value",   "fieldtype": "Currency", "width": 120},
        {"label": _("Selling Rate"),  "fieldname": "standard_rate", "fieldtype": "Currency", "width": 110},
        {"label": _("MRP Value"),     "fieldname": "mrp_value",     "fieldtype": "Currency", "width": 110},
    ]


def get_data(filters):
    conditions = ["is_active = 1", "current_stock > 0"]
    values = {}
    if filters.get("category"):
        conditions.append("category = %(category)s")
        values["category"] = filters["category"]
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT name, item_name, category, uom,
               current_stock, cost_price, standard_rate
        FROM `tabProduct Item`
        {where}
        ORDER BY item_name
    """, values, as_dict=True)
    return [{
        "name": r.name, "item_name": r.item_name, "category": r.category,
        "uom": r.uom, "current_stock": flt(r.current_stock),
        "cost_price": flt(r.cost_price),
        "stock_value": flt(r.current_stock) * flt(r.cost_price),
        "standard_rate": flt(r.standard_rate),
        "mrp_value": flt(r.current_stock) * flt(r.standard_rate),
    } for r in rows]

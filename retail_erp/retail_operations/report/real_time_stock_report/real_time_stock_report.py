import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Item Code"),      "fieldname": "name",          "fieldtype": "Link", "options": "Product Item", "width": 140},
        {"label": _("Item Name"),      "fieldname": "item_name",     "fieldtype": "Data", "width": 180},
        {"label": _("Category"),       "fieldname": "category",      "fieldtype": "Data", "width": 120},
        {"label": _("UOM"),            "fieldname": "uom",           "fieldtype": "Data", "width": 70},
        {"label": _("Current Stock"),  "fieldname": "current_stock", "fieldtype": "Float","width": 110},
        {"label": _("Reorder Level"),  "fieldname": "reorder_level", "fieldtype": "Float","width": 110},
        {"label": _("Reorder Qty"),    "fieldname": "reorder_qty",   "fieldtype": "Float","width": 100},
        {"label": _("Reorder Flag"),   "fieldname": "reorder_flag",  "fieldtype": "Data", "width": 100},
        {"label": _("Selling Rate"),   "fieldname": "standard_rate", "fieldtype": "Currency", "width": 110},
    ]


def get_data(filters):
    conditions = ["is_active = 1"]
    values = {}
    if filters.get("category"):
        conditions.append("category = %(category)s")
        values["category"] = filters["category"]
    if filters.get("low_stock_only"):
        conditions.append("current_stock <= reorder_level")
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT name, item_name, category, uom, current_stock,
               reorder_level, reorder_qty, standard_rate
        FROM `tabProduct Item`
        {where}
        ORDER BY item_name
    """, values, as_dict=True)
    return [{
        "name": r.name, "item_name": r.item_name, "category": r.category,
        "uom": r.uom, "current_stock": flt(r.current_stock),
        "reorder_level": flt(r.reorder_level), "reorder_qty": flt(r.reorder_qty),
        "reorder_flag": "⚠ Reorder" if flt(r.current_stock) <= flt(r.reorder_level) else "",
        "standard_rate": flt(r.standard_rate),
    } for r in rows]

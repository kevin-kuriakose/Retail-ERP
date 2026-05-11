import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Customer"),       "fieldname": "name",           "fieldtype": "Link", "options": "Retail Customer", "width": 140},
        {"label": _("Customer Name"),  "fieldname": "customer_name",  "fieldtype": "Data",     "width": 160},
        {"label": _("Mobile"),         "fieldname": "mobile",         "fieldtype": "Data",     "width": 110},
        {"label": _("Tier"),           "fieldname": "loyalty_tier",   "fieldtype": "Data",     "width": 90},
        {"label": _("Points Balance"), "fieldname": "loyalty_points", "fieldtype": "Float",    "width": 110},
        {"label": _("Points Expiry"),  "fieldname": "points_expiry_date","fieldtype": "Date",  "width": 110},
        {"label": _("Total Spent"),    "fieldname": "total_spent",    "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    conditions = ["is_active = 1"]
    values = {}
    if filters.get("loyalty_tier"):
        conditions.append("loyalty_tier = %(loyalty_tier)s")
        values["loyalty_tier"] = filters["loyalty_tier"]
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT name, customer_name, mobile, loyalty_tier,
               loyalty_points, points_expiry_date, total_spent
        FROM `tabRetail Customer`
        {where}
        ORDER BY loyalty_points DESC
    """, values, as_dict=True)
    return [{
        "name": r.name, "customer_name": r.customer_name, "mobile": r.mobile,
        "loyalty_tier": r.loyalty_tier, "loyalty_points": flt(r.loyalty_points),
        "points_expiry_date": r.points_expiry_date, "total_spent": flt(r.total_spent),
    } for r in rows]

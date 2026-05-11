import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Supplier"),     "fieldname": "supplier",       "fieldtype": "Link", "options": "Retail Supplier", "width": 140},
        {"label": _("PO No"),        "fieldname": "po_name",        "fieldtype": "Data", "width": 130},
        {"label": _("PO Date"),      "fieldname": "order_date",     "fieldtype": "Date", "width": 100},
        {"label": _("PO Amount"),    "fieldname": "po_amount",      "fieldtype": "Currency", "width": 110},
        {"label": _("Invoice No"),   "fieldname": "invoice_name",   "fieldtype": "Data", "width": 130},
        {"label": _("Invoice Amt"),  "fieldname": "invoice_amount", "fieldtype": "Currency", "width": 110},
        {"label": _("Variance"),     "fieldname": "variance",       "fieldtype": "Currency", "width": 100},
    ]


def get_data(filters):
    conditions = []
    values = {}
    if filters.get("supplier"):
        conditions.append("rpo.supplier = %(supplier)s")
        values["supplier"] = filters["supplier"]
    if filters.get("from_date"):
        conditions.append("rpo.order_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("rpo.order_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    rows = frappe.db.sql(f"""
        SELECT rpo.supplier, rpo.name as po_name, rpo.order_date, rpo.grand_total as po_amount,
               rpi.name as invoice_name, rpi.grand_total as invoice_amount
        FROM `tabRetail Purchase Order` rpo
        LEFT JOIN `tabRetail Purchase Invoice` rpi ON rpi.purchase_order = rpo.name
        {where}
        ORDER BY rpo.order_date DESC
    """, values, as_dict=True)
    return [{
        "supplier": r.supplier, "po_name": r.po_name, "order_date": r.order_date,
        "po_amount": flt(r.po_amount), "invoice_name": r.invoice_name or "",
        "invoice_amount": flt(r.invoice_amount),
        "variance": flt(r.po_amount) - flt(r.invoice_amount),
    } for r in rows]

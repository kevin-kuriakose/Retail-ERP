import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Invoice No"),    "fieldname": "name",        "fieldtype": "Link", "options": "Retail Purchase Invoice", "width": 140},
        {"label": _("Date"),          "fieldname": "posting_date","fieldtype": "Date",     "width": 100},
        {"label": _("Supplier"),      "fieldname": "supplier",    "fieldtype": "Link", "options": "Retail Supplier", "width": 130},
        {"label": _("Supplier Inv"),  "fieldname": "supplier_invoice_no","fieldtype": "Data","width": 120},
        {"label": _("Net Total"),     "fieldname": "net_total",   "fieldtype": "Currency", "width": 110},
        {"label": _("Total Tax"),     "fieldname": "total_tax",   "fieldtype": "Currency", "width": 100},
        {"label": _("Grand Total"),   "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    conditions = ["status = 'Submitted'"]
    values = {}
    if filters.get("from_date"):
        conditions.append("posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    if filters.get("supplier"):
        conditions.append("supplier = %(supplier)s")
        values["supplier"] = filters["supplier"]
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT name, posting_date, supplier, supplier_invoice_no,
               net_total, total_tax, grand_total
        FROM `tabRetail Purchase Invoice`
        {where}
        ORDER BY posting_date DESC
    """, values, as_dict=True)
    return [{
        "name": r.name, "posting_date": r.posting_date, "supplier": r.supplier,
        "supplier_invoice_no": r.supplier_invoice_no or "",
        "net_total": flt(r.net_total), "total_tax": flt(r.total_tax),
        "grand_total": flt(r.grand_total),
    } for r in rows]

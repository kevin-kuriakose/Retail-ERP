import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
    filters = filters or {}
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Invoice No"),   "fieldname": "name",        "fieldtype": "Link", "options": "Retail Sales Invoice", "width": 140},
        {"label": _("Date"),         "fieldname": "posting_date","fieldtype": "Date",     "width": 100},
        {"label": _("Store"),        "fieldname": "store",       "fieldtype": "Link", "options": "Store Profile", "width": 130},
        {"label": _("Customer"),     "fieldname": "customer",    "fieldtype": "Link", "options": "Retail Customer", "width": 130},
        {"label": _("HSN Code"),     "fieldname": "hsn_code",    "fieldtype": "Data",     "width": 90},
        {"label": _("Taxable Amt"),  "fieldname": "taxable_amount","fieldtype": "Currency","width": 120},
        {"label": _("GST Rate %"),   "fieldname": "gst_rate",    "fieldtype": "Float",    "width": 90},
        {"label": _("Tax Amount"),   "fieldname": "tax_amount",  "fieldtype": "Currency", "width": 110},
        {"label": _("Invoice Total"),"fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
        {"label": _("IRN"),          "fieldname": "irn",         "fieldtype": "Data",     "width": 130},
    ]


def get_data(filters):
    conditions = ["rsi.status = 'Submitted'"]
    values = {}
    if filters.get("store"):
        conditions.append("rsi.store = %(store)s")
        values["store"] = filters["store"]
    if filters.get("from_date"):
        conditions.append("rsi.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("rsi.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    where = "WHERE " + " AND ".join(conditions)
    rows = frappe.db.sql(f"""
        SELECT rsi.name, rsi.posting_date, rsi.store, rsi.customer,
               rsii.hsn_code, rsii.taxable_amount,
               tt.gst_rate, rsii.tax_amount,
               rsi.grand_total, rsi.irn
        FROM `tabRetail Sales Invoice` rsi
        JOIN `tabRetail Sales Invoice Item` rsii ON rsii.parent = rsi.name
        LEFT JOIN `tabTax Template` tt ON tt.name = rsii.tax_template
        {where}
        ORDER BY rsi.posting_date DESC, rsi.name
    """, values, as_dict=True)
    return [{
        "name": r.name, "posting_date": r.posting_date, "store": r.store,
        "customer": r.customer, "hsn_code": r.hsn_code or "",
        "taxable_amount": flt(r.taxable_amount), "gst_rate": flt(r.gst_rate),
        "tax_amount": flt(r.tax_amount), "grand_total": flt(r.grand_total),
        "irn": r.irn or "",
    } for r in rows]

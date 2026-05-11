import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, today


class InventoryLedger(Document):

    def validate(self):
        self.amount = flt(self.qty) * flt(self.rate)
        if not self.posting_date:
            self.posting_date = today()

    def before_insert(self):
        current = flt(frappe.db.get_value("Product Item", self.item, "current_stock"))
        self.qty_before = current
        if self.transaction_type == "In":
            self.qty_after = current + flt(self.qty)
        elif self.transaction_type == "Out":
            self.qty_after = current - flt(self.qty)
        else:
            self.qty_after = flt(self.qty)

    def after_insert(self):
        frappe.db.set_value("Product Item", self.item, "current_stock", self.qty_after)


def create_ledger_entry(item, qty, transaction_type, voucher_type, voucher_no,
                        store=None, warehouse=None, rate=0, remarks=""):
    """Helper called by invoices to create ledger entries."""
    frappe.get_doc({
        "doctype": "Inventory Ledger",
        "posting_date": today(),
        "item": item,
        "store": store,
        "warehouse": warehouse,
        "voucher_type": voucher_type,
        "voucher_no": voucher_no,
        "transaction_type": transaction_type,
        "qty": flt(qty),
        "rate": flt(rate),
        "remarks": remarks,
    }).insert(ignore_permissions=True)


def deduct_stock_on_sale(doc, method=None):
    for row in doc.items or []:
        create_ledger_entry(
            item=row.item, qty=flt(row.qty), transaction_type="Out",
            voucher_type="Retail Sales Invoice", voucher_no=doc.name,
            store=doc.store, rate=flt(row.rate)
        )


def restore_stock_on_cancel(doc, method=None):
    for row in doc.items or []:
        create_ledger_entry(
            item=row.item, qty=flt(row.qty), transaction_type="In",
            voucher_type="Retail Sales Invoice", voucher_no=doc.name,
            store=doc.store, rate=flt(row.rate), remarks="Cancelled — stock restored"
        )


def increase_stock_on_purchase(doc, method=None):
    for row in doc.items or []:
        create_ledger_entry(
            item=row.item, qty=flt(row.qty), transaction_type="In",
            voucher_type="Retail Purchase Invoice", voucher_no=doc.name,
            store=doc.store, rate=flt(row.rate)
        )


def restore_stock_on_return(doc, method=None):
    for row in doc.items or []:
        create_ledger_entry(
            item=row.item, qty=flt(row.qty), transaction_type="In",
            voucher_type="Return Transaction", voucher_no=doc.name,
            store=doc.store, rate=flt(row.rate), remarks="Return — stock restored"
        )

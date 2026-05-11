import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class ReturnTransaction(Document):

    def validate(self):
        self.return_date = self.return_date or today()
        total = 0.0
        for row in self.items or []:
            row.amount = flt(row.qty) * flt(row.rate)
            total += flt(row.amount)
        self.total_refund_amount = total

    def on_submit(self):
        self.status = "Approved"
        from retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger import restore_stock_on_return
        restore_stock_on_return(self)

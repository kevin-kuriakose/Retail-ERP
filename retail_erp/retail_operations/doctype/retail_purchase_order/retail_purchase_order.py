import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class RetailPurchaseOrder(Document):

    def validate(self):
        self.order_date = self.order_date or today()
        if self.expected_delivery_date:
            if getdate(self.expected_delivery_date) < getdate(self.order_date):
                frappe.throw(_("Expected delivery date cannot be before order date."))
        self.grand_total = sum(flt(r.qty) * flt(r.rate) for r in self.items or [])
        for row in self.items or []:
            row.amount = flt(row.qty) * flt(row.rate)

    def on_submit(self):
        self.status = "Ordered"

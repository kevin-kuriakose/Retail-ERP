import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class RetailDeliveryNote(Document):

    def validate(self):
        self.delivery_date = self.delivery_date or today()
        self.grand_total = sum(flt(r.qty) * flt(r.rate) for r in self.items or [])
        for row in self.items or []:
            row.amount = flt(row.qty) * flt(row.rate)

    def on_submit(self):
        self.status = "Dispatched"

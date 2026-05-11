import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class RetailPaymentEntry(Document):

    def validate(self):
        self.payment_date = self.payment_date or today()
        if flt(self.amount_received) <= 0:
            frappe.throw(_("Amount received must be greater than zero."))

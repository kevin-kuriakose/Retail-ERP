import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class PromotionalScheme(Document):

    def validate(self):
        if getdate(self.valid_to) < getdate(self.valid_from):
            frappe.throw(_("Valid To cannot be before Valid From."))
        if flt(self.discount_percent) > 100:
            frappe.throw(_("Discount % cannot exceed 100."))

import frappe
from frappe import _
from frappe.model.document import Document


class RetailSupplier(Document):

    def validate(self):
        if self.gstin and len(self.gstin) != 15:
            frappe.throw(_("GSTIN must be 15 characters."))
        if self.email:
            from frappe.utils import validate_email_address
            validate_email_address(self.email, throw=True)

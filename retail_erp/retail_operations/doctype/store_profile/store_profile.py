import frappe
from frappe import _
from frappe.model.document import Document


class StoreProfile(Document):

    def validate(self):
        if self.gstin and len(self.gstin) != 15:
            frappe.throw(_("GSTIN must be exactly 15 characters."))

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ProductItem(Document):

    def validate(self):
        if flt(self.standard_rate) <= 0:
            frappe.throw(_("Selling rate must be greater than zero."))
        if flt(self.reorder_level) < 0:
            frappe.throw(_("Reorder level cannot be negative."))

    def after_insert(self):
        self.generate_barcode()

    def generate_barcode(self):
        if not self.barcode:
            barcode_val = self.item_code or self.name
            frappe.db.set_value("Product Item", self.name, "barcode", barcode_val)

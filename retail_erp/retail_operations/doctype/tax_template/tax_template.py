import frappe
from frappe.model.document import Document
from frappe.utils import flt


class TaxTemplate(Document):

    def validate(self):
        self.gst_rate = sum(flt(row.rate) for row in self.tax_rows or [])

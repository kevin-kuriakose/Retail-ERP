import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class RetailPurchaseInvoice(Document):

    def validate(self):
        self.posting_date = self.posting_date or today()
        net = 0.0
        tax = 0.0
        for row in self.items or []:
            subtotal = flt(row.qty) * flt(row.rate)
            t = 0.0
            if row.tax_template:
                gst_rate = flt(frappe.db.get_value("Tax Template", row.tax_template, "gst_rate"))
                t = subtotal * gst_rate / 100
            row.tax_amount = t
            row.amount = subtotal + t
            net += subtotal
            tax += t
        self.net_total = net
        self.total_tax = tax
        self.grand_total = net + tax

    def on_submit(self):
        self.status = "Submitted"
        from retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger import increase_stock_on_purchase
        increase_stock_on_purchase(self)

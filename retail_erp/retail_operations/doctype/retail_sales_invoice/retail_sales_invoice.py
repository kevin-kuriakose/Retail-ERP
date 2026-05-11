import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class RetailSalesInvoice(Document):

    def validate(self):
        self.posting_date = self.posting_date or today()
        self.calculate_totals()

    def calculate_totals(self):
        net = 0.0
        tax = 0.0
        for row in self.items or []:
            base = flt(row.qty) * flt(row.rate)
            taxable = base * (1 - flt(row.discount_percent) / 100)
            row.taxable_amount = taxable
            t = 0.0
            if row.tax_template:
                gst_rate = flt(frappe.db.get_value("Tax Template", row.tax_template, "gst_rate"))
                t = taxable * gst_rate / 100
            row.tax_amount = t
            row.amount = taxable + t
            net += taxable
            tax += t
        self.net_total = net
        self.total_tax = tax
        self.grand_total = net + tax

    def on_submit(self):
        self.status = "Submitted"
        from retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger import deduct_stock_on_sale
        deduct_stock_on_sale(self)

    def on_cancel(self):
        self.status = "Cancelled"
        from retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger import restore_stock_on_cancel
        restore_stock_on_cancel(self)

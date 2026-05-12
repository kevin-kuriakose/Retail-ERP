import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class POSInvoice(Document):

    def validate(self):
        self.posting_date = self.posting_date or today()
        self.calculate_totals()

    def calculate_totals(self):
        net = 0.0
        disc = 0.0
        tax = 0.0
        for row in self.items or []:
            base = flt(row.qty) * flt(row.rate)
            d = base * flt(row.discount_percent) / 100
            row.discount_amount = d
            subtotal = base - d
            t = 0.0
            if row.tax_template:
                gst_rate = flt(frappe.db.get_value(
                    "Tax Template", row.tax_template, "gst_rate"))
                t = subtotal * gst_rate / 100
            row.tax_amount = t
            row.amount = subtotal + t
            net += subtotal
            disc += d
            tax += t
        self.net_total = net
        self.total_discount = disc
        self.total_tax = tax
        loyalty_deduction = flt(self.loyalty_points_redeemed) * 0.25
        self.grand_total = net + tax - loyalty_deduction

    def on_submit(self):
        self.status = "Paid"
        self._deduct_stock()
        self._award_loyalty_points()

    def _deduct_stock(self):
        from retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger import create_ledger_entry
        for row in self.items or []:
            current = flt(frappe.db.get_value("Product Item", row.item, "current_stock"))
            if current < flt(row.qty):
                frappe.throw(
                    _(f"Insufficient stock for {row.item_name}. "
                      f"Available: {current}, Required: {row.qty}")
                )
            create_ledger_entry(
                item=row.item,
                qty=flt(row.qty),
                transaction_type="Out",
                voucher_type="POS Invoice",
                voucher_no=self.name,
                store=self.store,
                rate=flt(row.rate)
            )

    def _award_loyalty_points(self):
        if self.customer:
            try:
                cust = frappe.get_doc("Retail Customer", self.customer)
                pts = cust.add_loyalty_points(flt(self.grand_total))
                self.loyalty_points_earned = pts
                frappe.db.set_value(
                    "POS Invoice", self.name, "loyalty_points_earned", pts)
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(), "POS Loyalty Points Error")

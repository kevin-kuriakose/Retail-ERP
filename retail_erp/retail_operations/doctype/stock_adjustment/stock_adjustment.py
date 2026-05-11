import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class StockAdjustment(Document):

    def validate(self):
        self.adjustment_date = self.adjustment_date or today()
        for row in self.items or []:
            current = flt(frappe.db.get_value("Product Item", row.item, "current_stock"))
            row.current_qty = current
            row.difference_qty = flt(row.adjusted_qty) - current

    def on_submit(self):
        self.status = "Submitted"
        from retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger import create_ledger_entry
        for row in self.items or []:
            diff = flt(row.difference_qty)
            if diff == 0:
                continue
            txn_type = "In" if diff > 0 else "Out"
            create_ledger_entry(
                item=row.item, qty=abs(diff), transaction_type="Adjustment",
                voucher_type="Stock Adjustment", voucher_no=self.name,
                store=self.store, warehouse=self.warehouse,
                remarks=f"{self.adjustment_type} — {row.reason or ''}"
            )
            frappe.db.set_value("Product Item", row.item, "current_stock", flt(row.adjusted_qty))

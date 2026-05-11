import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CashierShift(Document):

    def validate(self):
        self.total_collections = (
            flt(self.cash_collections) + flt(self.card_collections) +
            flt(self.upi_collections) + flt(self.other_collections)
        )
        if self.status == "Closed" and self.closing_cash is not None:
            expected_cash = flt(self.opening_cash) + flt(self.cash_collections)
            self.cash_variance = flt(self.closing_cash) - expected_cash
            if abs(flt(self.cash_variance)) > 50:
                self.status = "Variance Flagged"
                frappe.msgprint(
                    _("Cash variance of Rs {0} exceeds Rs 50. Shift flagged.").format(
                        abs(flt(self.cash_variance))
                    ), alert=True
                )

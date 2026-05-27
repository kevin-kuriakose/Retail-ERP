import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, nowtime


class CashierShift(Document):

    def validate(self):
        self.shift_date = self.shift_date or today()
        self.cash_variance = flt(self.closing_cash) - flt(self.opening_cash)

    def on_submit(self):
        self.status = "Closed"
        self.closing_time = nowtime()
        self._calculate_summary()
        frappe.db.set_value("Cashier Shift", self.name, {
            "status": "Closed",
            "closing_time": self.closing_time,
            "total_transactions": self.total_transactions,
            "total_sales": self.total_sales,
        })

    def _calculate_summary(self):
        result = frappe.db.sql("""
            SELECT COUNT(*) as cnt, COALESCE(SUM(grand_total), 0) as total
            FROM `tabBA POS Invoice`
            WHERE cashier_shift = %s AND docstatus = 1
        """, self.name, as_dict=True)
        if result:
            self.total_transactions = result[0].cnt or 0
            self.total_sales = flt(result[0].total)

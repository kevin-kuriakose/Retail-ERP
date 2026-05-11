import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, add_months, today


class RetailCustomer(Document):

    def validate(self):
        if self.email:
            from frappe.utils import validate_email_address
            validate_email_address(self.email, throw=True)
        self._update_loyalty_tier()
        if not self.points_expiry_date:
            self.points_expiry_date = add_months(today(), 12)

    def _update_loyalty_tier(self):
        pts = flt(self.loyalty_points)
        if pts >= 20000:
            self.loyalty_tier = "Platinum"
        elif pts >= 5000:
            self.loyalty_tier = "Gold"
        else:
            self.loyalty_tier = "Silver"

    def add_loyalty_points(self, amount):
        tier_rates = {"Silver": 1.0, "Gold": 1.5, "Platinum": 2.0}
        rate = tier_rates.get(self.loyalty_tier, 1.0)
        pts = flt(amount) / 100 * rate
        self.loyalty_points = flt(self.loyalty_points) + pts
        self.total_spent = flt(self.total_spent) + flt(amount)
        self._update_loyalty_tier()
        self.save(ignore_permissions=True)
        return pts

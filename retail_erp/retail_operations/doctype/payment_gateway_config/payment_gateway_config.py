import frappe
from frappe import _
from frappe.model.document import Document


class PaymentGatewayConfig(Document):

    def validate(self):
        if self.gateway_name == "Razorpay":
            if not self.api_key:
                frappe.throw(_("Razorpay Key ID is required."))
            if not self.api_secret:
                frappe.throw(_("Razorpay Key Secret is required."))

    def get_razorpay_client(self):
        try:
            import razorpay
        except ImportError:
            frappe.throw(_("razorpay package not installed. Run: pip install razorpay"))
        return razorpay.Client(auth=(self.api_key, self.get_password("api_secret")))

import frappe
from frappe import _
from frappe.utils import flt, today
import hmac
import hashlib
import json


def send_daily_sales_report():
    """Scheduled at 23:00 daily — emails sales summary to Store Managers."""
    try:
        from retail_erp.retail_operations.report.daily_sales_summary.daily_sales_summary import execute
        columns, data = execute({"from_date": today(), "to_date": today()})
        if not data:
            return
        headers = "".join(
            f"<th style='padding:6px;border:1px solid #ddd'>{c.get('label', c) if isinstance(c, dict) else c}</th>"
            for c in columns
        )
        rows_html = ""
        for row in data:
            vals = row.values() if isinstance(row, dict) else row
            cells = "".join(f"<td style='padding:6px;border:1px solid #ddd'>{v}</td>" for v in vals)
            rows_html += f"<tr>{cells}</tr>"
        body = f"""
        <h3>RetailEdge Daily Sales Summary — {today()}</h3>
        <table style='border-collapse:collapse;font-size:13px'>
        <thead><tr style='background:#f0f0f0'>{headers}</tr></thead>
        <tbody>{rows_html}</tbody>
        </table>
        """
        managers = frappe.get_all(
            "Has Role",
            filters={"role": ["in", ["Store Manager", "System Manager"]]},
            fields=["parent"],
            distinct=True
        )
        for m in managers:
            email = frappe.db.get_value("User", m.parent, "email")
            if email:
                frappe.sendmail(
                    recipients=[email],
                    subject=f"RetailEdge Daily Sales — {today()}",
                    message=body
                )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "RetailEdge Daily Sales Report")


@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
    """POST /api/method/retail_erp.retail_operations.utils.razorpay_webhook"""
    try:
        payload = frappe.request.data
        sig = frappe.request.headers.get("X-Razorpay-Signature", "")
        cfg = frappe.get_doc("Payment Gateway Config", "Razorpay")
        secret = cfg.get_password("webhook_secret") or ""
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            frappe.local.response["http_status_code"] = 401
            return {"status": "unauthorized"}
        event = json.loads(payload)
        event_type = event.get("event")
        if event_type == "payment.captured":
            _handle_captured(event["payload"]["payment"]["entity"])
        elif event_type == "payment.failed":
            _handle_failed(event["payload"]["payment"]["entity"])
        return {"status": "ok"}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Razorpay Webhook")
        frappe.local.response["http_status_code"] = 500
        return {"status": "error"}


def _handle_captured(payment):
    rzp_id = payment.get("id")
    order_id = payment.get("order_id")
    amount_inr = flt(payment.get("amount", 0)) / 100
    if frappe.db.exists("Retail Payment Entry", {"razorpay_payment_id": rzp_id}):
        return
    pe = frappe.db.get_value("Retail Payment Entry", {"razorpay_order_id": order_id}, "name")
    if pe:
        frappe.db.set_value("Retail Payment Entry", pe, {
            "payment_status": "Captured",
            "razorpay_payment_id": rzp_id,
            "amount_received": amount_inr,
        })
        frappe.db.commit()


def _handle_failed(payment):
    order_id = payment.get("order_id")
    pe = frappe.db.get_value("Retail Payment Entry", {"razorpay_order_id": order_id}, "name")
    if pe:
        frappe.db.set_value("Retail Payment Entry", pe, {"payment_status": "Failed"})
        frappe.db.commit()

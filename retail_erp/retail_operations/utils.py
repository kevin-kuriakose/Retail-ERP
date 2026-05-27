import frappe
from frappe import _
from frappe.utils import flt, today


@frappe.whitelist()
def get_wl_data_by_barcode(barcode):
    """Decode weigh label barcode WL-{name} for ERPNext POS."""
    if not barcode:
        return {}
    barcode = barcode.upper().strip()
    row = frappe.db.get_value("Item Barcode",
        {"barcode": barcode}, ["parent", "uom"], as_dict=True)
    if not row:
        return {}
    parts = (row.uom or "").split("|")
    if len(parts) < 3:
        return {}

    erp_item    = row.parent
    net_weight  = flt(parts[0])
    rate_per_kg = flt(parts[1])
    wl_name     = parts[2]
    total_amount = round(net_weight * rate_per_kg, 2)

    warehouse = frappe.db.get_value(
        "Store Profile", {}, "warehouse") or "Stores - B"
    actual_qty = flt(frappe.db.get_value("Bin",
        {"item_code": erp_item, "warehouse": warehouse},
        "actual_qty") or 0)
    item_doc = frappe.get_cached_doc("Item", erp_item)

    return {
        "item_code":  erp_item,
        "item_name":  f"{item_doc.item_name} ({net_weight} kg)",
        "qty":        net_weight,
        "rate":       rate_per_kg,
        "uom":        "Kg",
        "actual_qty": actual_qty,
        "wl_name":    wl_name,
        "barcode":    barcode,
    }


@frappe.whitelist()
def void_weigh_label(wl_name):
    frappe.db.set_value("Weigh Label", wl_name, "status", "Voided")
    frappe.db.delete("Item Barcode", {"barcode": f"WL-{wl_name}"})
    frappe.db.commit()
    return {"status": "voided"}


@frappe.whitelist()
def get_loyalty_points(customer):
    if not customer:
        return {"points": 0, "tier": "Standard"}
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(loyalty_points),0) as pts
        FROM `tabLoyalty Point Entry`
        WHERE customer = %s AND expiry_date >= CURDATE()
    """, customer, as_dict=True)
    total = flt(result[0].pts if result else 0)
    return {"points": total, "tier": _get_loyalty_tier(total)}


def _get_loyalty_tier(points):
    if points >= 10000: return "Platinum"
    elif points >= 5000: return "Gold"
    elif points >= 1000: return "Silver"
    return "Standard"


def award_loyalty_points(customer, invoice_name, amount, loyalty_program=None):
    if not customer or not amount:
        return 0
    try:
        points = int(flt(amount) / 100)
        if points <= 0:
            return 0
        program = loyalty_program or frappe.db.get_value(
            "BA Customer", customer, "loyalty_program")
        if not program:
            return 0
        frappe.get_doc({
            "doctype": "Loyalty Point Entry",
            "loyalty_program": program,
            "loyalty_program_tier": _get_loyalty_tier(points),
            "customer": customer,
            "invoice_type": "POS Invoice",
            "invoice": invoice_name,
            "loyalty_points": points,
            "purchase_amount": flt(amount),
            "expiry_date": frappe.utils.add_months(today(), 12),
            "company": frappe.defaults.get_user_default("Company"),
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        return points
    except Exception:
        frappe.log_error(frappe.get_traceback(), "RetailEdge Loyalty Points")
        return 0


@frappe.whitelist()
def create_razorpay_order(invoice_name, amount, currency="INR"):
    try:
        import razorpay
    except ImportError:
        frappe.throw(_("razorpay not installed. Run: pip install razorpay --break-system-packages"))
    key_id = frappe.conf.get("razorpay_key_id")
    key_secret = frappe.conf.get("razorpay_key_secret")
    if not key_id or not key_secret:
        frappe.throw(_("Set razorpay_key_id and razorpay_key_secret in site config"))
    client = razorpay.Client(auth=(key_id, key_secret))
    amount_paise = int(flt(amount) * 100)
    order = client.order.create({
        "amount": amount_paise, "currency": currency,
        "receipt": invoice_name,
        "notes": {"invoice": invoice_name},
    })
    frappe.db.set_value("POS Invoice", invoice_name, {
        "custom_razorpay_order_id": order["id"],
        "custom_payment_status": "Pending",
    })
    frappe.db.commit()
    return {"razorpay_order_id": order["id"],
            "amount": amount_paise, "currency": currency, "key_id": key_id}


@frappe.whitelist()
def verify_razorpay_payment(invoice_name, razorpay_order_id,
                             razorpay_payment_id, razorpay_signature):
    import hmac, hashlib
    key_secret = frappe.conf.get("razorpay_key_secret", "")
    body = f"{razorpay_order_id}|{razorpay_payment_id}"
    expected = hmac.new(
        key_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    if expected != razorpay_signature:
        frappe.throw(_("Payment verification failed"))
    frappe.db.set_value("POS Invoice", invoice_name, {
        "custom_razorpay_payment_id": razorpay_payment_id,
        "custom_razorpay_signature": razorpay_signature,
        "custom_payment_status": "Captured",
    })
    frappe.db.commit()
    return {"verified": True}


def on_pos_invoice_submit(doc, method):
    if doc.customer and doc.grand_total:
        award_loyalty_points(
            customer=doc.customer,
            invoice_name=doc.name,
            amount=doc.grand_total,
            loyalty_program=frappe.db.get_value(
                "BA Customer", doc.customer, "loyalty_program"),
        )


def on_pos_invoice_cancel(doc, method):
    try:
        frappe.db.delete("Loyalty Point Entry", {"invoice": doc.name})
        frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "RetailEdge Loyalty Reversal")

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
    """Add custom fields to ERPNext doctypes."""
    create_custom_fields({
        "POS Invoice": [
            {"fieldname":"custom_cashier_shift","fieldtype":"Link",
             "label":"Cashier Shift","options":"Cashier Shift",
             "insert_after":"pos_profile"},
            {"fieldname":"custom_store_profile","fieldtype":"Link",
             "label":"Store","options":"Store Profile",
             "insert_after":"custom_cashier_shift"},
            {"fieldname":"custom_razorpay_order_id","fieldtype":"Data",
             "label":"Razorpay Order ID","insert_after":"custom_store_profile",
             "read_only":1,"print_hide":1},
            {"fieldname":"custom_razorpay_payment_id","fieldtype":"Data",
             "label":"Razorpay Payment ID",
             "insert_after":"custom_razorpay_order_id",
             "read_only":1,"print_hide":1},
            {"fieldname":"custom_razorpay_signature","fieldtype":"Data",
             "label":"Razorpay Signature",
             "insert_after":"custom_razorpay_payment_id",
             "read_only":1,"print_hide":1,"hidden":1},
            {"fieldname":"custom_payment_status","fieldtype":"Select",
             "label":"Payment Status",
             "options":"\nPending\nCaptured\nFailed\nRefunded",
             "insert_after":"custom_razorpay_signature",
             "read_only":1,"print_hide":1},
        ],
        "Customer": [
            {"fieldname":"custom_loyalty_tier","fieldtype":"Select",
             "label":"Loyalty Tier",
             "options":"Standard\nSilver\nGold\nPlatinum",
             "default":"Standard","insert_after":"loyalty_program",
             "read_only":1},
        ],
        "Item": [
            {"fieldname":"custom_reorder_level","fieldtype":"Float",
             "label":"Reorder Level","default":"10",
             "insert_after":"last_purchase_rate"},
            {"fieldname":"custom_store_category","fieldtype":"Data",
             "label":"Store Category","insert_after":"item_group"},
        ],
    }, ignore_validate=True, update=True)
    frappe.db.commit()
    print("✅ RetailEdge custom fields installed")


def before_uninstall():
    fields = [
        ("POS Invoice","custom_cashier_shift"),
        ("POS Invoice","custom_store_profile"),
        ("POS Invoice","custom_razorpay_order_id"),
        ("POS Invoice","custom_razorpay_payment_id"),
        ("POS Invoice","custom_razorpay_signature"),
        ("POS Invoice","custom_payment_status"),
        ("Customer","custom_loyalty_tier"),
        ("Item","custom_reorder_level"),
        ("Item","custom_store_category"),
    ]
    for dt, fn in fields:
        frappe.db.delete("Custom Field", {"dt": dt, "fieldname": fn})
    frappe.db.commit()

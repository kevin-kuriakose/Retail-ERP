import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LowStockAlertConfig(Document):

    def validate(self):
        if flt(self.reorder_level) < 0:
            frappe.throw(_("Reorder level cannot be negative."))
        if flt(self.reorder_qty) <= 0:
            frappe.throw(_("Reorder quantity must be positive."))


def check_all_reorder_levels():
    """Daily scheduler: check stock and auto-create POs if needed."""
    configs = frappe.get_all(
        "Low Stock Alert Config",
        filters={"is_active": 1},
        fields=["name", "item", "store", "warehouse", "reorder_level", "reorder_qty", "auto_create_po"]
    )
    for cfg in configs:
        current = flt(frappe.db.get_value("Product Item", cfg.item, "current_stock"))
        if current <= flt(cfg.reorder_level) and cfg.auto_create_po:
            _auto_create_purchase_order(cfg)


def _auto_create_purchase_order(cfg):
    existing = frappe.db.exists(
        "Retail Purchase Order",
        {"item": cfg.item, "status": "Draft", "docstatus": 0}
    )
    if existing:
        return
    frappe.get_doc({
        "doctype": "Retail Purchase Order",
        "status": "Draft",
        "order_date": frappe.utils.today(),
        "store": cfg.store,
        "expected_delivery_date": frappe.utils.add_days(frappe.utils.today(), 7),
        "items": [{"item": cfg.item, "qty": flt(cfg.reorder_qty), "warehouse": cfg.warehouse}],
        "remarks": f"Auto-created by Low Stock Alert — {cfg.name}",
    }).insert(ignore_permissions=True)
    frappe.db.commit()

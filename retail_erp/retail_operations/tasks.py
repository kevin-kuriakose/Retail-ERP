import frappe
from frappe.utils import today, add_days


def daily_tasks():
    _void_stale_weigh_labels()
    _update_loyalty_tiers()


def _void_stale_weigh_labels():
    cutoff = add_days(today(), -1)
    stale = frappe.get_all("Weigh Label",
        filters={"status": "Weighed", "weigh_date": ["<", cutoff]},
        fields=["name"])
    for wl in stale:
        frappe.db.set_value("Weigh Label", wl.name, "status", "Voided")
        frappe.db.delete("Item Barcode", {"barcode": f"WL-{wl.name}"})
    if stale:
        frappe.db.commit()


def _update_loyalty_tiers():
    from retail_erp.retail_operations.utils import _get_loyalty_tier
    customers = frappe.db.sql("""
        SELECT customer, COALESCE(SUM(loyalty_points),0) as pts
        FROM `tabLoyalty Point Entry`
        WHERE expiry_date >= %s
        GROUP BY customer
    """, today(), as_dict=True)
    for c in customers:
        tier = _get_loyalty_tier(c.pts or 0)
        frappe.db.set_value("BA Customer", c.customer, "custom_loyalty_tier", tier)
    if customers:
        frappe.db.commit()

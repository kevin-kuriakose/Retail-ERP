import frappe
from frappe.utils import flt


@frappe.whitelist()
def search_by_term(search_term, pos_profile, price_list):
    """
    Override of ERPNext POS search_by_term.
    Handles WL- weigh label barcodes, falls through for everything else.
    """
    if search_term and search_term.upper().startswith("WL-"):
        from retail_erp.retail_operations.utils import get_wl_data_by_barcode
        d = get_wl_data_by_barcode(search_term)
        if d and d.get("item_code"):
            net_weight  = flt(d["qty"])
            rate_per_kg = flt(d["rate"])
            total       = round(net_weight * rate_per_kg, 2)
            return {
                "items": [{
                    "item_code":       d["item_code"],
                    "item_name":       d["item_name"],
                    "description":     f"{net_weight} kg @ Rs {rate_per_kg}/kg",
                    "stock_uom":       "Kg",
                    "uom":             "Kg",
                    "actual_qty":      d["actual_qty"],
                    "price_list_rate": rate_per_kg,
                    "rate":            rate_per_kg,
                    "qty":             net_weight,
                    "amount":          total,
                    "barcode":         search_term,
                    "item_image":      None,
                    "serial_no":       None,
                    "batch_no":        None,
                    "has_batch_no":    0,
                    "has_serial_no":   0,
                    "is_stock_item":   1,
                }],
                "serial_no": None,
                "batch_no":  None,
                "barcode":   search_term,
            }
        return {"items": [], "message": "Weigh label not found or already used"}

    from erpnext.selling.page.point_of_sale.point_of_sale import (
        search_by_term as erp_search,
    )
    return erp_search(search_term, pos_profile, price_list)


@frappe.whitelist()
def get_items(start, page_length, price_list, item_group, pos_profile, search_term=""):
    """Pass-through to ERPNext native get_items."""
    from erpnext.selling.page.point_of_sale.point_of_sale import (
        get_items as erp_get_items,
    )
    return erp_get_items(
        start=start,
        page_length=page_length,
        price_list=price_list,
        item_group=item_group,
        pos_profile=pos_profile,
        search_term=search_term,
    )

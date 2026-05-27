# POS search overrides — will be reimplemented in bizaxl_pos
# ERPNext POS imports removed — use bizaxl_pos when available

import frappe


def search_by_term(search_term, pos_profile, page_number=0):
    """Placeholder — will be implemented in bizaxl_pos."""
    return {"items": [], "serial_no": None, "batch_no": None, "barcode": None}


def get_items(start, page_length, price_list, item_group,
              pos_profile, search_term=""):
    """Placeholder — will be implemented in bizaxl_pos."""
    return {"items": [], "count": 0}

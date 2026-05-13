from . import __version__ as app_version

app_name = "retail_erp"
app_title = "RetailEdge ERP"
app_publisher = "bizaxl"
app_description = "Retail extensions for ERPNext — Weigh Labels, Cashier Shifts, Loyalty, Razorpay"
app_icon = "octicon octicon-shopping-cart"
app_color = "#2490ef"
app_email = "admin@bizaxl.com"
app_license = "MIT"

# ── Document Hooks ────────────────────────────────────────────
doc_events = {
    "POS Invoice": {
        "on_submit": "retail_erp.retail_operations.utils.on_pos_invoice_submit",
        "on_cancel": "retail_erp.retail_operations.utils.on_pos_invoice_cancel",
    }
}

# ── POS Search Override (weigh label barcodes) ────────────────
override_whitelisted_methods = {
      "erpnext.selling.page.point_of_sale.point_of_sale.search_by_term":
        "retail_erp.retail_operations.pos_search.search_by_term",
    "erpnext.selling.page.point_of_sale.point_of_sale.get_items":
        "retail_erp.retail_operations.pos_search.get_items",
}

# ── ERPNext POS JS Extension ──────────────────────────────────
app_include_js = "/assets/retail_erp/js/retail_erp_pos.js"

# ── Scheduled Tasks ───────────────────────────────────────────
scheduler_events = {
    "daily": ["retail_erp.retail_operations.tasks.daily_tasks"],
}

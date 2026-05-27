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
# POS overrides moved to bizaxl_pos (coming soon)

# ── ERPNext POS JS Extension ──────────────────────────────────
app_include_js = "/assets/retail_erp/js/retail_erp_pos.js"

# ── Scheduled Tasks ───────────────────────────────────────────
scheduler_events = {
    "daily": ["retail_erp.retail_operations.tasks.daily_tasks"],
}

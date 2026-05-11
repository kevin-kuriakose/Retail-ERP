app_name = "retail_erp"
app_title = "RetailEdge ERP"
app_publisher = "Your Company"
app_description = "Full-stack retail ERP — auto-billing, real-time stock, Razorpay, loyalty, GST, multi-store"
app_email = "dev@yourcompany.com"
app_license = "MIT"
app_version = "0.0.1"

required_apps = ["frappe", "erpnext"]

app_include_css = "/assets/retail_erp/css/retail_erp.css"
app_include_js = "/assets/retail_erp/js/retail_erp.js"

doc_events = {}

scheduler_events = {
    "daily": [
        "retail_erp.retail_operations.doctype.low_stock_alert_config.low_stock_alert_config.check_all_reorder_levels",
    ],
    "cron": {
        "0 23 * * *": [
            "retail_erp.retail_operations.utils.send_daily_sales_report",
        ],
    },
    "weekly": [],
}

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Retail Operations"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Retail Operations"]]},
]

override_doctype_class = {
    # Phase 1 — Masters
    "Store Profile":                "retail_erp.retail_operations.doctype.store_profile.store_profile.StoreProfile",
    "Product Item":                 "retail_erp.retail_operations.doctype.product_item.product_item.ProductItem",
    "Price List Item":              "retail_erp.retail_operations.doctype.price_list_item.price_list_item.PriceListItem",
    "Retail Price List":            "retail_erp.retail_operations.doctype.retail_price_list.retail_price_list.RetailPriceList",
    "Tax Template Detail":          "retail_erp.retail_operations.doctype.tax_template_detail.tax_template_detail.TaxTemplateDetail",
    "Tax Template":                 "retail_erp.retail_operations.doctype.tax_template.tax_template.TaxTemplate",
    "Retail Customer":              "retail_erp.retail_operations.doctype.retail_customer.retail_customer.RetailCustomer",
    "Retail Supplier":              "retail_erp.retail_operations.doctype.retail_supplier.retail_supplier.RetailSupplier",
    "Loyalty Tier":                 "retail_erp.retail_operations.doctype.loyalty_tier.loyalty_tier.LoyaltyTier",
    "Loyalty Program":              "retail_erp.retail_operations.doctype.loyalty_program.loyalty_program.LoyaltyProgram",
    "Payment Gateway Config":       "retail_erp.retail_operations.doctype.payment_gateway_config.payment_gateway_config.PaymentGatewayConfig",
    "Low Stock Alert Config":       "retail_erp.retail_operations.doctype.low_stock_alert_config.low_stock_alert_config.LowStockAlertConfig",
    "Promotional Scheme":           "retail_erp.retail_operations.doctype.promotional_scheme.promotional_scheme.PromotionalScheme",
    # Phase 2 — Transactional
    "Inventory Ledger":             "retail_erp.retail_operations.doctype.inventory_ledger.inventory_ledger.InventoryLedger",
    "Cashier Shift":                "retail_erp.retail_operations.doctype.cashier_shift.cashier_shift.CashierShift",
    "POS Invoice Item":             "retail_erp.retail_operations.doctype.pos_invoice_item.pos_invoice_item.POSInvoiceItem",
    "POS Invoice":                  "retail_erp.retail_operations.doctype.pos_invoice.pos_invoice.POSInvoice",
    "Retail Sales Invoice Item":    "retail_erp.retail_operations.doctype.retail_sales_invoice_item.retail_sales_invoice_item.RetailSalesInvoiceItem",
    "Retail Sales Invoice":         "retail_erp.retail_operations.doctype.retail_sales_invoice.retail_sales_invoice.RetailSalesInvoice",
    "Retail Payment Entry":         "retail_erp.retail_operations.doctype.retail_payment_entry.retail_payment_entry.RetailPaymentEntry",
    "Retail Purchase Order Item":   "retail_erp.retail_operations.doctype.retail_purchase_order_item.retail_purchase_order_item.RetailPurchaseOrderItem",
    "Retail Purchase Order":        "retail_erp.retail_operations.doctype.retail_purchase_order.retail_purchase_order.RetailPurchaseOrder",
    "Retail Purchase Invoice Item": "retail_erp.retail_operations.doctype.retail_purchase_invoice_item.retail_purchase_invoice_item.RetailPurchaseInvoiceItem",
    "Retail Purchase Invoice":      "retail_erp.retail_operations.doctype.retail_purchase_invoice.retail_purchase_invoice.RetailPurchaseInvoice",
    "Stock Adjustment Item":        "retail_erp.retail_operations.doctype.stock_adjustment_item.stock_adjustment_item.StockAdjustmentItem",
    "Stock Adjustment":             "retail_erp.retail_operations.doctype.stock_adjustment.stock_adjustment.StockAdjustment",
    "Return Transaction Item":      "retail_erp.retail_operations.doctype.return_transaction_item.return_transaction_item.ReturnTransactionItem",
    "Return Transaction":           "retail_erp.retail_operations.doctype.return_transaction.return_transaction.ReturnTransaction",
    "Retail Delivery Note Item":    "retail_erp.retail_operations.doctype.retail_delivery_note_item.retail_delivery_note_item.RetailDeliveryNoteItem",
    "Retail Delivery Note":         "retail_erp.retail_operations.doctype.retail_delivery_note.retail_delivery_note.RetailDeliveryNote",
}

after_install = "retail_erp.install.after_install"

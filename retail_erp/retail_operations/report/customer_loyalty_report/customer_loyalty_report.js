frappe.query_reports["Customer Loyalty Report"] = {
    filters: [
        {fieldname: "loyalty_tier", label: __("Loyalty Tier"), fieldtype: "Select",
         options: "\nSilver\nGold\nPlatinum"}
    ]
};

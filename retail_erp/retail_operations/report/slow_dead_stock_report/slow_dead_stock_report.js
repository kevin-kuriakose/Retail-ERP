frappe.query_reports["Slow Dead Stock Report"] = {
    filters: [
        {fieldname: "no_movement_days", label: __("No Movement (Days)"), fieldtype: "Select",
         options: "30\n60\n90", default: "30"}
    ]
};

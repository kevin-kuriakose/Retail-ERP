frappe.query_reports["Promotional Impact Report"] = {
    filters: [
        {fieldname: "store",     label: __("Store"),     fieldtype: "Link", options: "Store Profile"},
        {fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
         default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)},
        {fieldname: "to_date",   label: __("To Date"),   fieldtype: "Date",
         default: frappe.datetime.get_today()}
    ]
};

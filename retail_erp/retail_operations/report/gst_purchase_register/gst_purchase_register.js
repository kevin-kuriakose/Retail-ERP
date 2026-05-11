frappe.query_reports["GST Purchase Register"] = {
    filters: [
        {fieldname: "supplier",  label: __("Supplier"),  fieldtype: "Link", options: "Retail Supplier"},
        {fieldname: "from_date", label: __("From Date"), fieldtype: "Date",
         default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)},
        {fieldname: "to_date",   label: __("To Date"),   fieldtype: "Date",
         default: frappe.datetime.get_today()}
    ]
};

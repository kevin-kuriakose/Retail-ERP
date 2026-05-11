frappe.query_reports["Real-Time Stock Report"] = {
    filters: [
        {fieldname: "category",       label: __("Category"),  fieldtype: "Select",
         options: "\nGroceries\nBeverages\nPersonal Care\nApparel\nElectronics\nStationery\nDairy\nBakery\nHome Care"},
        {fieldname: "low_stock_only", label: __("Low Stock Only"), fieldtype: "Check"}
    ]
};

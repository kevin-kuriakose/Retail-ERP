frappe.query_reports["Inventory Valuation"] = {
    filters: [
        {fieldname: "category", label: __("Category"), fieldtype: "Select",
         options: "\nGroceries\nBeverages\nPersonal Care\nApparel\nElectronics\nStationery\nDairy\nBakery\nHome Care"}
    ]
};

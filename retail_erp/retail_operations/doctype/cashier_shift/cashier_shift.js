frappe.ui.form.on("Cashier Shift", {
    refresh(frm) {
        if (frm.doc.status === "Open" && !frm.is_new()) {
            frm.add_custom_button(__("Close Shift"), () => {
                frappe.prompt([
                    {fieldname:"closing_cash",fieldtype:"Currency",
                     label:__("Closing Cash (Rs)"),reqd:1},
                    {fieldname:"notes",fieldtype:"Small Text",label:__("Notes")},
                ], (v) => {
                    frm.set_value("closing_cash", v.closing_cash);
                    frm.set_value("notes", v.notes);
                    frm.savesubmit();
                }, __("Close Shift"), __("Close"));
            }).addClass("btn-primary");
        }
        if (frm.doc.cash_variance !== undefined && frm.doc.cash_variance !== null) {
            let color = Math.abs(frm.doc.cash_variance) < 100 ? "green" : "red";
            frm.dashboard.add_indicator(
                __("Variance: Rs {0}", [frm.doc.cash_variance]), color);
        }
    },
    closing_cash(frm) {
        frm.set_value("cash_variance",
            flt(frm.doc.closing_cash) - flt(frm.doc.opening_cash));
    }
});

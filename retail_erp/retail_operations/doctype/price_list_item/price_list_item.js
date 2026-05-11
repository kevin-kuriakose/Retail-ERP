frappe.ui.form.on('Price List Item', {
    rate(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (flt(row.rate) < 0) {
            frappe.model.set_value(cdt, cdn, 'rate', 0);
        }
    }
});

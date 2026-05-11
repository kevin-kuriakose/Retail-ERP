frappe.ui.form.on('Retail Purchase Invoice Item', {
    qty(frm, cdt, cdn) {
        let r = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', flt(r.qty) * flt(r.rate));
    },
    rate(frm, cdt, cdn) {
        let r = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'amount', flt(r.qty) * flt(r.rate));
    }
});

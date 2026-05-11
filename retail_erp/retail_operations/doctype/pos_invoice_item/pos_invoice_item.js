frappe.ui.form.on('POS Invoice Item', {
    qty(frm, cdt, cdn) { calculate_row(frm, cdt, cdn); },
    rate(frm, cdt, cdn) { calculate_row(frm, cdt, cdn); },
    discount_percent(frm, cdt, cdn) { calculate_row(frm, cdt, cdn); }
});
function calculate_row(frm, cdt, cdn) {
    let r = locals[cdt][cdn];
    let base = flt(r.qty) * flt(r.rate);
    let disc = base * flt(r.discount_percent) / 100;
    frappe.model.set_value(cdt, cdn, 'discount_amount', disc);
    frappe.model.set_value(cdt, cdn, 'amount', base - disc);
}

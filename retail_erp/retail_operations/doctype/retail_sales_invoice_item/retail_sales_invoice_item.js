frappe.ui.form.on('Retail Sales Invoice Item', {
    qty(frm, cdt, cdn)            { calculate_rsi_row(frm, cdt, cdn); },
    rate(frm, cdt, cdn)           { calculate_rsi_row(frm, cdt, cdn); },
    discount_percent(frm, cdt, cdn){ calculate_rsi_row(frm, cdt, cdn); }
});
function calculate_rsi_row(frm, cdt, cdn) {
    let r = locals[cdt][cdn];
    let base = flt(r.qty) * flt(r.rate);
    let taxable = base * (1 - flt(r.discount_percent) / 100);
    frappe.model.set_value(cdt, cdn, 'taxable_amount', taxable);
}

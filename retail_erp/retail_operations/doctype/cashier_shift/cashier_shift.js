frappe.ui.form.on('Cashier Shift', {
    closing_cash(frm) {
        let expected = flt(frm.doc.opening_cash) + flt(frm.doc.cash_collections);
        let variance = flt(frm.doc.closing_cash) - expected;
        frm.set_value('cash_variance', variance);
        if (Math.abs(variance) > 50) {
            frappe.msgprint({
                title: __('Variance Alert'),
                message: __('Cash variance Rs {0} exceeds Rs 50!', [Math.abs(variance).toFixed(2)]),
                indicator: 'red'
            });
        }
    },
    cash_collections(frm) { update_total(frm); },
    card_collections(frm) { update_total(frm); },
    upi_collections(frm)  { update_total(frm); },
    other_collections(frm){ update_total(frm); }
});
function update_total(frm) {
    frm.set_value('total_collections',
        flt(frm.doc.cash_collections) + flt(frm.doc.card_collections) +
        flt(frm.doc.upi_collections)  + flt(frm.doc.other_collections)
    );
}

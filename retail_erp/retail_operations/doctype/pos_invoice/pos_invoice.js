frappe.ui.form.on('POS Invoice', {
    refresh(frm) {
        if (frm.doc.status === 'Paid' && !frm.is_new()) {
            frm.add_custom_button(__('Create Return'), () => {
                frappe.set_route('Form', 'Return Transaction', {pos_invoice: frm.doc.name});
            });
        }
    }
});
frappe.ui.form.on('POS Invoice Item', {
    qty(frm, cdt, cdn)             { frm.trigger('calculate'); },
    rate(frm, cdt, cdn)            { frm.trigger('calculate'); },
    discount_percent(frm, cdt, cdn){ frm.trigger('calculate'); },
    items_remove(frm)              { frm.trigger('calculate'); }
});

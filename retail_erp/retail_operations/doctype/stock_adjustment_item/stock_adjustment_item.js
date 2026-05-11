frappe.ui.form.on('Stock Adjustment Item', {
    item(frm, cdt, cdn) {
        let r = locals[cdt][cdn];
        if (r.item) {
            frappe.db.get_value('Product Item', r.item, 'current_stock', (v) => {
                frappe.model.set_value(cdt, cdn, 'current_qty', v.current_stock || 0);
            });
        }
    },
    adjusted_qty(frm, cdt, cdn) {
        let r = locals[cdt][cdn];
        frappe.model.set_value(cdt, cdn, 'difference_qty',
            flt(r.adjusted_qty) - flt(r.current_qty));
    }
});

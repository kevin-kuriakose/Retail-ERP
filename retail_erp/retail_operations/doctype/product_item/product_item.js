frappe.ui.form.on('Product Item', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('View Stock Ledger'), () => {
                frappe.set_route('List', 'Inventory Ledger', {item: frm.doc.name});
            });
        }
    },
    standard_rate(frm) {
        let cost = flt(frm.doc.cost_price);
        let rate = flt(frm.doc.standard_rate);
        if (cost && rate) {
            let margin = ((rate - cost) / rate * 100).toFixed(1);
            frm.set_intro(__('Gross margin: {0}%', [margin]), 'blue');
        }
    }
});

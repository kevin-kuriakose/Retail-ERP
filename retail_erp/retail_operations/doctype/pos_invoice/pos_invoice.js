frappe.ui.form.on('POS Invoice', {

    refresh(frm) {
        if (frm.is_new()) {
            setTimeout(() => {
                let f = frm.fields_dict['barcode_scan'];
                if (f) f.input.focus();
            }, 500);
        }

        frm.fields_dict['items'].grid.get_field('item').get_query = () => ({
            filters: { is_active: 1 }
        });

        if (!frm.is_new()) {
            frm.add_custom_button(__('Check Stock'), () => {
                let rows = frm.doc.items || [];
                if (!rows.length) { frappe.msgprint(__('No items.')); return; }
                let msg = '<table style="width:100%;border-collapse:collapse">'
                    + '<tr style="background:#f0f0f0">'
                    + '<th style="padding:6px;border:1px solid #ddd">Item</th>'
                    + '<th style="padding:6px;border:1px solid #ddd">Billed</th>'
                    + '<th style="padding:6px;border:1px solid #ddd">Stock Remaining</th>'
                    + '</tr>';
                let promises = rows.map(row =>
                    frappe.db.get_value('Product Item', row.item, 'current_stock').then(r => {
                        let stock = r.message.current_stock;
                        let remaining = stock - flt(row.qty);
                        let color = remaining < 0 ? 'red' : remaining < 5 ? 'orange' : 'green';
                        msg += '<tr>'
                            + '<td style="padding:6px;border:1px solid #ddd">' + row.item_name + '</td>'
                            + '<td style="padding:6px;border:1px solid #ddd">' + row.qty + '</td>'
                            + '<td style="padding:6px;border:1px solid #ddd;color:' + color + '"><b>' + remaining + '</b></td>'
                            + '</tr>';
                    })
                );
                Promise.all(promises).then(() => {
                    msg += '</table>';
                    frappe.msgprint({ title: __('Stock Impact Preview'), message: msg, indicator: 'blue' });
                });
            });
        }
    },

    barcode_scan(frm) {
        let barcode = frm.doc.barcode_scan;
        if (!barcode) return;
        frm.set_value('barcode_scan', '');

        frappe.db.get_list('Product Item', {
            filters: { barcode: barcode, is_active: 1 },
            fields: ['name', 'item_name', 'standard_rate', 'tax_template', 'current_stock', 'uom', 'barcode'],
            limit: 1
        }).then(results => {
            if (!results || !results.length) {
                frappe.show_alert({ message: __('No item found for barcode: {0}', [barcode]), indicator: 'red' }, 4);
                return;
            }
            let item = results[0];

            if (item.current_stock <= 0) {
                frappe.show_alert({ message: __('OUT OF STOCK: {0}', [item.item_name]), indicator: 'red' }, 5);
                return;
            }

            let existing_row = (frm.doc.items || []).find(r => r.item === item.name);

            if (existing_row) {
                let new_qty = flt(existing_row.qty) + 1;
                if (new_qty > item.current_stock) {
                    frappe.show_alert({ message: __('Only {0} in stock for {1}', [item.current_stock, item.item_name]), indicator: 'orange' }, 5);
                    return;
                }
                frappe.model.set_value(existing_row.doctype, existing_row.name, 'qty', new_qty);
                frappe.show_alert({ message: __('{0} x{1} (stock left: {2})', [item.item_name, new_qty, item.current_stock - new_qty]), indicator: 'green' }, 3);
            } else {
                let row = frm.add_child('items');
                frappe.model.set_value(row.doctype, row.name, 'item', item.name);
                frappe.model.set_value(row.doctype, row.name, 'item_name', item.item_name);
                frappe.model.set_value(row.doctype, row.name, 'qty', 1);
                frappe.model.set_value(row.doctype, row.name, 'rate', item.standard_rate);
                frappe.model.set_value(row.doctype, row.name, 'tax_template', item.tax_template);
                frappe.model.set_value(row.doctype, row.name, 'barcode', item.barcode);
                frappe.show_alert({ message: __('{0} added (stock left: {1})', [item.item_name, item.current_stock - 1]), indicator: 'green' }, 3);
            }

            frm.refresh_field('items');
            frm.trigger('calculate');

            setTimeout(() => {
                let f = frm.fields_dict['barcode_scan'];
                if (f) f.input.focus();
            }, 200);
        });
    },

    calculate(frm) {
        let net = 0, disc = 0, tax = 0;
        let promises = (frm.doc.items || []).map(row => {
            if (!row.item) return Promise.resolve();
            return frappe.db.get_value('Tax Template', row.tax_template, 'gst_rate').then(r => {
                let gst_rate = flt((r && r.message && r.message.gst_rate) || 0);
                let base = flt(row.qty) * flt(row.rate);
                let d = base * flt(row.discount_percent) / 100;
                let subtotal = base - d;
                let t = subtotal * gst_rate / 100;
                frappe.model.set_value(row.doctype, row.name, 'discount_amount', d);
                frappe.model.set_value(row.doctype, row.name, 'tax_amount', t);
                frappe.model.set_value(row.doctype, row.name, 'amount', subtotal + t);
                net += subtotal; disc += d; tax += t;
            });
        });
        Promise.all(promises).then(() => {
            frm.set_value('net_total', net);
            frm.set_value('total_discount', disc);
            frm.set_value('total_tax', tax);
            frm.set_value('grand_total', net + tax - flt(frm.doc.loyalty_points_redeemed) * 0.25);
        });
    }
});

frappe.ui.form.on('POS Invoice Item', {
    qty(frm)             { frm.trigger('calculate'); },
    rate(frm)            { frm.trigger('calculate'); },
    discount_percent(frm){ frm.trigger('calculate'); },
    items_remove(frm)    { frm.trigger('calculate'); }
});

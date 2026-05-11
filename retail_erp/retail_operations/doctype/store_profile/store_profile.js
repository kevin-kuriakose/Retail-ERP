frappe.ui.form.on('Store Profile', {
    refresh(frm) {
        frm.set_intro(
            frm.doc.is_active ? __('Store is active') : __('Store is inactive'),
            frm.doc.is_active ? 'green' : 'red'
        );
    }
});

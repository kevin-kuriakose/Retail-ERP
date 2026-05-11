frappe.ui.form.on('Retail Customer', {
    refresh(frm) {
        const colors = {Silver: 'grey', Gold: 'orange', Platinum: 'blue'};
        if (frm.doc.loyalty_tier) {
            frm.set_intro(
                __('Tier: {0} | Points: {1}', [frm.doc.loyalty_tier, frm.doc.loyalty_points]),
                colors[frm.doc.loyalty_tier] || 'grey'
            );
        }
    }
});

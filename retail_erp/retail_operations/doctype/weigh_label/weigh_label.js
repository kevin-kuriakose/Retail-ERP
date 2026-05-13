frappe.ui.form.on("Weigh Label", {
    refresh(frm) {
        if (frm.doc.status === "Weighed" && !frm.is_new()) {
            frm.add_custom_button(__("Void Label"), () => {
                frappe.confirm(__("Void this weigh label?"), () => {
                    frappe.call({
                        method: "retail_erp.retail_operations.utils.void_weigh_label",
                        args: { wl_name: frm.doc.name },
                        callback() { frm.reload_doc(); }
                    });
                });
            });
        }

        // Only show barcode after the doc is saved
        if (frm.doc.barcode_string && !frm.is_new()) {
            frm.dashboard.add_indicator(
                __("Barcode: {0}", [frm.doc.barcode_string]), "blue");

            let wrapper = frm.get_field("barcode_display").$wrapper;
            wrapper.html(`
                <div style="padding:12px 0; text-align:center; background:#fff; border:1px solid #eee; border-radius:6px; margin-top:8px;">
                    <svg id="wl-barcode-svg"></svg>
                    <div style="margin-top:6px; font-size:13px; color:#555; letter-spacing:2px;">
                        ${frm.doc.barcode_string}
                    </div>
                </div>
            `);

            const renderBarcode = () => {
                JsBarcode("#wl-barcode-svg", frm.doc.barcode_string, {
                    format: "CODE128",
                    width: 2,
                    height: 80,
                    displayValue: false,
                    margin: 10,
                });
            };

            if (typeof JsBarcode !== "undefined") {
                renderBarcode();
            } else {
                frappe.require(
                    "assets/frappe/js/lib/jsbarcode/JsBarcode.all.min.js",
                    renderBarcode
                );
            }
        }
    },

    // ── Auto-fill date and rate when item is selected ──────────
    item(frm) {
        frm.set_value("weigh_date", frappe.datetime.get_today());

        if (frm.doc.item) {
            // Fetch from Item Price (Standard Selling) — more reliable than standard_rate
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Item Price",
                    filters: {
                        item_code: frm.doc.item,
                        price_list: "Standard Selling",
                        selling: 1,
                    },
                    fields: ["price_list_rate"],
                    limit: 1,
                },
                callback(r) {
                    if (r.message && r.message.length > 0) {
                        frm.set_value("unit_rate_per_kg", r.message[0].price_list_rate);
                    } else {
                        // Fallback to standard_rate on the Item master
                        frappe.db.get_value("Item", frm.doc.item, "standard_rate", (d) => {
                            if (d && d.standard_rate) {
                                frm.set_value("unit_rate_per_kg", d.standard_rate);
                            }
                        });
                    }
                }
            });
        }
    },

    gross_weight_kg(frm) { frm.trigger("calculate"); },
    tare_weight_kg(frm)  { frm.trigger("calculate"); },
    unit_rate_per_kg(frm){ frm.trigger("calculate"); },

    calculate(frm) {
        let net = Math.max(0,
            flt(frm.doc.gross_weight_kg) - flt(frm.doc.tare_weight_kg));
        net = Math.round(net * 1000) / 1000;
        frm.set_value("net_weight_kg", net);
        frm.set_value("total_amount",
            Math.round(net * flt(frm.doc.unit_rate_per_kg) * 100) / 100);
    }
});

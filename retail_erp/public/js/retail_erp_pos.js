// RetailEdge POS Extension v3
// Adds Razorpay payment and Loyalty Points display to ERPNext native POS

frappe.provide("retail_erp.pos");

// ── Razorpay in ERPNext POS ────────────────────────────────────
// Adds "Pay via Razorpay" button in POS payment section
$(document).on("frappe.ready", function() {
    if (frappe.get_route_str && frappe.get_route_str() === "point-of-sale") {
        retail_erp.pos.setup_payment_button();
    }
    frappe.router.on("change", function() {
        if (frappe.get_route_str() === "point-of-sale") {
            setTimeout(retail_erp.pos.setup_payment_button, 2000);
        }
    });
});

retail_erp.pos = {
    setup_payment_button() {
        // Watch for payment section to appear
        const observer = new MutationObserver(() => {
            const payment_section = document.querySelector(".payment-section");
            if (payment_section && !document.getElementById("rzp-btn")) {
                retail_erp.pos.add_razorpay_button();
            }
        });
        observer.observe(document.body, {childList: true, subtree: true});
    },

    add_razorpay_button() {
        const btn = document.createElement("button");
        btn.id = "rzp-btn";
        btn.className = "btn btn-primary btn-sm";
        btn.style.cssText = "width:100%;margin-top:8px;background:#2490ef";
        btn.innerHTML = "Pay via Razorpay";
        btn.onclick = () => retail_erp.pos.initiate_razorpay();

        const payment_section = document.querySelector(".payment-section");
        if (payment_section) {
            payment_section.appendChild(btn);
        }
    },

    initiate_razorpay() {
        // Get current POS invoice
        if (!cur_pos || !cur_pos.frm || !cur_pos.frm.doc) return;
        const doc = cur_pos.frm.doc;
        if (!doc.name || doc.docstatus !== 0) {
            frappe.show_alert({
                message: __("Save the invoice before paying"),
                indicator: "orange"
            }, 4);
            return;
        }
        const amount = doc.grand_total;
        if (!amount || amount <= 0) {
            frappe.show_alert({
                message: __("Grand total must be greater than zero"),
                indicator: "orange"
            }, 4);
            return;
        }
        frappe.call({
            method: "retail_erp.retail_operations.utils.create_razorpay_order",
            args: {invoice_name: doc.name, amount: amount, currency: "INR"},
            callback(r) {
                if (r.exc || !r.message) {
                    frappe.msgprint(__("Could not create Razorpay order"));
                    return;
                }
                retail_erp.pos.open_checkout(doc.name, r.message);
            }
        });
    },

    open_checkout(invoice_name, order) {
        if (typeof Razorpay === "undefined") {
            const s = document.createElement("script");
            s.src = "https://checkout.razorpay.com/v1/checkout.js";
            s.onload = () => retail_erp.pos.open_checkout(invoice_name, order);
            document.head.appendChild(s);
            return;
        }
        const rzp = new Razorpay({
            key: order.key_id,
            amount: order.amount,
            currency: order.currency,
            name: "RetailEdge Store",
            description: "Invoice " + invoice_name,
            order_id: order.razorpay_order_id,
            theme: {color: "#2490ef"},
            handler(response) {
                frappe.call({
                    method: "retail_erp.retail_operations.utils.verify_razorpay_payment",
                    args: {
                        invoice_name: invoice_name,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_signature: response.razorpay_signature,
                    },
                    callback(r) {
                        if (r.exc) {
                            frappe.msgprint(__("Payment verification failed"));
                            return;
                        }
                        frappe.show_alert({
                            message: __("Payment captured!"),
                            indicator: "green"
                        }, 5);
                        if (cur_pos) cur_pos.save_and_checkout();
                    }
                });
            },
            modal: {
                ondismiss() {
                    frappe.show_alert({
                        message: __("Payment cancelled"),
                        indicator: "orange"
                    }, 3);
                }
            }
        });
        rzp.open();
    },

    // Show loyalty points for selected customer
    show_loyalty_points(customer) {
        if (!customer) return;
        frappe.call({
            method: "retail_erp.retail_operations.utils.get_loyalty_points",
            args: {customer: customer},
            callback(r) {
                if (r.message) {
                    const d = r.message;
                    const badge = document.getElementById("loyalty-badge");
                    if (badge) {
                        badge.textContent =
                            `${d.tier} | ${d.points} pts`;
                    }
                }
            }
        });
    }
};

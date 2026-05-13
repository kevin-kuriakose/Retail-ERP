frappe.pages['retail-pos'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'RetailEdge POS',
        single_column: true,
    });
    window.retail_pos_app = new RetailPOS(wrapper, page);
};

class RetailPOS {
    constructor(wrapper, page) {
        this.wrapper = wrapper;
        this.page = page;
        this.cart = [];
        this.allItems = [];
        this.selectedPayment = 'Cash';
        this.scanBuffer = '';
        this.scanTimer = null;
        this.posProfile = null;
        this.company = null;
        this.warehouse = null;
        this.priceList = 'Standard Selling';
        this.init();
    }

    async init() {
        await this.loadPOSProfile();
        this.render();
        await this.loadItems();
        await this.loadCustomers();
        this.setupBarcode();
        this.setupClock();
    }

    async loadPOSProfile() {
        try {
            const profiles = await frappe.db.get_list('POS Profile', {
                filters: { disabled: 0 },
                fields: ['name', 'warehouse', 'company', 'currency',
                         'selling_price_list'],
                limit: 1,
            });
            if (profiles.length) {
                const p = profiles[0];
                this.posProfile  = p.name;
                this.warehouse   = p.warehouse;
                this.company     = p.company;
                this.priceList   = p.selling_price_list || 'Standard Selling';
            }
        } catch(e) {
            frappe.show_alert({ message: 'Could not load POS Profile', indicator: 'red' });
        }
    }

    render() {
        $(this.wrapper).find('.page-content').html(`
        <div id="rpos-root" style="
            display:grid;
            grid-template-columns:1fr 380px;
            grid-template-rows:auto 1fr;
            height:calc(100vh - 120px);
            gap:0;
            background:#0f0f11;
            border-radius:12px;
            overflow:hidden;
            border:1px solid rgba(255,255,255,0.08);
            font-family:'Sora',sans-serif;
        ">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@400;500;600&display=swap');
        #rpos-root { --bg:#0f0f11;--surface:#1a1a1f;--surface2:#22222a;--surface3:#2a2a35;
            --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.13);
            --accent:#00e5a0;--accent-dim:rgba(0,229,160,0.12);
            --red:#ff5c5c;--red-dim:rgba(255,92,92,0.12);
            --amber:#ffb347;--amber-dim:rgba(255,179,71,0.12);
            --text:#f0f0f4;--text2:#9090a0;--text3:#505060;
            --mono:'DM Mono',monospace;--sans:'Sora',sans-serif; }
        #rpos-root * { box-sizing:border-box; margin:0; padding:0; }
        #rpos-toolbar {
            grid-column:1/-1;
            background:var(--surface);
            border-bottom:1px solid var(--border);
            padding:10px 16px;
            display:flex; align-items:center; gap:12px;
        }
        #rpos-search {
            flex:1; max-width:460px; position:relative;
        }
        #rpos-search input {
            width:100%; height:36px;
            background:var(--surface2);
            border:1px solid var(--border2);
            border-radius:8px;
            color:var(--text);
            font-family:var(--mono); font-size:13px;
            padding:0 12px 0 36px; outline:none;
            transition:border-color .15s,box-shadow .15s;
        }
        #rpos-search input:focus {
            border-color:var(--accent);
            box-shadow:0 0 0 3px rgba(0,229,160,0.2);
        }
        #rpos-search input::placeholder { color:var(--text3); }
        .rpos-search-icon {
            position:absolute; left:11px; top:50%;
            transform:translateY(-50%);
            color:var(--text3); font-size:16px; pointer-events:none;
        }
        #rpos-profile-badge {
            font-family:var(--mono); font-size:11px;
            color:var(--accent);
            background:rgba(0,229,160,0.1);
            padding:4px 10px; border-radius:20px;
        }
        #rpos-clock {
            margin-left:auto;
            font-family:var(--mono); font-size:12px; color:var(--text3);
        }
        #rpos-items-panel {
            background:var(--bg);
            display:flex; flex-direction:column;
            overflow:hidden;
            border-right:1px solid var(--border);
        }
        #rpos-filters {
            padding:10px 12px;
            border-bottom:1px solid var(--border);
            display:flex; align-items:center; gap:8px; flex-wrap:wrap;
        }
        .rpos-filter {
            height:26px; padding:0 12px; border-radius:20px;
            border:1px solid var(--border2);
            background:transparent; color:var(--text2);
            font-size:11px; cursor:pointer; transition:all .15s;
            font-family:var(--sans);
        }
        .rpos-filter.active, .rpos-filter:hover {
            background:rgba(0,229,160,0.12);
            border-color:var(--accent); color:var(--accent);
        }
        #rpos-item-count {
            margin-left:auto; font-size:11px;
            color:var(--text3); font-family:var(--mono);
        }
        #rpos-grid {
            flex:1; overflow-y:auto; padding:10px;
            display:grid;
            grid-template-columns:repeat(auto-fill,minmax(130px,1fr));
            gap:8px; align-content:start;
        }
        #rpos-grid::-webkit-scrollbar { width:3px; }
        #rpos-grid::-webkit-scrollbar-thumb { background:var(--surface3); border-radius:4px; }
        .rpos-item {
            background:var(--surface);
            border:1px solid var(--border);
            border-radius:12px; padding:12px 10px;
            cursor:pointer; transition:all .15s; position:relative;
        }
        .rpos-item:hover { border-color:var(--border2); background:var(--surface2); transform:translateY(-1px); }
        .rpos-item.oos { opacity:.35; cursor:not-allowed; }
        .rpos-stock {
            position:absolute; top:7px; right:7px;
            font-size:9px; font-family:var(--mono);
            padding:2px 5px; border-radius:10px;
        }
        .rpos-stock.ok  { color:var(--accent); background:var(--accent-dim); }
        .rpos-stock.low { color:var(--amber);  background:var(--amber-dim); }
        .rpos-stock.out { color:var(--red);    background:var(--red-dim); }
        .rpos-initials {
            width:40px; height:40px; border-radius:8px;
            background:var(--surface3);
            display:flex; align-items:center; justify-content:center;
            font-family:var(--mono); font-size:12px; color:var(--text2);
            margin-bottom:8px;
        }
        .rpos-iname { font-size:11px; font-weight:500; color:var(--text); line-height:1.3; margin-bottom:5px; }
        .rpos-iprice { font-family:var(--mono); font-size:12px; color:var(--accent); }
        #rpos-cart-panel {
            background:var(--surface);
            display:flex; flex-direction:column; overflow:hidden;
        }
        #rpos-cart-head {
            padding:12px 14px 8px;
            border-bottom:1px solid var(--border); flex-shrink:0;
        }
        #rpos-customer-row {
            display:flex; align-items:center; gap:8px; margin-bottom:8px;
        }
        #rpos-customer {
            flex:1; height:30px;
            background:var(--surface2);
            border:1px solid var(--border2); border-radius:8px;
            color:var(--text); font-family:var(--sans); font-size:12px;
            padding:0 8px; outline:none;
        }
        #rpos-customer:focus { border-color:var(--accent); }
        #rpos-loyalty {
            display:none; font-family:var(--mono); font-size:10px;
            color:var(--amber); background:var(--amber-dim);
            padding:3px 8px; border-radius:20px;
        }
        #rpos-cart-label {
            font-size:10px; color:var(--text3);
            font-family:var(--mono); letter-spacing:.08em; text-transform:uppercase;
        }
        #rpos-cart-rows {
            flex:1; overflow-y:auto; padding:6px;
        }
        #rpos-cart-rows::-webkit-scrollbar { width:3px; }
        #rpos-cart-rows::-webkit-scrollbar-thumb { background:var(--surface3); border-radius:4px; }
        .rpos-empty {
            height:100%; display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            gap:6px; color:var(--text3); font-size:12px;
        }
        .rpos-crow {
            display:flex; align-items:center; gap:8px;
            padding:8px 6px; border-radius:8px; transition:background .1s;
            animation:rpos-slide .18s ease;
        }
        @keyframes rpos-slide {
            from { opacity:0; transform:translateX(8px); }
            to   { opacity:1; transform:translateX(0); }
        }
        .rpos-crow:hover { background:var(--surface2); }
        .rpos-crow-info { flex:1; min-width:0; }
        .rpos-crow-name {
            font-size:12px; font-weight:500;
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        }
        .rpos-crow-meta { font-size:10px; color:var(--text2); font-family:var(--mono); margin-top:2px; }
        .rpos-weigh-tag {
            color:var(--accent); font-size:9px;
            background:var(--accent-dim); padding:1px 4px;
            border-radius:4px; margin-right:3px;
        }
        .rpos-qty { display:flex; align-items:center; gap:5px; flex-shrink:0; }
        .rpos-qbtn {
            width:22px; height:22px; border-radius:5px;
            border:1px solid var(--border2); background:var(--surface3);
            color:var(--text); font-size:14px; cursor:pointer;
            display:flex; align-items:center; justify-content:center;
            transition:all .1s; line-height:1;
        }
        .rpos-qbtn:hover { border-color:var(--accent); color:var(--accent); }
        .rpos-qval { font-family:var(--mono); font-size:12px; min-width:26px; text-align:center; }
        .rpos-crow-amt {
            font-family:var(--mono); font-size:12px;
            min-width:60px; text-align:right; flex-shrink:0;
        }
        .rpos-crow-del {
            width:18px; height:18px; border:none; background:transparent;
            color:var(--text3); cursor:pointer; font-size:13px;
            display:flex; align-items:center; justify-content:center;
            border-radius:4px; transition:all .1s; flex-shrink:0;
        }
        .rpos-crow-del:hover { color:var(--red); background:var(--red-dim); }
        #rpos-footer {
            border-top:1px solid var(--border);
            padding:12px 14px; flex-shrink:0;
        }
        .rpos-disc-row {
            display:flex; align-items:center; gap:8px; margin-bottom:10px;
        }
        .rpos-disc-label { font-size:11px; color:var(--text2); flex:1; }
        .rpos-disc-input {
            height:26px; width:70px;
            background:var(--surface2); border:1px solid var(--border2);
            border-radius:8px; color:var(--text);
            font-family:var(--mono); font-size:12px;
            padding:0 8px; outline:none; text-align:right;
        }
        .rpos-disc-input:focus { border-color:var(--accent); }
        .rpos-totals { width:100%; margin-bottom:10px; }
        .rpos-totals td { padding:2px 0; font-size:12px; }
        .rpos-totals td:last-child { text-align:right; font-family:var(--mono); }
        .rpos-totals .muted { color:var(--text2); }
        .rpos-totals .grand td {
            font-size:17px; font-weight:600; color:var(--accent);
            padding-top:7px; border-top:1px solid var(--border);
        }
        .rpos-pay-btns {
            display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:8px;
        }
        .rpos-pay {
            height:36px; border-radius:8px;
            border:1px solid var(--border2); background:var(--surface2);
            color:var(--text2); font-size:11px; font-family:var(--sans);
            cursor:pointer; transition:all .15s;
        }
        .rpos-pay:hover { color:var(--text); background:var(--surface3); }
        .rpos-pay.sel { border-color:var(--accent); color:var(--accent); background:var(--accent-dim); }
        #rpos-checkout {
            width:100%; height:44px;
            background:var(--accent); border:none; border-radius:12px;
            color:#0a1a12; font-size:14px; font-weight:600;
            font-family:var(--sans); cursor:pointer; transition:all .15s;
        }
        #rpos-checkout:hover { background:#00ffb3; }
        #rpos-checkout:disabled { opacity:.3; cursor:not-allowed; }
        </style>

        <!-- TOOLBAR -->
        <div id="rpos-toolbar">
            <span style="font-family:var(--mono);font-size:14px;color:var(--accent);font-weight:500;">
                Retail<span style="color:var(--text2)">Edge</span>
            </span>
            <div id="rpos-search">
                <span class="rpos-search-icon">⌕</span>
                <input type="text" id="rpos-search-input"
                    placeholder="Scan barcode or type item name..." autocomplete="off">
            </div>
            <div id="rpos-profile-badge">⬤ ${this.posProfile || 'No POS Profile'}</div>
            <span id="rpos-clock"></span>
        </div>

        <!-- ITEMS PANEL -->
        <div id="rpos-items-panel">
            <div id="rpos-filters">
                <button class="rpos-filter active" onclick="window.retail_pos_app.filterGroup(this,'All')">All</button>
                <div id="rpos-group-btns" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
                <span id="rpos-item-count"></span>
            </div>
            <div id="rpos-grid">
                <div class="rpos-empty"><span>Loading items...</span></div>
            </div>
        </div>

        <!-- CART PANEL -->
        <div id="rpos-cart-panel">
            <div id="rpos-cart-head">
                <div id="rpos-customer-row">
                    <select id="rpos-customer" onchange="window.retail_pos_app.onCustomerChange()">
                        <option>Walk-In Customer</option>
                    </select>
                    <div id="rpos-loyalty"></div>
                </div>
                <div id="rpos-cart-label">item cart</div>
            </div>
            <div id="rpos-cart-rows">
                <div class="rpos-empty">
                    <span style="font-size:20px;opacity:.3">◫</span>
                    <span>Cart is empty</span>
                    <span style="font-size:10px;color:var(--text3)">scan or tap an item</span>
                </div>
            </div>
            <div id="rpos-footer">
                <div class="rpos-disc-row">
                    <span class="rpos-disc-label">Discount (%)</span>
                    <input type="number" class="rpos-disc-input" id="rpos-disc"
                        value="0" min="0" max="100" step="0.5"
                        oninput="window.retail_pos_app.renderTotals()">
                </div>
                <table class="rpos-totals">
                    <tr><td class="muted">Subtotal</td><td id="rpos-subtotal">₹ 0.00</td></tr>
                    <tr><td class="muted">Discount</td><td id="rpos-disc-amt" style="color:var(--red)">—</td></tr>
                    <tr class="grand"><td>Total</td><td id="rpos-grand">₹ 0.00</td></tr>
                </table>
                <div class="rpos-pay-btns">
                    <button class="rpos-pay sel" id="rpos-pay-Cash"
                        onclick="window.retail_pos_app.selectPayment('Cash')">💵 Cash</button>
                    <button class="rpos-pay" id="rpos-pay-Card"
                        onclick="window.retail_pos_app.selectPayment('Card')">💳 Card</button>
                    <button class="rpos-pay" id="rpos-pay-UPI"
                        onclick="window.retail_pos_app.selectPayment('UPI')">📱 UPI</button>
                    <button class="rpos-pay" id="rpos-pay-Credit"
                        onclick="window.retail_pos_app.selectPayment('Credit')">📋 Credit</button>
                </div>
                <button id="rpos-checkout" disabled
                    onclick="window.retail_pos_app.checkout()">
                    Checkout →
                </button>
            </div>
        </div>
        </div>`);
    }

    // ── LOAD ITEMS ─────────────────────────────────────────────
    async loadItems() {
        try {
            const result = await frappe.call({
                method: 'erpnext.selling.page.point_of_sale.point_of_sale.get_items',
                args: {
                    start: 0,
                    page_length: 200,
                    price_list: this.priceList,
                    item_group: 'All Item Groups',
                    pos_profile: this.posProfile,
                    search_term: '',
                },
            });
            this.allItems = result.message?.items || result.message || [];
            this.renderGroups();
            this.renderItems(this.allItems);
        } catch(e) {
            frappe.show_alert({ message: 'Failed to load items', indicator: 'red' });
        }
    }

    async loadCustomers() {
        try {
            const result = await frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Customer',
                    fields: ['name'],
                    limit: 100,
                },
            });
            const sel = document.getElementById('rpos-customer');
            sel.innerHTML = '<option>Walk-In Customer</option>';
            (result.message || []).forEach(c => {
                if (c.name !== 'Walk-In Customer') {
                    const o = document.createElement('option');
                    o.value = o.textContent = c.name;
                    sel.appendChild(o);
                }
            });
        } catch(e) {}
    }

    // ── RENDER ─────────────────────────────────────────────────
    renderGroups() {
        const groups = [...new Set(this.allItems.map(i => i.item_group).filter(Boolean))];
        document.getElementById('rpos-group-btns').innerHTML = groups.map(g =>
            `<button class="rpos-filter"
                onclick="window.retail_pos_app.filterGroup(this,'${g}')">${g}</button>`
        ).join('');
    }

    filterGroup(btn, group) {
        document.querySelectorAll('.rpos-filter').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filtered = group === 'All' ? this.allItems :
            this.allItems.filter(i => i.item_group === group);
        this.renderItems(filtered);
    }

    renderItems(items) {
        const grid = document.getElementById('rpos-grid');
        document.getElementById('rpos-item-count').textContent = `${items.length} items`;
        if (!items.length) {
            grid.innerHTML = `<div class="rpos-empty"><span>No items</span></div>`;
            return;
        }
        grid.innerHTML = items.map(item => {
            const ini = item.item_code.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();
            const qty = item.actual_qty || 0;
            const sc  = qty <= 0 ? 'out' : qty < 10 ? 'low' : 'ok';
            const st  = qty <= 0 ? 'OUT' : qty < 10 ? `${qty} low` : qty;
            return `<div class="rpos-item ${qty<=0?'oos':''}"
                onclick="${qty>0?`window.retail_pos_app.addToCart('${item.item_code.replace(/'/g,"\\'")}')`:''}"
            >
                <span class="rpos-stock ${sc}">${st}</span>
                <div class="rpos-initials">${ini}</div>
                <div class="rpos-iname">${item.item_name || item.item_code}</div>
                <div class="rpos-iprice">₹ ${(item.price_list_rate||0).toFixed(2)}</div>
            </div>`;
        }).join('');
    }

    // ── CART ───────────────────────────────────────────────────
    addToCart(itemCode, overrides = {}) {
        const item = this.allItems.find(i => i.item_code === itemCode);
        const rate     = overrides.rate     ?? (item?.price_list_rate || 0);
        const qty      = overrides.qty      ?? 1;
        const name     = overrides.item_name ?? (item?.item_name || itemCode);
        const isWeigh  = !!overrides.isWeigh;

        if (isWeigh) {
            // Each weigh scan = unique cart line
            this.cart.push({ itemCode, name, qty, rate, isWeigh,
                amount: parseFloat((qty * rate).toFixed(2)) });
        } else {
            const existing = this.cart.find(r => r.itemCode === itemCode && !r.isWeigh);
            if (existing) {
                existing.qty++;
                existing.amount = parseFloat((existing.qty * existing.rate).toFixed(2));
            } else {
                this.cart.push({ itemCode, name, qty, rate, isWeigh: false,
                    amount: parseFloat((qty * rate).toFixed(2)) });
            }
        }
        this.renderCart();
        frappe.show_alert({ message: `✓ ${name}`, indicator: 'green' }, 2);
    }

    changeQty(idx, delta) {
        const row = this.cart[idx];
        if (!row || row.isWeigh) return;
        row.qty = Math.max(1, row.qty + delta);
        row.amount = parseFloat((row.qty * row.rate).toFixed(2));
        this.renderCart();
    }

    removeRow(idx) {
        this.cart.splice(idx, 1);
        this.renderCart();
    }

    renderCart() {
        const el = document.getElementById('rpos-cart-rows');
        if (!this.cart.length) {
            el.innerHTML = `<div class="rpos-empty">
                <span style="font-size:20px;opacity:.3">◫</span>
                <span>Cart is empty</span>
                <span style="font-size:10px;color:var(--text3)">scan or tap an item</span>
            </div>`;
            document.getElementById('rpos-checkout').disabled = true;
            this.renderTotals();
            return;
        }
        el.innerHTML = this.cart.map((row, idx) => `
            <div class="rpos-crow">
                <div class="rpos-crow-info">
                    <div class="rpos-crow-name">${row.name}</div>
                    <div class="rpos-crow-meta">
                        ${row.isWeigh ? '<span class="rpos-weigh-tag">⚖ WEIGH</span>' : ''}
                        ₹ ${row.rate.toFixed(2)} / ${row.isWeigh ? 'kg' : 'unit'}
                    </div>
                </div>
                <div class="rpos-qty">
                    ${row.isWeigh
                        ? `<span class="rpos-qval">${row.qty} kg</span>`
                        : `<button class="rpos-qbtn"
                               onclick="window.retail_pos_app.changeQty(${idx},-1)">−</button>
                           <span class="rpos-qval">${row.qty}</span>
                           <button class="rpos-qbtn"
                               onclick="window.retail_pos_app.changeQty(${idx},1)">+</button>`
                    }
                </div>
                <div class="rpos-crow-amt">₹ ${row.amount.toFixed(2)}</div>
                <button class="rpos-crow-del"
                    onclick="window.retail_pos_app.removeRow(${idx})">✕</button>
            </div>`).join('');
        document.getElementById('rpos-checkout').disabled = false;
        this.renderTotals();
    }

    renderTotals() {
        const sub  = this.cart.reduce((s, r) => s + r.amount, 0);
        const disc = parseFloat(document.getElementById('rpos-disc').value || 0);
        const da   = sub * disc / 100;
        const grand = sub - da;
        document.getElementById('rpos-subtotal').textContent = `₹ ${sub.toFixed(2)}`;
        document.getElementById('rpos-disc-amt').textContent =
            disc > 0 ? `— ₹ ${da.toFixed(2)}` : '—';
        document.getElementById('rpos-grand').textContent = `₹ ${grand.toFixed(2)}`;
    }

    getGrand() {
        const sub  = this.cart.reduce((s, r) => s + r.amount, 0);
        const disc = parseFloat(document.getElementById('rpos-disc').value || 0);
        return sub * (1 - disc / 100);
    }

    // ── PAYMENT ────────────────────────────────────────────────
    selectPayment(method) {
        this.selectedPayment = method;
        ['Cash','Card','UPI','Credit'].forEach(m => {
            document.getElementById(`rpos-pay-${m}`)
                .classList.toggle('sel', m === method);
        });
    }

    async checkout() {
        if (!this.cart.length) return;
        const customer = document.getElementById('rpos-customer').value;
        const grand    = this.getGrand();
        const disc     = parseFloat(document.getElementById('rpos-disc').value || 0);

        const d = new frappe.ui.Dialog({
            title: 'Confirm Payment',
            fields: [
                { fieldtype: 'HTML', options:
                    `<div style="text-align:center;padding:12px 0;">
                        <div style="font-size:11px;color:#888;margin-bottom:4px;">
                            ${this.selectedPayment} · ${customer}</div>
                        <div style="font-size:28px;font-weight:600;color:#00e5a0;">
                            ₹ ${grand.toFixed(2)}</div>
                     </div>` },
                { fieldname: 'cash_tendered', fieldtype: 'Currency',
                  label: 'Cash Tendered',
                  depends_on: `eval:${this.selectedPayment === 'Cash'}` },
            ],
            primary_action_label: 'Submit Invoice',
            primary_action: async (values) => {
                d.hide();
                await this.submitInvoice(customer, grand, disc, values.cash_tendered);
            },
        });
        d.show();
    }

    async submitInvoice(customer, grand, disc, cashTendered) {
        frappe.show_alert({ message: 'Creating invoice...', indicator: 'blue' }, 3);

        const modeMap = {
            'Cash': 'Cash', 'Card': 'Credit Card',
            'UPI': 'Cash', 'Credit': 'Cash',
        };

        try {
            // Step 1: Create the invoice
            const inv = await frappe.call({
                method: 'frappe.client.insert',
                args: {
                    doc: {
                        doctype: 'POS Invoice',
                        customer: customer,
                        pos_profile: this.posProfile,
                        company: this.company,
                        currency: 'INR',
                        selling_price_list: this.priceList,
                        additional_discount_percentage: disc,
                        set_warehouse: this.warehouse,
                        items: this.cart.map(row => ({
                            item_code: row.itemCode,
                            qty:       row.qty,
                            rate:      row.rate,
                            uom:       row.isWeigh ? 'Kg' : undefined,
                            warehouse: this.warehouse,
                        })),
                        payments: [{
                            mode_of_payment: modeMap[this.selectedPayment] || 'Cash',
                            amount: grand,
                        }],
                    },
                },
            });

            // Step 2: Submit it
            frappe.show_alert({ message: 'Submitting...', indicator: 'blue' }, 2);
            await frappe.call({
                method: 'frappe.client.submit',
                args: { doc: inv.message },
            });

            frappe.show_alert({
                message: `✓ Invoice ${inv.message.name} created!`,
                indicator: 'green',
            }, 5);

            this.cart = [];
            document.getElementById('rpos-disc').value = 0;
            this.renderCart();

        } catch(e) {
            frappe.msgprint({
                title: 'Invoice Error',
                message: e.message || 'Could not create invoice',
                indicator: 'red',
            });
        }
    }

    // ── BARCODE ────────────────────────────────────────────────
    setupBarcode() {
        const input = document.getElementById('rpos-search-input');

        input.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const term = input.value.trim();
                if (term) await this.handleSearch(term);
                input.value = '';
            }
        });

        // Rapid input detection for physical barcode scanners
        let lastTime = 0;
        let buf = '';
        input.addEventListener('input', () => {
            const now = Date.now();
            if (now - lastTime < 30) {
                buf = input.value;
                clearTimeout(this.scanTimer);
                this.scanTimer = setTimeout(async () => {
                    const term = buf.trim();
                    if (term.length > 3) {
                        await this.handleSearch(term);
                        input.value = '';
                        buf = '';
                    }
                }, 80);
            }
            lastTime = now;
        });
    }

    async handleSearch(term) {
        term = term.trim().toUpperCase();
        if (!term) return;

        // Weigh label
        if (term.startsWith('WL-')) {
            await this.handleWeighBarcode(term);
            return;
        }

        // Local match first
        const match = this.allItems.find(i =>
            i.item_code === term ||
            i.item_code.toUpperCase() === term ||
            (i.item_name || '').toUpperCase() === term
        );
        if (match) { this.addToCart(match.item_code); return; }

        // Server search
        try {
            const r = await frappe.call({
                method: 'erpnext.selling.page.point_of_sale.point_of_sale.search_by_term',
                args: {
                    search_term: term,
                    pos_profile: this.posProfile,
                    price_list: this.priceList,
                },
            });
            const items = r.message?.items || [];
            if (items.length) {
                this.addToCart(items[0].item_code, {
                    qty:       items[0].qty || 1,
                    rate:      items[0].price_list_rate || items[0].rate,
                    item_name: items[0].item_name,
                });
            } else {
                frappe.show_alert({ message: `Not found: ${term}`, indicator: 'red' }, 3);
            }
        } catch(e) {
            frappe.show_alert({ message: 'Search error', indicator: 'red' }, 3);
        }
    }

    async handleWeighBarcode(barcode) {
        try {
            const r = await frappe.call({
                method: 'retail_erp.retail_operations.utils.get_wl_data_by_barcode',
                args: { barcode },
            });
            const d = r.message;
            if (!d || !d.item_code) {
                frappe.show_alert({ message: 'Weigh label not found', indicator: 'red' }, 3);
                return;
            }
            // qty = exact net weight, rate = per kg rate
            this.addToCart(d.item_code, {
                qty:       d.qty,
                rate:      d.rate,
                item_name: d.item_name,
                isWeigh:   true,
            });
        } catch(e) {
            frappe.show_alert({ message: 'Weigh label error: ' + e.message, indicator: 'red' }, 3);
        }
    }

    // ── CUSTOMER ───────────────────────────────────────────────
    async onCustomerChange() {
        const customer = document.getElementById('rpos-customer').value;
        try {
            const r = await frappe.call({
                method: 'retail_erp.retail_operations.utils.get_loyalty_points',
                args: { customer },
            });
            const badge = document.getElementById('rpos-loyalty');
            if (r.message?.points > 0) {
                badge.textContent = `${r.message.tier} · ${r.message.points} pts`;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        } catch(e) {}
    }

    // ── CLOCK ──────────────────────────────────────────────────
    setupClock() {
        const tick = () => {
            const el = document.getElementById('rpos-clock');
            if (el) el.textContent = new Date().toLocaleTimeString('en-IN',
                { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        };
        tick();
        setInterval(tick, 1000);
    }
}

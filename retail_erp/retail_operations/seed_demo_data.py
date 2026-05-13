"""
RetailEdge v3 Demo Data
Run: bench --site mysite.local execute retail_erp.retail_operations.seed_demo_data.run
"""
import frappe
from frappe.utils import today


def run():
    print("=" * 60)
    print("  RetailEdge v3 Demo Data")
    print("=" * 60)

    company = frappe.defaults.get_user_default("Company") or "bizaxl"
    warehouse = frappe.db.get_value("Warehouse",
        {"company": company, "is_group": 0}, "name") or "Stores - B"
    pos_profile = frappe.db.get_value("POS Profile",
        {"company": company}, "name") or "Pos"
    print(f"Company: {company}")
    print(f"Warehouse: {warehouse}")
    print(f"POS Profile: {pos_profile}")

    # 1. Loyalty Program
    if not frappe.db.exists("Loyalty Program", "RetailEdge Rewards"):
        frappe.get_doc({
            "doctype": "Loyalty Program",
            "loyalty_program_name": "RetailEdge Rewards",
            "auto_opt_in": 1,
            "from_date": today(),
            "loyalty_program_type": "Multiple Tier Program",
            "conversion_factor": 0.25,
            "company": company,
            "collection_rules": [
                {"tier_name":"Standard","collection_factor":100,
                 "min_spent":0,"expiry_duration":365},
                {"tier_name":"Silver","collection_factor":90,
                 "min_spent":5000,"expiry_duration":365},
                {"tier_name":"Gold","collection_factor":80,
                 "min_spent":15000,"expiry_duration":365},
            ],
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Loyalty Program: RetailEdge Rewards")
    else:
        print("✅ Loyalty Program exists")

    # 2. Customers
    for cname in ["Walk-In Customer", "Rahul Mehta", "Priya Sharma"]:
        if not frappe.db.exists("Customer", cname):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": cname,
                "customer_type": "Individual",
                "customer_group": "Individual",
                "territory": "India",
                "loyalty_program": "RetailEdge Rewards",
            }).insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"  Created customer: {cname}")
        else:
            print(f"  Customer exists: {cname}")

    # 3. Items with opening stock
    items = [
        ("Basmati Rice 5kg","Grocery","Kg",420,350,50),
        ("Whole Wheat Bread","Bakery","Nos",45,30,100),
        ("Full Cream Milk 1L","Dairy","Nos",68,55,80),
        ("Coca Cola 2L","Beverages","Nos",95,70,60),
        ("Colgate Toothpaste","Personal Care","Nos",110,85,40),
        ("Dove Soap Bar","Personal Care","Nos",55,40,60),
        ("Classmate Notebook","Stationery","Nos",65,45,100),
        ("Floor Cleaner 1L","Household","Nos",85,60,50),
        ("Cotton T-Shirt M","Apparel","Nos",499,350,30),
        ("Bluetooth Speaker","Electronics","Nos",1299,900,20),
    ]

    for code, group, uom, rate, val_rate, qty in items:
        if not frappe.db.exists("Item", code):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": code,
                "item_name": code,
                "item_group": group,
                "stock_uom": uom,
                "standard_rate": rate,
                "valuation_rate": val_rate,
                "is_stock_item": 1,
                "item_defaults": [{
                    "company": company,
                    "default_warehouse": warehouse,
                }]
            })
            doc.insert(ignore_permissions=True)

            # Set price list rate
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": code,
                "price_list": "Standard Selling",
                "selling": 1,
                "currency": "INR",
                "price_list_rate": rate,
            }).insert(ignore_permissions=True)

            # Opening stock via Stock Entry
            try:
                se = frappe.get_doc({
                    "doctype": "Stock Entry",
                    "stock_entry_type": "Material Receipt",
                    "company": company,
                    "items": [{
                        "item_code": code,
                        "t_warehouse": warehouse,
                        "qty": qty,
                        "basic_rate": val_rate,
                    }]
                })
                se.insert(ignore_permissions=True)
                se.submit()
                print(f"  Created: {code} | stock={qty}")
            except Exception as e:
                print(f"  Item created but stock failed: {code} — {e}")
            frappe.db.commit()
        else:
            print(f"  Item exists: {code}")

    # 4. Store Profile
    if not frappe.db.exists("Store Profile", "Main Street Store"):
        frappe.get_doc({
            "doctype": "Store Profile",
            "store_name": "Main Street Store",
            "warehouse": warehouse,
            "pos_profile": pos_profile,
            "company": company,
        }).insert(ignore_permissions=True)
        frappe.db.commit()
        print("✅ Store Profile: Main Street Store")
    else:
        print("✅ Store Profile exists")

    print("")
    print("=" * 60)
    print("  Demo data complete!")
    print("  Open /point-of-sale to start billing")
    print("=" * 60)

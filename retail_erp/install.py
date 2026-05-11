import frappe


def after_install():
    create_custom_roles()
    frappe.db.commit()
    print("retail_erp installed successfully.")


def create_custom_roles():
    roles = ["Cashier", "Store Manager", "Purchase Executive", "Accounts Manager"]
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1,
            }).insert(ignore_permissions=True)

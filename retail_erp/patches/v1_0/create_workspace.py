import frappe


def execute():
    frappe.db.commit()

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today, nowtime


class WeighLabel(Document):

    def validate(self):
        self.weigh_date = self.weigh_date or today()
        self.weigh_time = self.weigh_time or nowtime()
        gross = flt(self.gross_weight_kg)
        tare = flt(self.tare_weight_kg)
        if gross <= 0:
            frappe.throw(_("Gross weight must be greater than zero"))
        if tare >= gross:
            frappe.throw(_("Tare weight cannot be >= gross weight"))
        self.net_weight_kg = round(gross - tare, 3)
        self.total_amount = round(flt(self.net_weight_kg) * flt(self.unit_rate_per_kg), 2)
        self.status = "Weighed"
        if self.name and not self.name.startswith("New Weigh"):
            self.barcode_string = f"WL-{self.name}"

    def after_insert(self):
        self.barcode_string = f"WL-{self.name}"
        frappe.db.set_value("Weigh Label", self.name,
            "barcode_string", self.barcode_string)
        self._register_erpnext_barcode()
        frappe.db.commit()

    def on_trash(self):
        frappe.db.delete("Item Barcode", {"barcode": f"WL-{self.name}"})

    def _register_erpnext_barcode(self):
        try:
            barcode_val = f"WL-{self.name}"
            encoded = f"{self.net_weight_kg}|{self.unit_rate_per_kg}|{self.name}"
            frappe.db.delete("Item Barcode", {"barcode": barcode_val})
            frappe.db.sql("""
                INSERT INTO `tabItem Barcode`
                (name, parent, parenttype, parentfield, idx,
                 creation, modified, modified_by, owner,
                 barcode, barcode_type, uom)
                VALUES (%s, %s, 'Item', 'barcodes', 99,
                 NOW(), NOW(), 'Administrator', 'Administrator',
                 %s, 'CODE128', %s)
            """, (frappe.generate_hash("", 10), self.item,
                  barcode_val, encoded))
            frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(),
                "WeighLabel Barcode Registration")

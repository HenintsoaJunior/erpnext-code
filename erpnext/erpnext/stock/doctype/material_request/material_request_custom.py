import frappe
from frappe import _

import frappe
from frappe import _

def _create_material_request(material_request_type, company, schedule_date, items, customer=None, set_warehouse=None):
    try:
        doc = frappe.get_doc({
            "doctype": "Material Request",
            "material_request_type": material_request_type,
            "company": company,
            "schedule_date": schedule_date,
            "transaction_date": frappe.utils.today(),
            "customer": customer,
            "set_warehouse": set_warehouse,
            "items": []
        })

        for item in items:
            doc.append("items", {
                "item_code": item["item_code"],
                "qty": item["qty"],
                "uom": item.get("uom", "Nos"),
                "schedule_date": schedule_date,
                "warehouse": item.get("warehouse", set_warehouse)
            })

        doc.insert()
        doc.submit()  # 🟢 Soumission ici
        frappe.db.commit()
        frappe.msgprint(_("Material Request {0} created and submitted").format(doc.name))
        return doc.name

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Material Request Creation Error")
        frappe.throw(_("Une erreur est survenue lors de la création de la demande de matériel : {0}").format(str(e)))

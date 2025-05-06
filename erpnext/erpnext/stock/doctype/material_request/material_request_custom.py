import frappe
from frappe import _

def _create_material_request(ref, material_request_type, company, schedule_date, items, customer=None, set_warehouse=None):
    try:
        # Vérifier si le nom 'ref' existe déjà
        if frappe.db.exists("Material Request", ref):
            frappe.throw(_("Une demande de matériel avec le nom {0} existe déjà").format(ref))

        # Créer le document sans spécifier de nom (laisser Frappe générer un nom temporaire)
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

        # Ajouter les articles
        for item in items:
            doc.append("items", {
                "item_code": item["item_code"],
                "qty": item["qty"],
                "uom": item.get("uom", "Nos"),
                "schedule_date": schedule_date,
                "warehouse": item.get("warehouse", set_warehouse)
            })

        # Insérer le document (avec un nom temporaire généré par Frappe)
        doc.insert()

        # Renommer le document pour utiliser la valeur de 'ref'
        frappe.rename_doc("Material Request", doc.name, ref, force=True)

        # Recharger le document après le renommage
        doc = frappe.get_doc("Material Request", ref)

        # Soumettre le document
        doc.submit()
        frappe.db.commit()
        frappe.msgprint(_("Material Request {0} created and submitted").format(doc.name))
        return doc.name

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Material Request Creation Error: {ref}")
        frappe.throw(_("Une erreur est survenue lors de la création de la demande de matériel : {0}").format(str(e)))
import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_linked_doctypes(field):
    linked_docs = []
    
    # Récupérer tous les doctypes
    for doctype in frappe.get_all("DocType", pluck="name"):
        meta = frappe.get_meta(doctype)
        for f in meta.fields:
            if f.fieldtype == "Link" and f.options == field:
                linked_docs.append({
                    "doctype": doctype,
                    "fieldname": f.fieldname,
                    "label": f.label
                })
    
    # Trier les résultats par ordre alphabétique du doctype
    linked_docs.sort(key=lambda x: x["doctype"].lower())
    
    return {"linked_doctypes": linked_docs}
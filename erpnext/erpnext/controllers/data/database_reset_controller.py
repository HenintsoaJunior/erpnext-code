import frappe
from frappe import _
from erpnext.utils.mapper.DocTypeResetter import DocTypeResetter
import urllib.parse
import json

@frappe.whitelist()
def reset_specific_doctypes():
    try:
        doctype_order = ["Supplier","Item","Item Price","Item Default","Material Request Item", "Material Request","Supplier Quotation Item",
                         "Supplier Quotation","Request for Quotation","Request for Quotation Item","Request for Quotation Supplier",
                         "Purchase Order Item","Purchase Order","Purchase Receipt","Purchase Receipt Item","Payment Entry","Payment Request","Payment Entry Reference","Payment Ledger Entry",
                         "Purchase Invoice Item","Purchase Invoice","Stock Entry","Stock Entry Detail","Stock Ledger Entry","Bin","GL Entry","Fichier1","Fichier2","Fichier3","Warehouse"
                        ]
        
        for doctype in doctype_order:
            if not frappe.db.exists("DocType", doctype):
                raise Exception(f"DocType '{doctype}' does not exist")
            if not frappe.has_permission(doctype, "delete"):
                raise Exception(f"User lacks delete permission for DocType '{doctype}'")
        
        resetter = DocTypeResetter(doctype_order)
        # Uncomment to test conditional reset
        # status, message = resetter.reset_doctype_except("Import2", "item_code", "ITEM002")
        # if not status:
        #     raise Exception(message)

        results = resetter.reset_doctypes()
        
        # Check if any resets failed
        failed_results = {k: v[1] for k, v in results.items() if not v[0]}
        if failed_results:
            response = {
                "status": "partial_success",
                "results": {k: v[1] for k, v in results.items()}
            }
        else:
            response = {
                "status": "success",
                "results": {k: v[1] for k, v in results.items()}
            }
        
        response_json = json.dumps(response)
        encoded_response = urllib.parse.quote(response_json)
        
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/app/resetsuccess?data={encoded_response}"
        
    except Exception as e:
        frappe.log_error(f"Reset operation failed: {str(e)}")
        response = {
            "status": "error",
            "message": str(e)
        }
        response_json = json.dumps(response)
        encoded_response = urllib.parse.quote(response_json)
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/app/resetsuccess?data={encoded_response}"
import frappe
from frappe import _
from frappe.model.document import Document
import json
from erpnext.utils.mapper.ImportMapper import ImportMapper
import logging

logger = logging.getLogger(__name__)

class ImportController(Document):
    pass

@frappe.whitelist(allow_guest=False)
@frappe.whitelist(allow_guest=False)
def import_csv_files(files_data):
    try:
        files_data = json.loads(files_data) if isinstance(files_data, str) else files_data
        
        if not files_data:
            frappe.throw(_("Missing required parameter: files_data"))
            
        logger.info(f"Received files_data: {files_data}")
        
        mapper = ImportMapper(
            doctypes={
                "Fichier1": "Fichier1",
                "Fichier2": "Fichier2",
                "Fichier3": "Fichier3" 
            },
            column_mappings={
                "Fichier1": {
                    "date": "date",
                    "item_name": "item_name",
                    "item_groupe": "item_groupe",
                    "required_by": "required_by",
                    "quantity": "quantity",
                    "purpose": "purpose",
                    "target_warehouse": "target_warehouse",
                    "ref": "ref"
                },
                "Fichier2": {
                    "supplier_name": "supplier_name",
                    "country": "country",
                    "type": "type"
                },
                "Fichier3": {
                    "ref_request_quotation": "ref_request_quotation",
                    "supplier": "supplier"
                }
            },
            numeric_fields={
                "Fichier1": ["quantity"]
            },
            date_validation={
                "Fichier1": {
                    "date": {
                        "min_date": None,
                        "max_date": None       
                    }
                }
            },
            valid_values={
                "Fichier1": {
                   "item_groupe": ["piece", "consommable"],
                   "purpose": ["Purchase"], 
                },
                "Fichier2": {
                   "type": ["Company", "Individual", "Partnership"], 
                },
                "Fichier3": {}
            },
            separator=","
        )
        
        all_errors = []
        
        logger.info("Validating ref_request_quotation against ref")
        validation_result = mapper.validate_cross_file_columns(
            files_data=files_data,
            file1_name="Fichier1",
            file1_column="ref",
            file2_name="Fichier3",
            file2_column="ref_request_quotation"
        )
        
        if validation_result["status"] == "error":
            logger.warning(f"Cross-file validation failed: {validation_result['message']}")
            all_errors.append({
                "code": "cross_file_validation",
                "field": "ref_request_quotation",
                "message": validation_result["message"],
                "details": validation_result.get("details")
            })
        
        logger.info("Calling process_import")
        import_result = mapper.process_import(files_data)
        
        if import_result["status"] == "errors":
            all_errors.extend(import_result["errors"])
        
        if all_errors:
            return {
                "status": "errors",
                "data": None,
                "errors": all_errors
            }
        
        return import_result
        
    except json.JSONDecodeError as json_error:
        frappe.log_error(f"JSON parse error: {str(json_error)}", "ImportController.import_csv_files")
        return {
            "status": "errors",
            "data": None,
            "errors": [{
                "code": "json_error",
                "field": "json",
                "message": _("Invalid JSON format: {0}").format(str(json_error)),
                "details": None
            }]
        }
    except Exception as e:
        frappe.log_error(f"Import error: {str(e)}", "ImportController.import_csv_files")
        return {
            "status": "errors",
            "data": None,
            "errors": [{
                "code": None,
                "field": "exception",
                "message": _("Failed to process import: {0}").format(str(e)),
                "details": None
            }]
        }
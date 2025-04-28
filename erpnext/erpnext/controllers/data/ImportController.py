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
def import_csv_files(files_data):
    try:
        files_data = json.loads(files_data) if isinstance(files_data, str) else files_data
        if not files_data:
            frappe.throw(_("Missing required parameter: files_data"))
            
        logger.info(f"Received files_data: {files_data}")
        
        mapper = ImportMapper(
            doctypes={
                "input1": "Import1",
                "input2": "Import2"
            },
            column_mappings={
                "input1": {
                    "csv_column_name": "item_code",
                    "name_column": "item_name",
                    "date_test": "date_test"
                },
                "input2": {
                    "customer_name": "customer_name",
                    "customer_type": "customer_type",
                }
            },
            numeric_fields={
                # "input1": ["csv_column_name"],
                # "input2": ["customer_name"]
            },
            valid_values={
                # "input1": {
                #     "csv_column_name": ["ITEM001", "ITEM002"]
                # },
                # "input2": {
                #     "csv_column_name": ["ITEM001", "ITEM002"]
                # }
            },
            separator=","
        )
        
        logger.info("Calling process_import")
        import_result = mapper.process_import(files_data)

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

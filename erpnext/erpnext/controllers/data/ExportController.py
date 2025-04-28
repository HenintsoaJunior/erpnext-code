import frappe
from frappe.model.document import Document
import logging
from erpnext.utils.service.ExportService import ExportService
import json

# Configure logging
logger = logging.getLogger(__name__)

class ExportController(Document):
    pass

@frappe.whitelist(allow_guest=True)
def export_import2_data():
    export_config = {
        "doctype": "Import2",
        "fields": ["customer_name", "customer_type"],
        "file_name": "import2_export.csv"
    }
    return _handle_export_request(export_config)

@frappe.whitelist()
def export_data(doctype="Import2", filters=None, fields=None, file_name=None,
               delimiter=",", is_private=0):
    """Flexible endpoint for exporting any doctype with custom parameters"""
    if fields is None:
        fields = ["customer_name", "customer_type"]
    
    if filters and isinstance(filters, str):
        filters = json.loads(filters)
        
    export_config = {
        "doctype": doctype,
        "filters": filters,
        "fields": fields,
        "file_name": file_name,
        "delimiter": delimiter,
        "is_private": is_private
    }
    return _handle_export_request(export_config)

@frappe.whitelist(allow_guest=True)
def export_multi_doctype_data(config=None):
    """Export data from multiple related doctypes"""
    try:
        if not config:
            config = _get_default_multi_export_config()
        elif isinstance(config, str):
            config = json.loads(config)
        
        logger.info(f"Starting multi-doctype export with primary doctype: {config.get('primary_doctype')}")
        
        export_service = ExportService()
        result = export_service.export_multi_doctype(config)
        
        return _handle_export_response(result)
    except Exception as e:
        logger.error(f"Multi-doctype export failed with error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error in multi-doctype export: {str(e)}",
            "file_url": None
        }

def _handle_export_request(export_config):
    """Common handler for export requests"""
    try:
        logger.info(f"ExportController: Starting export for doctype {export_config.get('doctype')}")
        export_service = ExportService()
        result = export_service.export_to_csv(**export_config)
        
        return _handle_export_response(result)
    except Exception as e:
        logger.error(f"ExportController: Export failed with error {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error in export controller: {str(e)}",
            "file_url": None
        }

def _handle_export_response(result):
    """Common handler for export responses"""
    if result.get('status') == 'success' and result.get('csv_content'):
        frappe.response['doctype'] = result.get('doctype', '')
        frappe.response['filename'] = result.get('file_name')
        frappe.response['result'] = result.get('csv_content').encode('utf-8')
        frappe.response['type'] = 'csv'
        return
    else:
        return result

def _get_default_multi_export_config():
    """Returns default configuration for multi-doctype export"""
    return {
        "primary_doctype": "Import2",
        "primary_filters": {"customer_name": "DAXIDO"},
        "primary_fields": ["customer_name", "customer_type"],
        "related_doctypes": [
            {
                "doctype": "Customer",
                "join_field": "customer_name",
                "fields": ["language"],
                "filters": {}
            }
        ],
        "file_name": "import2_customer_export.csv",
        "delimiter": ",",
        "is_private": 0
    }
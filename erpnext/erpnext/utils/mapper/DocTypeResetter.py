import frappe
from frappe import _
import logging

# Configure logger
logger = frappe.logger("doctype_resetter", allow_site=True)

class DocTypeResetter:
    def __init__(self, doctype_order=None):
        self.doctype_dependencies = doctype_order or []
        self.except_conditions = {}

    def reset_doctype(self, doctype):
        try:
            logger.info(f"Starting reset of DocType '{doctype}'")
            
            if not frappe.db.exists("DocType", doctype):
                logger.error(f"DocType '{doctype}' does not exist")
                return False, f"DocType '{doctype}' does not exist"

            if not frappe.has_permission(doctype, "delete"):
                logger.error(f"User lacks delete permission for DocType '{doctype}'")
                return False, f"User lacks delete permission for DocType '{doctype}'"

            conditions = self.except_conditions.get(doctype, {})
            logger.info(f"Resetting '{doctype}' with conditions: {conditions}")

            initial_count = frappe.db.count(doctype)
            logger.info(f"Initial record count for '{doctype}': {initial_count}")

            frappe.db.delete(doctype, conditions)
            
            final_count = frappe.db.count(doctype)
            deleted_count = initial_count - final_count
            
            frappe.db.commit()
            
            logger.info(f"DocType '{doctype}' reset: Deleted {deleted_count} records, {final_count} records remain")
            
            return True, f"Deleted {deleted_count} records"
            
        except Exception as e:
            logger.error(f"Error resetting DocType '{doctype}': {str(e)}")
            frappe.log_error(f"Failed to reset {doctype}: {str(e)}")
            return False, f"Error: {str(e)}"

    def reset_doctype_except(self, doctype, field, value):
        try:
            logger.info(f"Setting reset condition for '{doctype}': preserve '{field} = {value}'")
            
            if not frappe.db.exists("DocType", doctype):
                logger.error(f"DocType '{doctype}' does not exist")
                return False, f"DocType '{doctype}' does not exist"
            
            if not frappe.get_meta(doctype).has_field(field):
                logger.error(f"Field '{field}' does not exist in DocType '{doctype}'")
                return False, f"Field '{field}' does not exist in DocType '{doctype}'"
            
            self.except_conditions[doctype] = {field: ["!=", value]}
            
            logger.info(f"Condition set for '{doctype}' to preserve '{field} = {value}'")
            return True, f"Condition set to preserve '{field} = {value}'"
            
        except Exception as e:
            logger.error(f"Error setting condition for '{doctype}': {str(e)}")
            frappe.log_error(f"Failed to set condition for {doctype}: {str(e)}")
            return False, f"Error: {str(e)}"

    def reset_doctypes(self, doctypes=None):
        results = {}
        doctypes_to_reset = doctypes or self.doctype_dependencies
        
        if not doctypes_to_reset:
            logger.warning("No DocTypes specified for reset")
            return results
            
        logger.info("Starting reset of multiple DocTypes")
        
        for doctype in doctypes_to_reset:
            status, message = self.reset_doctype(doctype)
            results[doctype] = (status, message)
        
        logger.info("Completed reset of DocTypes")
        return results

    def set_doctype_dependencies(self, dependencies):
        self.doctype_dependencies = dependencies
        logger.info(f"DocType dependencies set: {', '.join(dependencies)}")
        return self

    def get_doctype_dependencies(self):
        return self.doctype_dependencies

    def detect_doctype_dependencies(self):
        logger.info("Starting detection of DocType dependencies")
        
        doctypes = frappe.get_all("DocType", filters={"istable": 0}, pluck="name")
        foreign_keys = {}
        
        for doctype in doctypes:
            fields = frappe.get_meta(doctype).get("fields", {"fieldtype": "Link"})
            for field in fields:
                if field.fieldtype == "Link" and field.options:
                    if doctype not in foreign_keys:
                        foreign_keys[doctype] = []
                    if field.options not in foreign_keys[doctype]:
                        foreign_keys[doctype].append(field.options)
        
        visited = set()
        sorted_doctypes = []
        
        def visit(doctype):
            if doctype in visited:
                return
            visited.add(doctype)
            
            dependencies = foreign_keys.get(doctype, [])
            for dep in dependencies:
                if dep in doctypes:
                    visit(dep)
            
            sorted_doctypes.append(doctype)
        
        for doctype in doctypes:
            visit(doctype)
        
        self.doctype_dependencies = list(reversed(sorted_doctypes))
        logger.info(f"Detected DocType order: {', '.join(self.doctype_dependencies)}")
        return self
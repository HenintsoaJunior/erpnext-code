from erpnext.services.customers.customer_service import get_all_customers
import frappe

@frappe.whitelist() 
def data(customer_type=None, email=None):
    return get_all_customers(customer_type, email)

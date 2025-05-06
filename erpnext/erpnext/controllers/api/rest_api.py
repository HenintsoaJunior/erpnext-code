from erpnext.services.customers.customer_service import get_all_customers
from erpnext.services.fournisseur.fournisseur_service import get_all_suppliers
from erpnext.services.fournisseur.fournisseur_service import get_all_supplier_quotations
from erpnext.services.fournisseur.fournisseur_service import make_update_quotation_item
from erpnext.services.fournisseur.fournisseur_service import make_request_quotation_price
from erpnext.services.fournisseur.fournisseur_service import get_all_purchase_orders
from erpnext.services.fournisseur.fournisseur_service import get_all_request_for_quotations
from erpnext.services.compta.facture_service import get_purchase_invoices
from erpnext.services.compta.facture_service import create_payment_entry

import frappe

#################################################FOURNISSEUR################################################################################

@frappe.whitelist()
def purchase_orders(supplier=None,status_filter=None):
    return get_all_purchase_orders(supplier,status_filter)

@frappe.whitelist()
def data(customer_type=None, email=None):
    return get_all_customers(customer_type, email)

@frappe.whitelist()
def fournisseur():
    return get_all_suppliers()

@frappe.whitelist()
def supplier_quotations(supplier=None):
    return get_all_supplier_quotations(supplier)


@frappe.whitelist()
def request_quotations(supplier=None):
    return get_all_request_for_quotations(supplier)


@frappe.whitelist()
def update_quotation_item(quotation_name, item_code, rate):
    try:
        quotation_name = quotation_name
        item_code = item_code
        rate = rate

        if not all([quotation_name, item_code, rate]):
            return {
                "status": "error",
                "message": "Les paramètres quotation_name, item_code et rate sont requis.",
                "data": None,
                "errors": None
            }

        return make_update_quotation_item(quotation_name, item_code, rate)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la mise à jour : {str(e)}",
            "data": None,
            "errors": str(e)
        }
    
@frappe.whitelist()
def update_request_quotation():
    try:
        data = frappe.request.get_json()
        quotation_name = data.get("quotation_name")
        item_code = data.get("item_code")
        rate = data.get("rate")

        if not all([quotation_name, item_code, rate]):
            return {
                "status": "error",
                "message": "Les paramètres quotation_name, item_code et rate sont requis.",
                "data": None,
                "errors": None
            }

        return make_request_quotation_price(quotation_name, item_code, rate)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la mise à jour : {str(e)}",
            "data": None,
            "errors": str(e)
        }
    
######################################################COMPATBLE###########################################################################

@frappe.whitelist()
def purchase_invoices():
    return get_purchase_invoices()


@frappe.whitelist()
def payment_entry(invoice_name=None,paid_amount=None):
    return create_payment_entry(invoice_name,paid_amount)


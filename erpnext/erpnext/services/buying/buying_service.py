import frappe
from frappe import _
from erpnext.stock.doctype.material_request.material_request_custom import _create_material_request
from erpnext.stock.doctype.material_request.material_request import make_request_for_quotation
from erpnext.buying.doctype.request_for_quotation.request_for_quotation import make_supplier_quotation_from_rfq
from erpnext.buying.doctype.supplier_quotation.supplier_quotation import make_purchase_order
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
from erpnext.buying.doctype.supplier.test_supplier import create_supplier

import json
    

##########################################################SUPPLIER####################################################################

@frappe.whitelist()
def create_new_supplier(supplier_name, default_currency="USD", supplier_type="Company", supplier_group="Services",country=None):
    try:
        supplier = create_supplier(
            supplier_name=supplier_name,
            default_currency=default_currency,
            supplier_type=supplier_type,
            supplier_group=supplier_group,
            country=country
        )
        frappe.db.commit()
        frappe.msgprint(_("Supplier  {0} created and submitted").format(supplier.name))

        return {
            "status": "success",
            "message": f"Supplier {supplier.name} créé avec succès.",
            "data": {
                "supplier_name": supplier.name
            }
        }
    except Exception as e:
        frappe.log_error(str(e), "Erreur lors de la création du Supplier")
        return {
            "status": "error",
            "message": f"Erreur lors de la création du Supplier: {str(e)}",
            "data": None
        }

##########################################################ITEM####################################################################

def create_item(
    item_code,
    item_name,
    is_stock_item=1,
    valuation_rate=0,
    stock_uom="Nos",
    warehouse="_Test Warehouse - _TC",
    is_customer_provided_item=None,
    customer=None,
    is_purchase_item=None,
    opening_stock=0,
    is_fixed_asset=0,
    asset_category=None,
    buying_cost_center=None,
    selling_cost_center=None,
    company="_Test Company",
    item_group=None
):
    if not frappe.db.exists("Item", item_code):
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = item_name
        item.description = item_code
        item.item_group = item_group
        item.stock_uom = stock_uom
        item.is_stock_item = is_stock_item
        item.is_fixed_asset = is_fixed_asset
        item.asset_category = asset_category
        item.opening_stock = opening_stock
        item.valuation_rate = valuation_rate
        item.is_purchase_item = is_purchase_item
        item.is_customer_provided_item = is_customer_provided_item
        item.customer = customer or ""
        item.append(
            "item_defaults",
            {
                "default_warehouse": warehouse,
                "company": company,
                "selling_cost_center": selling_cost_center,
                "buying_cost_center": buying_cost_center,
            },
        )
        item.save()
    else:
        item = frappe.get_doc("Item", item_code)
    return item

@frappe.whitelist()
def create_new_item(item_code,item_name, is_stock_item=1, valuation_rate=0, stock_uom="Nos", warehouse="_Test Warehouse - _TC", company="_Test Company",item_group="All Item Groups"):
    try:
        item = create_item(
            item_code=item_code,
            item_name=item_name,
            is_stock_item=is_stock_item,
            valuation_rate=valuation_rate,
            stock_uom=stock_uom,
            warehouse=warehouse,
            company=company,
            item_group=item_group
        )

        frappe.msgprint(_("Item  {0} created and submitted").format(item.name))
        return {
            "status": "success",
            "message": f"Item {item.name} créé avec succès.",
            "data": {
                "item_code": item.item_code,
                "item_name": item.item_name
            }
        }
    except Exception as e:
        frappe.log_error(str(e), "Erreur lors de la création de l'Item")
        return {
            "status": "error",
            "message": f"Erreur lors de la création de l'Item: {str(e)}",
            "data": None
        }
##########################################################MATERIAL REQUEST####################################################################
@frappe.whitelist()
def create_material_request(ref,material_request_type, company, schedule_date, items, customer=None,set_warehouse=None):
    return _create_material_request(ref,material_request_type, company, schedule_date, items, customer,set_warehouse)


##########################################################REQUEST FOR QUOTATION####################################################################

@frappe.whitelist()
def create_request_for_quotation(material_request_name, suppliers=None, message_for_supplier=None):
    
    try:
        if isinstance(suppliers, str):
            suppliers = json.loads(suppliers)

        if not suppliers:
            return {
                "status": "error",
                "message": "Veuillez fournir au moins un fournisseur.",
                "data": None
            }

        if not message_for_supplier:
            message_for_supplier = "Merci de nous faire parvenir votre meilleure offre de prix."

        rfq_doc = make_request_for_quotation(material_request_name)

        rfq_doc.suppliers = []
        for supplier in suppliers:
            rfq_doc.append("suppliers", {
                "supplier": supplier
            })

        rfq_doc.message_for_supplier = message_for_supplier

        rfq_doc.insert()
        rfq_doc.submit()
        frappe.db.commit()

        
        return {
            "status": "success",
            "message": f"RFQ créé et soumis avec les fournisseurs à partir de {material_request_name}.",
            "data": {
                "rfq_name": rfq_doc.name
            }
        }

    except Exception as e:
        frappe.log_error(str(e), "Erreur création/soumission RFQ")
        return {
            "status": "error",
            "message": f"Erreur lors de la création du RFQ: {str(e)}",
            "data": None
        }


##########################################################SUPPLIER QUOTATION####################################################################

@frappe.whitelist()
def create_supplier_quotation_from_rfq(rfq_name, supplier, item_rates=None):
	try:
		import json

		if isinstance(item_rates, str):
			item_rates = json.loads(item_rates)

		doc = make_supplier_quotation_from_rfq(source_name=rfq_name, for_supplier=supplier)

		if item_rates:
			for item in doc.items:
				item_code = item.item_code
				if item_code in item_rates:
					item.rate = item_rates[item_code]

		doc.insert()
		doc.submit()

		return {
			"status": "success",
			"message": f"Supplier Quotation {doc.name} créé et soumis avec succès.",
			"name": doc.name
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Erreur dans create_supplier_quotation_from_rfq")
		return {
			"status": "error",
			"message": f"Erreur lors de la création du Supplier Quotation: {str(e)}"
		}


##########################################################PURCHASE ORDER####################################################################

@frappe.whitelist()
def create_purchase_order_from_supplier_quotation(source_name):
    try:
        doc = make_purchase_order(source_name=source_name)
        doc.insert() 
        doc.submit()

        return {
            "status": "success",
            "message": f"Purchase Order {doc.name} créé avec succès à partir de {source_name}.",
            "data": {
                "purchase_order_name": doc.name
            }
        }

    except Exception as e:
        frappe.log_error(str(e), "Erreur lors de la création du Purchase Order")
        return {
            "status": "error",
            "message": f"Erreur lors de la création du Purchase Order: {str(e)}",
            "data": None
        }

##########################################################Purchase Receipt####################################################################
@frappe.whitelist()
def create_purchase_receipt_from_purchase_order(purchase_order_name):
    try:
        doc = make_purchase_receipt(source_name=purchase_order_name)

        if not doc.items:
            return {
                "status": "error",
                "message": "Aucun article éligible à la réception dans ce bon de commande.",
                "data": None
            }

        doc.insert()
        doc.submit()

        return {
            "status": "success",
            "message": f"Purchase Receipt {doc.name} créé avec succès à partir de {purchase_order_name}.",
            "data": {
                "purchase_receipt_name": doc.name
            }
        }

    except Exception as e:
        frappe.log_error(str(e), "Erreur lors de la création du Purchase Receipt")
        return {
            "status": "error",
            "message": f"Erreur lors de la création du Purchase Receipt: {str(e)}",
            "data": None
        }
    
##########################################################Purchase Invoice####################################################################
@frappe.whitelist()
def create_purchase_invoice_from_purchase_receipt(purchase_receipt_name):
    try:
        doc = make_purchase_invoice(source_name=purchase_receipt_name)

        if not doc.items:
            return {
                "status": "error",
                "message": "Aucun article disponible pour la facturation dans ce Purchase Receipt.",
                "data": None
            }

        doc.insert()
        doc.submit()

        return {
            "status": "success",
            "message": f"Purchase Invoice {doc.name} créé avec succès à partir de {purchase_receipt_name}.",
            "data": {
                "purchase_invoice_name": doc.name
            }
        }

    except Exception as e:
        frappe.log_error(str(e), "Erreur lors de la création du Purchase Invoice")
        return {
            "status": "error",
            "message": f"Erreur lors de la création du Purchase Invoice: {str(e)}",
            "data": None
        }

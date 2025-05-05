import frappe
from frappe import _

###########################################################COMMANDE###################################################################
def is_order_paid(order_name):
    """Check if a purchase order has at least one paid invoice."""
    try:
        invoices = frappe.get_all(
            "Purchase Invoice",
            filters={"purchase_order": order_name, "docstatus": 1},
            fields=["status"]
        )
        return any(invoice.status == "Paid" for invoice in invoices)
    except Exception as e:
        frappe.log_error(f"Error in is_order_paid for order {order_name}: {str(e)}")
        return False

def is_order_received(order_name):
    """Check if a purchase order has at least one submitted purchase receipt."""
    try:
        receipts = frappe.get_all(
            "Purchase Receipt Item",
            filters={"purchase_order": order_name, "docstatus": 1},
            limit=1
        )
        return len(receipts) > 0
    except Exception as e:
        frappe.log_error(f"Error in is_order_received for order {order_name}: {str(e)}")
        return False

def get_paid_order_names():
    """Retrieve names of purchase orders with paid invoices."""
    try:
        paid_orders = frappe.get_all(
            "Purchase Invoice",
            filters={"status": "Paid", "docstatus": 1, "purchase_order": ["not in", [None, ""]]},
            fields=["purchase_order"],
            pluck="purchase_order"
        )
        return paid_orders if paid_orders else []
    except Exception as e:
        frappe.log_error(f"Error in get_paid_order_names: {str(e)}")
        return []

def get_order_items(order_name):
    """Retrieve items of a purchase order."""
    try:
        items = frappe.get_all(
            "Purchase Order Item",
            filters={"parent": order_name},
            fields=["item_code", "item_name", "qty", "rate", "amount", "received_qty"]
        )
        return items
    except Exception as e:
        frappe.log_error(f"Error in get_order_items for order {order_name}: {str(e)}")
        return []

def get_all_purchase_orders(supplier=None, status_filter=None):
    """Retrieve all purchase orders based on supplier and status filters."""
    print("ENTERING get_all_purchase_orders with supplier=%s, status_filter=%s" % (supplier, status_filter))
    
    try:
        # Base filters for submitted purchase orders
        filters = {"docstatus": 1}
        if supplier:
            filters["supplier"] = supplier

        # Process status filters
        status_filters = []
        is_received_and_paid = False
        if status_filter:
            if isinstance(status_filter, str):
                status_filters = [s.strip() for s in status_filter.split(",")]
            elif isinstance(status_filter, list):
                status_filters = status_filter

            valid_statuses = ["received", "paid", "finish"]
            invalid_statuses = [s for s in status_filters if s not in valid_statuses]
            if invalid_statuses:
                return {
                    "status": "error",
                    "message": f"Invalid statuses: {', '.join(invalid_statuses)}. Valid statuses: {', '.join(valid_statuses)}.",
                    "data": None,
                    "errors": None
                }
            if sorted(status_filters) == ["paid", "received"] or status_filters == ["finish"]:
                is_received_and_paid = True

        # Apply paid filter only for 'paid' status, not for 'finish' or 'received,paid'
        paid_order_names = []
        if "paid" in status_filters and not is_received_and_paid:
            paid_order_names = get_paid_order_names()
            print("PAID ORDER NAMES: ", paid_order_names)
            if paid_order_names:
                filters["name"] = ["in", paid_order_names]

        # Fetch purchase orders
        purchase_orders_data = frappe.get_all(
            "Purchase Order",
            filters=filters,
            fields=[
                "name",
                "supplier",
                "supplier_name",
                "grand_total",
                "transaction_date",
                "status",
                "per_received",
                "per_billed"
            ],
            order_by="transaction_date desc"
        )
        print("PURCHASE ORDERS FETCHED: ", len(purchase_orders_data))

        # Process each order
        for order in purchase_orders_data:
            order["items"] = get_order_items(order.name)
            order["is_paid"] = is_order_paid(order.name)
            order["is_received"] = is_order_received(order.name)

        # Apply status filters if provided
        if status_filters:
            if is_received_and_paid:
                # For "finish" or "received,paid", require both conditions to be true
                print("Applying received,paid filter")
                purchase_orders_data = [
                    order for order in purchase_orders_data
                    if order["is_received"] and order["is_paid"]
                ]
            else:
                # For other cases, use OR logic
                print("Applying OR filter for ", status_filters)
                purchase_orders_data = [
                    order for order in purchase_orders_data
                    if (
                        ("received" in status_filters and order["is_received"]) or
                        ("paid" in status_filters and order["is_paid"])
                    )
                ]
        print("FILTERED PURCHASE ORDERS: ", len(purchase_orders_data))

        return {
            "status": "success",
            "data": {
                "purchase_orders": purchase_orders_data,
                "count": len(purchase_orders_data)
            },
            "message": "Purchase orders retrieved successfully.",
            "errors": None
        }

    except Exception as e:
        frappe.log_error(f"Error in get_all_purchase_orders: {str(e)}")
        print("ERROR in get_all_purchase_orders: ", str(e))
        return {
            "status": "error",
            "message": f"Error retrieving purchase orders: {str(e)}",
            "data": None,
            "errors": str(e)
        }


###########################################################SUPPLIER###################################################################
      
def get_all_suppliers():
    try:
        filters = {}
        suppliers_data = frappe.get_all(
            "Supplier",
            filters=filters,
            fields=["name", "email_id", "owner", "supplier_name", "supplier_type"],
            order_by="creation desc"
        )
        
        return {
            "status": "success",
            "data": {
                "suppliers": suppliers_data,
                "count": len(suppliers_data)
            },
            "message": "Données fournisseurs filtrées récupérées avec succès.",
            "errors": None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des données: {str(e)}",
            "data": None,
            "errors": str(e)
        }
    
def get_all_supplier_quotations(supplier=None):
    try:
        filters = {"status": ["!=", "Cancelled"]}  # Exclut les devis avec status "Cancelled"
        if supplier:
            filters["supplier"] = supplier
        
        quotations_data = frappe.get_all(
            "Supplier Quotation",
            filters=filters,
            fields=[
                "name",
                "supplier",
                "supplier_name",
                "transaction_date",
                "grand_total",
                "status"
            ],
            order_by="creation desc"
        )
        
        for quotation in quotations_data:
            items = frappe.get_all(
                "Supplier Quotation Item",
                filters={"parent": quotation["name"]},
                fields=["item_code", "item_name", "qty", "rate", "amount"]
            )
            quotation["items"] = items
        
        return {
            "status": "success",
            "data": {
                "quotations": quotations_data,
                "count": len(quotations_data)
            },
            "message": f"Données des demandes de devis récupérées avec succès. Filtre par supplier: {supplier or 'Aucun'}",
            "errors": None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des demandes de devis: {str(e)}",
            "data": None,
            "errors": str(e)
        }



###########################################################UPDATE###################################################################

@frappe.whitelist()
def update_quotation_item():
    try:
        success, result = extract_and_validate_request_data()
        if not success:
            return result
        
        quotation_name, item_code, rate = result
        
        success, result = validate_quotation_access(quotation_name)
        if not success:
            return result
            
        original_quotation = result
        
        success, result = validate_quotation_dependencies(quotation_name)
        if not success:
            return result
        
        return process_quotation_by_status(original_quotation, quotation_name, item_code, rate)
        
    except Exception as e:
        return handle_general_exception(e)
    
def validate_request_data(data):
    if not data:
        return False, {
            "status": "error",
            "message": _("Aucun corps JSON fourni dans la requête."),
            "data": None,
            "errors": "No JSON body provided"
        }

    quotation_name = data.get("quotation_name")
    item_code = data.get("item_code")
    rate = data.get("rate")

    if not all([quotation_name, item_code, rate]):
        return False, {
            "status": "error",
            "message": _("Les paramètres quotation_name, item_code et rate sont requis."),
            "data": None,
            "errors": None
        }

    try:
        rate = float(rate)
    except (TypeError, ValueError):
        return False, {
            "status": "error",
            "message": _("Le prix unitaire doit être un nombre valide."),
            "data": None,
            "errors": f"Invalid rate: {rate}"
        }

    if rate < 0:
        return False, {
            "status": "error",
            "message": _("Le prix unitaire doit être positif."),
            "data": None,
            "errors": None
        }
        
    return True, (quotation_name, item_code, rate)


def validate_quotation_dependencies(quotation_name):
    purchase_orders = frappe.get_all(
        "Purchase Order",
        filters={"supplier_quotation": quotation_name, "docstatus": 1},
        fields=["name"]
    )
    if purchase_orders:
        for po in purchase_orders:
            purchase_receipts = frappe.get_all(
                "Purchase Receipt",
                filters={"purchase_order": po.name, "docstatus": 1},
                fields=["name"]
            )
            if purchase_receipts:
                return False, {
                    "status": "error",
                    "message": _(f"Le devis {quotation_name} est lié à un reçu d'achat. La mise à jour n'est pas autorisée."),
                    "data": None,
                    "errors": None
                }
            # Annuler la Purchase Order si nécessaire
            try:
                po_doc = frappe.get_doc("Purchase Order", po.name)
                po_doc.cancel()
            except Exception as e:
                frappe.db.rollback()
                return False, {
                    "status": "error",
                    "message": _(f"Impossible d'annuler la commande {po.name} : {str(e)}"),
                    "data": None,
                    "errors": str(e)
                }
    return True, None

def validate_quotation_access(quotation_name):
    if not frappe.db.exists("Supplier Quotation", quotation_name):
        return False, {
            "status": "error",
            "message": _(f"Devis {quotation_name} non trouvé."),
            "data": None,
            "errors": None
        }

    quotation = frappe.get_doc("Supplier Quotation", quotation_name)
    
    if not frappe.has_permission("Supplier Quotation", "write", quotation_name):
        return False, {
            "status": "error",
            "message": _("Vous n'avez pas la permission de modifier ce devis."),
            "data": None,
            "errors": None
        }
        
    return True, quotation


def create_amended_quotation(original_quotation, item_code, rate):
    try:
        amended_doc = frappe.new_doc("Supplier Quotation")
        amended_doc.amended_from = original_quotation.name
        
        # Copier les champs principaux
        for field in original_quotation.meta.get_valid_columns():
            if field not in ["name", "docstatus", "amended_from", "amendment_date"]:
                amended_doc.set(field, original_quotation.get(field))
        
        # Copier les éléments de la table
        updated_item_qty = 0
        for item in original_quotation.items:
            new_item = amended_doc.append("items", {})
            for field in item.meta.get_valid_columns():
                if field != "name" and field != "parent":
                    new_item.set(field, item.get(field))
            
            # Mettre à jour le taux pour l'article spécifié
            if new_item.item_code == item_code:
                new_item.rate = rate
                new_item.amount = rate * new_item.qty
                updated_item_qty = new_item.qty
        
        # Copier les taxes et frais si présents
        if hasattr(original_quotation, "taxes"):
            for tax in original_quotation.taxes:
                new_tax = amended_doc.append("taxes", {})
                for field in tax.meta.get_valid_columns():
                    if field != "name" and field != "parent":
                        new_tax.set(field, tax.get(field))
        
        # Insérer et soumettre le nouveau devis
        amended_doc.insert()
        amended_doc.calculate_taxes_and_totals()
        amended_doc.save()
        amended_doc.submit()
        
        new_amount = rate * updated_item_qty
        
        return True, {
            "amended_doc": amended_doc,
            "new_amount": new_amount
        }
        
    except Exception as e:
        frappe.db.rollback()
        return False, {
            "status": "error",
            "message": _(f"Impossible de créer une nouvelle version du devis : {str(e)}"),
            "data": None,
            "errors": str(e)
        }


def update_draft_quotation(quotation_name, item_code, rate):
    try:
        # Récupérer l'article correspondant
        items = frappe.get_all(
            "Supplier Quotation Item",
            filters={"parent": quotation_name, "item_code": item_code},
            fields=["name", "rate", "qty", "amount"]
        )

        if not items:
            return False, {
                "status": "error",
                "message": _(f"Article {item_code} non trouvé dans le devis {quotation_name}."),
                "data": None,
                "errors": None
            }

        # Mettre à jour le rate et recalculer amount
        item = items[0]
        new_amount = rate * item.qty
        frappe.db.set_value(
            "Supplier Quotation Item",
            item.name,
            {
                "rate": rate,
                "amount": new_amount
            }
        )

        # Recalculer les totaux du devis
        quotation = frappe.get_doc("Supplier Quotation", quotation_name)
        quotation.calculate_taxes_and_totals()
        quotation.save()
        
        return True, {
            "quotation": quotation,
            "new_amount": new_amount
        }
    
    except Exception as e:
        frappe.db.rollback()
        return False, {
            "status": "error",
            "message": _(f"Erreur lors de la mise à jour du devis en brouillon : {str(e)}"),
            "data": None,
            "errors": str(e)
        }


def extract_and_validate_request_data():
    try:
        try:
            data = frappe.request.get_json()
        except Exception as e:
            return False, {
                "status": "error",
                "message": _("Corps JSON invalide ou manquant."),
                "data": None,
                "errors": f"JSONDecodeError: {str(e)}"
            }

        return validate_request_data(data)
        
    except Exception as e:
        frappe.log_error(
            message=f"Error extracting request data: {str(e)}",
            title="Data Extraction Error"
        )
        return False, {
            "status": "error",
            "message": _(f"Erreur lors de l'extraction des données : {str(e)}"),
            "data": None,
            "errors": str(e)
        }


def process_quotation_by_status(original_quotation, quotation_name, item_code, rate):
    try:
        if original_quotation.docstatus == 2:  # Annulé
            return process_cancelled_quotation(original_quotation, quotation_name, item_code, rate)
            
        elif original_quotation.docstatus == 1:  # Soumis
            return process_submitted_quotation(original_quotation, quotation_name, item_code, rate)
            
        else:  # Brouillon (docstatus == 0)
            return process_draft_quotation(quotation_name, item_code, rate)
            
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(
            message=f"Error in process_quotation_by_status: {str(e)}",
            title="Quotation Processing Error"
        )
        return {
            "status": "error",
            "message": _(f"Erreur lors du traitement du devis : {str(e)}"),
            "data": None,
            "errors": str(e)
        }


def process_cancelled_quotation(original_quotation, quotation_name, item_code, rate):
    success, result = create_amended_quotation(original_quotation, item_code, rate)
    if not success:
        return result
        
    return format_amended_response(result, quotation_name, item_code, rate)


def process_submitted_quotation(original_quotation, quotation_name, item_code, rate):
    try:
        original_quotation.cancel()
    except Exception as e:
        frappe.db.rollback()
        return {
            "status": "error",
            "message": _(f"Impossible d'annuler le devis {quotation_name} : {str(e)}"),
            "data": None,
            "errors": str(e)
        }
        
    # Créer une version amendée
    success, result = create_amended_quotation(original_quotation, item_code, rate)
    if not success:
        return result
        
    return format_amended_response(result, quotation_name, item_code, rate)


def process_draft_quotation(quotation_name, item_code, rate):
    # Mettre à jour le devis en brouillon
    success, result = update_draft_quotation(quotation_name, item_code, rate)
    if not success:
        return result
        
    quotation = result["quotation"]
    new_amount = result["new_amount"]
    
    # Journaliser et retourner le résultat
    frappe.log_error(
        message=f"Updated Supplier Quotation Item: {quotation_name}, Item: {item_code}, New Rate: {rate}, New Amount: {new_amount}",
        title="Supplier Quotation Update"
    )
    
    return {
        "status": "success",
        "message": _(f"Prix unitaire de l'article {item_code} mis à jour avec succès dans le devis {quotation_name}."),
        "data": {
            "quotation_name": quotation_name,
            "item_code": item_code,
            "new_rate": rate,
            "new_amount": new_amount,
            "grand_total": quotation.grand_total
        },
        "errors": None
    }


def format_amended_response(result, quotation_name, item_code, rate):
    amended_doc = result["amended_doc"]
    new_amount = result["new_amount"]
    
    frappe.log_error(
        message=f"Created amended Supplier Quotation: {amended_doc.name} from {quotation_name}, Item: {item_code}, New Rate: {rate}",
        title="Supplier Quotation Update"
    )
    
    return {
        "status": "success",
        "message": _(f"Nouvelle version du devis créée avec l'article {item_code} mis à jour."),
        "data": {
            "quotation_name": amended_doc.name,
            "item_code": item_code,
            "new_rate": rate,
            "new_amount": new_amount,
            "grand_total": amended_doc.grand_total
        },
        "errors": None
    }


def handle_general_exception(e):
    frappe.db.rollback()
    frappe.log_error(
        message=f"Error updating Supplier Quotation Item: {str(e)}",
        title="Supplier Quotation Update Error"
    )
    return {
        "status": "error",
        "message": _(f"Erreur lors de la mise à jour : {str(e)}"),
        "data": None,
        "errors": str(e)
    }
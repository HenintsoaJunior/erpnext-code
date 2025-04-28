import frappe

def get_all_customers(customer_type=None, email=None):
    try:
        filters = {}
        if customer_type:
            filters["customer_type"] = customer_type
        if email:
            filters["email_id"] = email
            
        customers_data = frappe.get_all(
            "Customer",
            filters=filters,
            fields=["name", "email_id", "owner", "customer_name", "customer_type"],
            order_by="creation desc"
        )
        
        return {
            "status": "success",
            "data": {
                "customers": customers_data,
                "count": len(customers_data)
            },
            "message": "Données clients filtrées récupérées avec succès.",
            "errors": None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des données: {str(e)}",
            "data": None,
            "errors": str(e)
        }
    
def import_customers_from_import2():
    try:
        import_data = frappe.get_all(
            "Import2",
            fields=["customer_name", "customer_type"]
        )

        if not import_data:
            return {
                "status": "success",
                "message": "Aucune donnée trouvée dans Import2.",
                "data": {"imported": 0},
                "errors": None
            }

        # Étape 2 : Insertion dans Customer
        inserted_count = 0
        for entry in import_data:
            try:
                # Créer un nouveau client
                customer = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": entry["customer_name"],
                    "customer_type": entry["customer_type"]
                })
                customer.insert(ignore_permissions=True)
                inserted_count += 1
            except Exception as insert_error:
                frappe.log_error(str(insert_error), "Erreur d'insertion Client")

        return {
            "status": "success",
            "message": f"{inserted_count} clients importés avec succès depuis Import2.",
            "data": {"imported": inserted_count},
            "errors": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur pendant l'importation : {str(e)}",
            "data": None,
            "errors": str(e)
        }
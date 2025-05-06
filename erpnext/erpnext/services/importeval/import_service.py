import frappe
from frappe import _
from erpnext.services.buying.buying_service import create_new_item, create_material_request,create_new_supplier,create_request_for_quotation
from erpnext.stock.doctype.warehouse.test_warehouse import create_warehouse_custom
from erpnext.utils.country.CountryAlias import CountryAlias
from erpnext.utils.item.ItemGroupAlias import ItemGroupAlias




def fichier3_data_to_request_for_quotation():
    try:
        fichier3_list = frappe.get_all("Fichier3", fields=["ref_request_quotation", "supplier"])

        if not fichier3_list:
            return {
                "status": "error",
                "message": "Aucun document Fichier3 trouvé.",
                "data": None
            }

        results = []
        for fichier3 in fichier3_list:
            if not fichier3.ref_request_quotation or not fichier3.supplier:
                results.append({
                    "status": "error",
                    "message": f"Les champs ref_request_quotation et supplier doivent être remplis pour {fichier3.name}.",
                    "data": None
                })
                continue

            material_request_name = fichier3.ref_request_quotation
            suppliers = [fichier3.supplier]  # Convertir en liste pour compatibilité
            message_for_supplier = "Merci de nous faire parvenir votre meilleure offre de prix."

            result = create_request_for_quotation(material_request_name, suppliers, message_for_supplier)
            results.append({
                "result": result
            })

        return {
            "status": "success",
            "message": "Traitement des données de Fichier3 terminé.",
            "data": results
        }

    except Exception as e:
        frappe.log_error(str(e), "Erreur fichier3_data_to_request_for_quotation")
        return {
            "status": "error",
            "message": f"Erreur lors du traitement des données de Fichier3: {str(e)}",
            "data": None
        }
    

def fichier1_data_to_material_request():
    company = "IT UNIVERSITY"
    fields = [
        "item_name",
        "ref",
        "quantity",
        "required_by",
        "purpose",
        "target_warehouse"
    ]
    
    try:
        data = frappe.get_list(
            "Fichier1",
            fields=fields,
            distinct=True,
            as_list=False
        )
    except Exception as e:
        frappe.log_error(f"Erreur lors de la récupération des données de Fichier1: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des données: {str(e)}",
            "created_requests": [],
            "errors": []
        }

    created_requests = []
    errors = []

    for row in data:
        ref = row.get("ref")
        item_code = row.get("item_name")
        item_name = row.get("item_name")
        quantity = row.get("quantity") or 1
        schedule_date = row.get("required_by") or frappe.utils.today()
        material_request_type = row.get("purpose") or "Purchase"
        abbr = frappe.get_value("Company", company, "abbr")
        warehouse_name = row.get("target_warehouse") or "All Warehouse"
        set_warehouse = f"{warehouse_name} - {abbr}"

        if not item_code:
            errors.append("Code d'article vide ou non défini, ignoré.")
            continue

        if not frappe.db.exists("Item", {"item_code": item_code}):
            errors.append(f"Article {item_code} n'existe pas, ignoré.")
            continue

        if not isinstance(quantity, (int, float)) or quantity <= 0:
            errors.append(f"Quantité invalide pour l'article {item_code}, ignoré.")
            continue

        # Vérifier l'existence de l'entrepôt
        if not frappe.db.exists("Warehouse", set_warehouse):
            errors.append(f"Entrepôt {set_warehouse} n'existe pas, ignoré.")
            continue

        items = [{
            "item_code": item_code,
            "item_name": item_name,
            "qty": quantity,
            "uom": "Nos",
            "schedule_date": schedule_date
        }]

        try:
            result = create_material_request(
                ref=ref,
                material_request_type=material_request_type,
                company=company,
                schedule_date=schedule_date,
                items=items,
                customer=None,
                set_warehouse=set_warehouse
            )

            if result.get("status") == "success":
                created_requests.append(result.get("data"))
            else:
                errors.append(result.get("message", f"Échec de la création de la demande pour {item_code}"))
        except Exception as e:
            errors.append(f"Erreur lors de la création de la demande pour l'article {item_code}: {str(e)}")

    return {
        "status": "success" if created_requests else "partial" if errors else "error",
        "message": _("Opération terminée."),
        "created_requests": created_requests,
        "errors": errors
    }

def fichier1_data_to_item():
    company = "IT UNIVERSITY"
    fields = [
        "item_name",
        "item_groupe",
        "target_warehouse"
    ]
    
    try:
        data = frappe.get_list(
            "Fichier1",
            fields=fields,
            distinct=True,
            as_list=False
        )
    except Exception as e:
        frappe.log_error(f"Erreur lors de la récupération des données de Fichier1: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des données: {str(e)}",
            "created_items": [],
            "errors": []
        }

    # Initialiser les résultats
    created_items = []
    errors = []

    # Parcourir les items distincts
    for row in data:
        item_code = row.get("item_name")
        item_name = row.get("item_name")
        item_group = ItemGroupAlias.get_item_group(row.get("item_groupe"))
        if not item_group or not frappe.db.exists("Item Group", item_group):
            item_group = "All Item Groups"

        abbr = frappe.get_value("Company", company, "abbr")
        warehouse_name = row.get("target_warehouse") or "All Warehouse"
        warehouse = f"{warehouse_name} - {abbr}"

        if frappe.db.exists("Item", {"item_code": item_code}):
            errors.append(f"Item {item_code} existe déjà, ignoré.")
            continue

        try:
            result = create_new_item(
                item_code=item_code,
                item_name=item_name,
                is_stock_item=1,
                valuation_rate=0,
                stock_uom="Nos",
                warehouse=warehouse,
                company=company,
                item_group=item_group
            )

            if result["status"] == "success":
                created_items.append(result["data"])
            else:
                errors.append(result["message"])
        except Exception as e:
            errors.append(f"Erreur lors de la création de l'item {item_code}: {str(e)}")

    return {
        "status": "success" if created_items else "partial" if errors else "error",
        "message": _("Opération terminée."),
        "created_items": created_items,
        "errors": errors
    }

def fichier2_data_to_supplier():
    company = "IT UNIVERSITY"
    try:
        fichier2_list = frappe.get_all("Fichier2", fields=["supplier_name", "country", "type"])
        
        if not fichier2_list:
            return {
                "status": "warning",
                "message": "Aucun document Fichier2 trouvé.",
                "data": []
            }
        
        results = []
        
        for fichier2 in fichier2_list:
            if not fichier2.supplier_name:
                results.append({
                    "status": "error",
                    "message": f"Le champ supplier_name est requis pour le document Fichier2.",
                    "data": None
                })
                continue
            
            supplier_name = fichier2.supplier_name
            supplier_type = fichier2.type if fichier2.type else "Company"
            supplier_group = "Services"
            
            default_currency = "EUR"
            # if fichier2.country:
            #     country_name = CountryAlias.get_country_name(fichier2.country)
            #     try:
            #         currency_mapping = frappe.get_all(
            #             'Country Currency',
            #             filters={'country': country_name},
            #             fields=['currency'],
            #             limit=1
            #         )
            #         if currency_mapping:
            #             default_currency = currency_mapping[0].currency
            #         else:
            #             frappe.log_error(
            #                 f"Aucune devise définie pour le pays {country_name} dans Fichier2",
            #                 "Erreur fichier2_data_to_supplier"
            #             )
            #     except frappe.DoesNotExistError:
            #         frappe.log_error(
            #             f"Pays {country_name} introuvable pour Fichier2",
            #             "Erreur fichier2_data_to_supplier"
            #         )
            
            result = create_new_supplier(
                supplier_name=supplier_name,
                default_currency=default_currency,
                supplier_type=supplier_type,
                supplier_group=supplier_group
            )
            
            abbr = frappe.get_value("Company", company, "abbr")
            currency = f"{default_currency} - {abbr}"

            insert_party_account("IT UNIVERSITY",currency,supplier_name,"accounts","Supplier")
            results.append({
                "result": result
            })
        
        if all(r["result"]["status"] == "success" for r in results):
            overall_status = "success"
            overall_message = "Tous les fournisseurs ont été créés avec succès."
        elif any(r["result"]["status"] == "success" for r in results):
            overall_status = "partial_success"
            overall_message = "Certains fournisseurs ont été créés, mais des erreurs sont survenues."
        else:
            overall_status = "error"
            overall_message = "Aucun fournisseur n'a été créé en raison d'erreurs."
        
        return {
            "status": overall_status,
            "message": overall_message,
            "data": results
        }
    
    except Exception as e:
        frappe.log_error(str(e), "Erreur dans fichier2_data_to_supplier")
        return {
            "status": "error",
            "message": f"Erreur lors du traitement des documents Fichier2: {str(e)}",
            "data": []
        }




def insert_party_account(company, account, parent, parentfield, parenttype, advance_account=None):
    # Validation des champs obligatoires
    if not company:
        frappe.throw(_("Le champ 'company' est obligatoire."))
    if not account:
        frappe.throw(_("Le champ 'account' est obligatoire."))
    if not parent:
        frappe.throw(_("Le champ 'parent' est obligatoire."))
    if not parentfield:
        frappe.throw(_("Le champ 'parentfield' est obligatoire."))
    if not parenttype:
        frappe.throw(_("Le champ 'parenttype' est obligatoire."))

    if not frappe.db.exists("Company", company):
        frappe.throw(_("L'entreprise {0} n'existe pas.").format(company))
    if not frappe.db.exists("Account", account):
        frappe.throw(_("Le compte {0} n'existe pas.").format(account))

    party_account = frappe.get_doc({
        "doctype": "Party Account",
        "company": company,
        "account": account,
        "advance_account": advance_account,
        "parent": parent,
        "parentfield": parentfield,
        "parenttype": parenttype
    })

    party_account.insert()

    frappe.msgprint(_("Party Account {0} created and submitted").format(party_account.name))

    return {
        "name": party_account.name,
        "company": party_account.company,
        "account": party_account.account,
        "parent": party_account.parent,
        "parentfield": party_account.parentfield,
        "parenttype": party_account.parenttype,
        "advance_account": party_account.advance_account
    }
        
def fichier1_data_to_warehouse():
    fields = [
        "target_warehouse"
    ]
    
    try:
        data = frappe.get_list(
            "Fichier1",
            fields=fields,
            distinct=True,
            as_list=False
        )
    except Exception as e:
        frappe.log_error(f"Erreur lors de la récupération des données de Fichier1: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des données: {str(e)}",
            "created_warehouses": [],
            "errors": []
        }

    # Initialiser les résultats
    created_warehouses = []
    errors = []

    # Parcourir les entrepôts distincts
    for row in data:
        warehouse_name = row.get("target_warehouse")

        # Validation
        if not warehouse_name:
            errors.append("Nom d'entrepôt vide ou non défini, ignoré.")
            continue

        if frappe.db.exists("Warehouse", warehouse_name):
            errors.append(f"Entrepôt {warehouse_name} existe déjà, ignoré.")
            continue

        try:
            warehouse = create_warehouse_custom(
                warehouse_name=warehouse_name,
                properties=None,
                company="IT UNIVERSITY"
            )
            created_warehouses.append(warehouse)
        except Exception as e:
            errors.append(f"Erreur lors de la création de l'entrepôt {warehouse_name}: {str(e)}")

    return {
        "status": "success" if created_warehouses else "partial" if errors else "error",
        "message": _("Opération terminée."),
        "created_warehouses": created_warehouses,
        "errors": errors
    }

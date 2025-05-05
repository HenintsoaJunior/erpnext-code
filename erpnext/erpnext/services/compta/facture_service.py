import frappe
from frappe import _
import json
import requests
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from datetime import date, datetime

# Custom JSON encoder to handle date and datetime objects
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def get_purchase_invoices():
    try:
        # Récupérer le paramètre 'supplier' depuis l'URL
        supplier = frappe.form_dict.get("supplier")
        
        # Définir les filtres
        filters = {}
        if supplier:
            filters["supplier"] = supplier

        # Récupérer les factures d'achat
        invoices_data = frappe.get_all(
            "Purchase Invoice",
            filters=filters,
            fields=[
                "name",
                "status",
                "supplier",
                "posting_date",
                "grand_total",
                "outstanding_amount",
                "currency"
            ],
            order_by="posting_date desc"
        )

        # Pour chaque facture, récupérer les détails des articles
        for invoice in invoices_data:
            invoice_items = frappe.get_all(
                "Purchase Invoice Item",
                filters={"parent": invoice.name},
                fields=[
                    "item_code",
                    "item_name",
                    "qty",
                    "rate",
                    "amount",
                    "purchase_order",
                    "purchase_receipt"
                ]
            )
            invoice["items"] = invoice_items
            invoice["item_count"] = len(invoice_items)

        # Retourner une réponse structurée
        return {
            "status": "success",
            "data": {
                "invoices": invoices_data,
                "count": len(invoices_data)
            },
            "message": "Données des factures d'achat avec détails des articles récupérées avec succès.",
            "errors": None
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la récupération des factures: {str(e)}",
            "data": None,
            "errors": str(e)
        }

def create_payment_entry(invoice_name, paid_amount=None):
    frappe.flags.in_transaction = True
    frappe.flags.ignore_account_permission = True
    try:
        invoice = frappe.get_doc("Purchase Invoice", invoice_name)
        
        # Vérifier si la facture est déjà entièrement payée
        if invoice.outstanding_amount <= 0:
            return {
                "status": "error",
                "message": "La facture est déjà entièrement payée.",
                "data": None,
                "errors": None
            }

        # Générer l'entrée de paiement
        payment_entry_dict = frappe.get_doc(
            get_payment_entry(dt="Purchase Invoice", dn=invoice_name)
        )

        # Si un montant partiel est spécifié, ajuster le paiement
        if paid_amount:
            paid_amount = float(paid_amount)
            if paid_amount <= 0:
                return {
                    "status": "error",
                    "message": "Le montant du paiement doit être supérieur à 0.",
                    "data": None,
                    "errors": None
                }
            if paid_amount > invoice.outstanding_amount:
                return {
                    "status": "error",
                    "message": f"Le montant du paiement ({paid_amount} {invoice.currency}) dépasse le montant restant dû ({invoice.outstanding_amount} {invoice.currency}).",
                    "data": None,
                    "errors": None
                }
            # Ajuster les montants dans l'entrée de paiement
            payment_entry_dict.paid_amount = paid_amount
            for reference in payment_entry_dict.references:
                if reference.reference_name == invoice_name:
                    reference.allocated_amount = paid_amount

        # Ajout des informations de référence
        payment_entry_dict.reference_no = f"REF-{invoice_name}-{frappe.utils.nowdate()}"
        payment_entry_dict.reference_date = frappe.utils.nowdate()

        # Insérer et soumettre
        payment_entry_dict.flags.ignore_permissions = True
        payment_entry_dict.insert(ignore_permissions=True)
        payment_entry_dict.submit()
        frappe.db.commit()

        return {
            "status": "success",
            "data": {
                "payment_entry_name": payment_entry_dict.name,
                "invoice_name": invoice_name,
                "amount_paid": payment_entry_dict.paid_amount,
                "paid_from": payment_entry_dict.paid_from,
                "paid_to": payment_entry_dict.paid_to,
                "payment_date": payment_entry_dict.posting_date,
                "mode_of_payment": payment_entry_dict.mode_of_payment
            },
            "message": f"Paiement de {payment_entry_dict.paid_amount} {invoice.currency} créé et soumis avec succès pour la facture {invoice_name}.",
            "errors": None
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Erreur lors de la création du paiement: {str(e)}", "Payment Error")
        return {
            "status": "error",
            "message": f"Erreur lors de la création du paiement: {str(e)}",
            "data": None,
            "errors": str(e)
        }
    finally:
        frappe.flags.in_transaction = False
        frappe.flags.ignore_account_permission = False
import frappe

class CountryAlias:
    @staticmethod
    def get_country_name(country_alias):
        country_name = frappe.db.get_value('CountryAlias', {'alias': country_alias.strip()}, 'country')
        
        if country_name:
            return country_name
        else:
            # Retourne l'alias si aucun pays n'est trouvé
            return country_alias.strip()
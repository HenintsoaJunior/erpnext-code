import frappe

class ItemGroupAlias:
    @staticmethod
    def get_item_group(item_alias):
        item_group = frappe.db.get_value("ItemGroupAlias",{"item_group_alias": item_alias},"item_group")

        if item_group:
            return item_group
        else:
            return item_alias
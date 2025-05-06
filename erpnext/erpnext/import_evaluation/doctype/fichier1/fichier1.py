# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Fichier1(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		date: DF.Date | None
		item_groupe: DF.Data | None
		item_name: DF.Data | None
		purpose: DF.Data | None
		quantity: DF.Int
		ref: DF.Data | None
		required_by: DF.Date | None
		target_warehouse: DF.Data | None
	# end: auto-generated types

	pass

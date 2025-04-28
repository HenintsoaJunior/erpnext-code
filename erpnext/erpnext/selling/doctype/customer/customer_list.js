frappe.listview_settings["Customer"] = {
	add_fields: ["customer_name", "territory", "customer_group", "customer_type", "image"],

	get_indicator: function(doc) {
		if (doc.customer_type === "Company") {
			return [__("Company"), "blue", "customer_type,=,Company"];
		} else {
			return [__("Individual"), "green", "customer_type,=,Individual"];
		}
	}
};

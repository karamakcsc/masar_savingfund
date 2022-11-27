// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Total Right"] = {
		"filters": [
								// {
								// 	"fieldname": "employee",
								// 	"label": __("Employee"),
								// 	"fieldtype": "Link",
								// 	"options": "Employee",
								// 	"width": 100,
								// 	"reqd": 0,
								// },
								 {
									"fieldname": "date_to",
									"label": __("To Date"),
									"fieldtype": "Date",
									"width": 80,
									"reqd": 1,
									"default": frappe.datetime.get_today()
								}
	]
};

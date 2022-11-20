// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Total Rights"] = {
	"filters": [
							{
								"fieldname": "emp",
								"label": __("Employee Name"),
								"fieldtype": "Link",
								"options": "Employee",
								"width": 100,
								"reqd": 0,
							},
							{
								"fieldname": "from",
								"label": __("From Date"),
								"fieldtype": "Date",
								"width": 80,
								"reqd": 1,
								"default": dateutil.year_start()
							 },
							 {
								"fieldname": "to",
								"label": __("To Date"),
								"fieldtype": "Date",
								"width": 80,
								"reqd": 1,
								"default": dateutil.year_end()
							}
						  // {
							// 	"fieldname": "customer_name",
							// 	"label": __("Customer Name"),
							// 	"fieldtype": "Link",
							// 	"options": "Customer",
							// 	"width": 100,
							// 	"reqd": 0,
							// },
							// {
							// 	"fieldname": "item_group",
							// 	"label": __("Item Group"),
							// 	"fieldtype": "Link",
							// 	"options": "Item Group",
							// 	"width": 100,
							// 	"reqd": 0,
							// }
	]
};

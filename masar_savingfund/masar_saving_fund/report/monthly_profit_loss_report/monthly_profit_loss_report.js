// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Profit Loss Report"] = {
		"filters": [
							  {
									"fieldname": "from",
									"label": __("From Date"),
									"fieldtype": "Date",
									"width": 80,
									"reqd": 1,
									"default": frappe.datetime.year_start()
								 },
								 {
									"fieldname": "to",
									"label": __("To Date"),
									"fieldtype": "Date",
									"width": 80,
									"reqd": 1,
									"default": frappe.datetime.year_end()
								},
								{
									"fieldname": "employee_no",
									"label": __("Employee Number"),
									"fieldtype": "Link",
									"options": "Employee",
									"width": 100,
									"reqd": 0,
								}
	]
};

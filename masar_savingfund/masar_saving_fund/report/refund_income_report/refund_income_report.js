// Copyright (c) 2024, Karama kcsc and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Refund Income Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": __("Employee Number"),
			"fieldtype": "Link",
			"options": "Employee"
		},

		{
			"fieldname": "employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Data",
		},

		{
			"fieldname": "_from",
			"label": __("From Joining Date"),
			"fieldtype": "Date",
		},

		{
			"fieldname": "to",
			"label": __("To Joining Date"),
			"fieldtype": "Date",
		}
	]
};
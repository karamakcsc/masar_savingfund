// Copyright (c) 2023, Karama kcsc and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Total Right for Period"] = {
	"filters": [
		{
			"fieldname": "from",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": 80,
			"reqd": 1,
			"default": dateutil.year_start()
		 }
		// {
		// 	"fieldname": "to",
		// 	"label": __("To Date"),
		// 	"fieldtype": "Date",
		// 	"width": 80,
		// 	"reqd": 1,
		// 	"default":  dateutil.year_end()
		// }

]
};

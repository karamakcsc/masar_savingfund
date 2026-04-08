// Copyright (c) 2026, Karama kcsc and contributors
// For license information, please see license.txt

frappe.query_reports["Saving Fund Differences"] = {
	filters: [
		{
			fieldname: "report_type",
			label: __("Report Type"),
			fieldtype: "Select",
			options: "\nEmployee Contribution\nIncome Allocation\nBoth",
			default: "Both",
			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee"
		},
		{
			fieldname: "show_all",
			label: __("Show All Records (Including Zero Diff)"),
			fieldtype: "Check",
			default: 0
		}
	]
};

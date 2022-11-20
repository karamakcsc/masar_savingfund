// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Contribution', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on("Employee Contribution Line", "employee_contr", function(frm, cdt, cdn) {
		  var d = locals[cdt][cdn];
         d.total_contr = flt(d.employee_contr + d.bank_contr)
         cur_frm.refresh_field();
});

frappe.ui.form.on("Employee Contribution Line", "bank_contr", function(frm, cdt, cdn) {
		  var d = locals[cdt][cdn];
         d.total_contr = flt(d.employee_contr + d.bank_contr)
         cur_frm.refresh_field();
});

frappe.ui.form.on("Employee Contribution Line", "employee_contr", function(frm, cdt, cdn) {

   var contr_lines = frm.doc.employee_contr_lines;
   var total = 0
   for(var i in contr_lines) {
	total = total + contr_lines[i].employee_contr
	}

	frm.set_value("total_employee_contr",total)

});


frappe.ui.form.on("Employee Contribution Line", "bank_contr", function(frm, cdt, cdn) {

   var contr_lines = frm.doc.employee_contr_lines;
   var total = 0
   for(var i in contr_lines) {
	total = total + contr_lines[i].bank_contr
	}

	frm.set_value("total_bank_contr",total)

});

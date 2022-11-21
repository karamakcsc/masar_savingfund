// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Contribution', {
	validate: function(frm) {
		//Get the employees listed in the form
		var selected_employees = new Array();
		for (let e = 0; e < frm.doc.employee_contr_lines.length; e++) {
				selected_employees.push(frm.doc.employee_contr_lines[e].employee);
			}

			frappe.call({
	        method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_exist_employee_in_month",
	        args: {
	          selected_employees: selected_employees,
	          date_to: frm.doc.date_transaction
	        },
	        callback: function(r) {
	          let vr_employees = frm.doc.employee_contr_lines;
	          $.each(r.message, function(i, d) {
	            for (let e = 0; e < vr_employees.length; e++) {
	              if (vr_employees[e].employee == d.employee){
									msgprint('(' + d.employee +' '+ d.employee_name + ') is already exist in another voucher for this month');
									validated = false;
		               }
	            }
	          });
	        }
	    });
	}
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

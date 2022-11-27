// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Saving Fund Payment', {
	// refresh: function(frm) {

	// }
});


frappe.ui.form.on('Saving Fund Payment', {
	employee: function(frm) {
    //Get the employees listed in the form
    var selected_employees = new Array();
    selected_employees.push(frm.doc.employee);

    frappe.call({
        method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
        args: {
          selected_employees: selected_employees,
          date_to: frm.doc.resignation_date
        },
        callback: function(r) {
              $.each(r.message, function(i, d) {
                frm.set_value('employee_contr', d.total_employee_contr);
                frm.set_value('bank_contr', d.total_bank_contr);
                frm.set_value('pl_employee_contr', d.total_employee_pl);
                frm.set_value('pl_bank_contr', d.total_bank_pl);
                frm.set_value('total_right', d.total_right);
                frm.set_value('deserved_amount', d.deserved_amount);
          });
        }
    });
	}
});

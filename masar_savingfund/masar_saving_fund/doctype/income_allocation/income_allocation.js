// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Income Allocation', {
    refresh: function(frm) {
      //$('input[data-fieldname="income"]').css("color","red")
      var child = locals[cdt][cdn];
      frm.doc.employees.forEach(function(child){
            $('div[data-fieldname="employees"]').find(format('.grid-static-col[data-fieldname="total_right"]')).css('background','blue')

      });
	 }
});


frappe.ui.form.on('Income Allocation', {
  validate: function(frm) {

    //Get the employees listed in the form
    var selected_employees = new Array();
    for (let e = 0; e < frm.doc.employees.length; e++) {
        selected_employees.push(frm.doc.employees[e].employee);
      }

    //subtract 1 month from date to get the Pl for previous month
    // let date_prev= new Date(frm.doc.date);
    // date_prev = date_prev.toLocaleDateString("en-US");
    // var m = date_prev.getMonth();
    // frappe.msgprint(date_prev)
    // if(m==0)m=11;
    // else m--;
    // date_prev.setMonth(m);

    frappe.call({
        method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
        args: {
          selected_employees: selected_employees,
          date_to: frm.doc.date
        },
        callback: function(r) {
          let vr_employees = frm.doc.employees;
          $.each(r.message, function(i, d) {
            for (let e = 0; e < vr_employees.length; e++) {
              if (vr_employees[e].employee == d.employee){
                 vr_employees[e].employee_contr = d.total_employee_contr;
                 vr_employees[e].bank_contr = d.total_bank_contr;
                 vr_employees[e].pl_employee_contr_prev = d.total_employee_pl; // siam
                 vr_employees[e].pl_bank_contr_prev = d.total_bank_pl; // siam
                 vr_employees[e].total_right = d.total_right; // yasser


               }
            }
            refresh_field("employees");
          });
        }
    });
  }
});


frappe.ui.form.on("Income Allocation Line","employee", function(frm, cdt, cdn) {
    var e = locals[cdt][cdn];
    //Get the employees listed in the form
    var selected_employees = new Array();
    selected_employees.push(e.employee);

    frappe.call({
        method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
        args: {
          selected_employees: selected_employees,
          date_to: frm.doc.date
        },
        callback: function(r) {
              $.each(r.message, function(i, d) {
                 e.employee_contr = d.total_employee_contr;
                 e.bank_contr = d.total_bank_contr;
                 e.pl_employee_contr_prev = d.total_employee_pl; // siam
                 e.pl_bank_contr_prev = d.total_bank_pl; // siam
                 e.total_right = d.total_right; // yasser
            refresh_field("employees");
          });
        }
    });
  });

////Siam ///////////////////////
frappe.ui.form.on("Income Allocation Line", "pl_employee_contr", function(frm, cdt, cdn) {
		  var d = locals[cdt][cdn];
         d.pl_total = flt(d.pl_employee_contr + d.pl_bank_contr)
         cur_frm.refresh_field();
});
frappe.ui.form.on("Income Allocation Line", "pl_bank_contr", function(frm, cdt, cdn) {
		  var d = locals[cdt][cdn];
         d.pl_total = flt(d.pl_employee_contr + d.pl_bank_contr)
         cur_frm.refresh_field();
});
////// Siam //////////////////////


frappe.ui.form.on("Income Allocation", "employees", function(frm, cdt, cdn) {
  frm.get_field("employees").grid.set_multiple_add("employee");
});

// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Income Allocation', {
//     refresh: function(frm) {
//         $('[data-fieldname="income"]').css('color','red');
//  $('[data-fieldname="total_right"]').css('color','red');
//         $('[data-fieldname="total_right"]').css('background','#f5f5f5');
//     }
// });

frappe.ui.form.on('Income Allocation', {
    refresh: function(frm) {
        if (!frm._color_rows) {
            frm._color_rows = 1;
            $('[data-fieldname="income"]').addClass('text-danger');
            $('div[data-fieldname="total_right"]').each(function(i, row) {
                if (i > 0)$(row).addClass('text-danger');
            });
        }
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
          var sum_total_rights=0;
          var sum_total_pl_emp=0;
          var sum_total_pl=0;
          var sum_total_pl_bank=0;
          var x=0.0;


          let vr_employees = frm.doc.employees;
          $.each(r.message, function(i, d) {
            for (let e = 0; e < vr_employees.length; e++) {
              if (vr_employees[e].employee == d.employee){
                 vr_employees[e].employee_contr = d.total_employee_contr;
                 vr_employees[e].bank_contr = d.total_bank_contr;
                 // frappe.msgprint(d.total_employee_pl.toString());
                 vr_employees[e].pl_employee_contr_prev = d.total_employee_pl;
                 vr_employees[e].pl_bank_contr_prev = d.total_bank_pl;
                 vr_employees[e].total_right = d.total_right; // yasser

                 sum_total_rights+=d.total_right;

               }
            }
            // refresh_field("employees");
          });
          $.each(r.message, function(i, d) {
            for (let e = 0; e < vr_employees.length; e++) {
              if (vr_employees[e].employee == d.employee){

                var total_pl=(d.total_right/sum_total_rights)*frm.doc.income;
                vr_employees[e].pl_total=total_pl;
                sum_total_pl+=total_pl;
                vr_employees[e].pl_employee_contr=(1/3.0)*total_pl;
                sum_total_pl_emp+=(1/3.0)*total_pl;
                vr_employees[e].pl_bank_contr=(2/3.0)*total_pl;
                sum_total_pl_bank+=(2/3.0)*total_pl;

              }

            }

      });
      frm.doc.total_employee_contr = sum_total_pl_emp.toFixed(3);
      frm.doc.total_bank_contr = sum_total_pl_bank.toFixed(3);
      frm.doc.total_pl = sum_total_pl.toFixed(3);

      refresh_field("employees");
      refresh_field("total_employee_contr");
      refresh_field("total_bank_contr");
      refresh_field("total_pl");

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
                 e.pl_employee_contr_prev =d.total_employee_pl;
                 e.pl_bank_contr_prev = d.total_bank_pl
                 e.total_right = d.total_right; // yasser
          });
          refresh_field("employees");

        }
    });
  });

////Add Multiple button /////Siam//////Start Code//
frappe.ui.form.on('Income Allocation', {
    refresh: function(frm) {
        if (!frm._add_multiple) {
            frm._add_multiple = 1;
            var grid = frm.get_field('employees').grid;
            var link_field = frappe.meta.get_docfield(grid.df.options, 'employee');
    		var btn = $(grid.wrapper).find('.grid-add-multiple-rows');
    		btn.removeClass('hidden').toggle(true);
    		btn.on('click', function() {
    			new frappe.ui.form.LinkSelector({
    				doctype: link_field.options,
    				fieldname: 'employee',
    				qty_fieldname: '',
    				get_query: link_field.get_query,
    				target: grid,
    				txt: ''
    			});
    			grid.grid_pagination.go_to_last_page_to_add_row();
    			return false;
    		});
        }
    }
});

////Add Multiple button /////Siam//////END Code//

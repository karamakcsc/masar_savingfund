// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Income Allocation', {
//     refresh: function(frm) {
//         $('[data-fieldname="income"]').css('color','red');
//  $('[data-fieldname="total_right"]').css('color','red');
//         $('[data-fieldname="total_right"]').css('background','#f5f5f5');
//     }
// });


//Get Default Accounts
frappe.ui.form.on('Income Allocation', {
	onload: function(frm) {
    if (frm.doc.docstatus!= 1) {
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.income_allocation.income_allocation.get_interim_revenue_account",
					callback: function(r) {

						frm.set_value('interim_revenue', r.message);
					}
						});
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.income_allocation.income_allocation.get_current_year_profit_account",
					callback: function(r) {
						frm.set_value('current_year_profit', r.message);
					}
						});

          }
}
});
//end Default Accounts

// Validate if the employee has income line in the same month
frappe.ui.form.on('Income Allocation', {
	validate: function(frm) {
		//Get the employees listed in the form
		var selected_employees = new Array();
		for (let e = 0; e < frm.doc.employees.length; e++) {
				selected_employees.push(frm.doc.employees[e].employee);
			}

			frappe.call({
	        method: "masar_savingfund.masar_saving_fund.doctype.income_allocation.income_allocation.get_exist_income_allocation_in_month",
	        args: {
	          selected_employees: selected_employees,
	          date_to: frm.doc.posting_date
	        },
	        callback: function(r) {
	          let vr_employees = frm.doc.employees;
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

// Make the total right colum color red 
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



// Calculate the employee Balances 
frappe.ui.form.on("Income Allocation Line","employee", function(frm, cdt, cdn) {
    var e = locals[cdt][cdn];
    //Get the employees listed in the form
    var selected_employees = new Array();
    if (e.status == 'Active') {
      selected_employees.push(e.employee);
    }


    frappe.call({
        method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
        args: {
          selected_employees: selected_employees,
          date_to: frm.doc.posting_date
        },
        callback: function(r) {
              $.each(r.message, function(i, d) {
                 e.employee_contr = d.total_employee_contr;
                 e.bank_contr = d.total_bank_contr;
                 e.pl_employee_contr_prev =d.total_employee_pl;
                 e.pl_bank_contr_prev = d.total_bank_pl
                 e.total_right = d.total_right; // yasser
								 e.withdraw_amount = d.total_paid_amount; // Siam
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




// Show General Ledger
frappe.ui.form.on('Income Allocation', {
  refresh: function(frm) {
    frm.events.show_general_ledger(frm);
  }
});

frappe.ui.form.on('Income Allocation', {
show_general_ledger: function(frm) {
  if(frm.doc.docstatus > 0) {
    frm.add_custom_button(__('Show GL Ledger'), function() {
      frappe.route_options = {
        "voucher_no": frm.doc.name,
        "from_date": frm.doc.posting_date,
        "to_date": moment(frm.doc.modified).format('YYYY-MM-DD'),
        "company": frm.doc.company,
        "group_by": "",
        "show_cancelled_entries": frm.doc.docstatus === 2
      };
      frappe.set_route("query-report", "General Ledger");
    }, "fa fa-table");
  }
}
});
// END Show General Ledger




frappe.ui.form.on("Income Allocation", "refresh", function(frm) {
  if (frm.doc.docstatus != 1){
        frm.add_custom_button(__("Re-Calculate Income Allocation"), function() {
          var selected_employees = new Array();
          for (let e = 0; e < frm.doc.employees.length; e++) {
            frm.doc.employees[e].pl_total=0;
            frm.doc.employees[e].pl_employee_contr=0;
            frm.doc.employees[e].pl_bank_contr=0;
            var emp = frm.doc.employees[e];
            if (emp.status == 'Active' || 
                (emp.status == 'Left' && isLastDayOfMonth(emp.resignation_date))) {
                selected_employees.push(emp.employee);
              }
            }

          frappe.call({
              method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
              args: {
                selected_employees: selected_employees,
                date_to: frm.doc.posting_date
              },
              callback: function(r) {
                var sum_total_rights=0;
                var sum_total_pl_emp=0;
                var sum_total_pl=0;
                var sum_total_pl_bank=0;
								var sum_withdraw_amount=0;
                var x=0.0;


                let vr_employees = frm.doc.employees;
                $.each(r.message, function(i, d) {
                  for (let e = 0; e < vr_employees.length; e++) {
                    if (vr_employees[e].employee == d.employee){
											// frappe.msgprint(d.total_paid_amount.toString())
                       vr_employees[e].employee_contr = d.total_employee_contr;
                       vr_employees[e].bank_contr = d.total_bank_contr;
                       vr_employees[e].pl_employee_contr_prev = d.total_employee_pl;
                       vr_employees[e].pl_bank_contr_prev = d.total_bank_pl;
                       vr_employees[e].total_right = d.total_right; // yasser
											 vr_employees[e].withdraw_amount = d.total_paid_amount; // Siam
											 sum_withdraw_amount+=d.withdraw_amount;
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
											vr_employees[e].total_paid_amount += d.withdraw_amount;

                    }

                  }

            });
            frm.doc.total_employee_contr = sum_total_pl_emp.toFixed(3);
            frm.doc.total_bank_contr = sum_total_pl_bank.toFixed(3);
            frm.doc.total_pl = sum_total_pl.toFixed(3);
						frm.doc.total_rights = sum_total_rights.toFixed(3);

            refresh_field("employees");
            refresh_field("total_employee_contr");
            refresh_field("total_bank_contr");
            refresh_field("total_pl");
						refresh_field("total_rights");

              }
          });

        });
  }
});


frappe.ui.form.on("Income Allocation", "refresh", function(frm) {

  frm.add_custom_button(__("Get Employees"), function() {
    frappe.call({
      doc:frm.doc,
      method : "fill_employee_details",
    
      callback : function (r) {
        refresh_field("status");
        refresh_field("number_of_employees");
        refresh_field("employees");
      }
    })

  });
});        

function isLastDayOfMonth(dateStr) {
    if (!dateStr) return false;
    var d = new Date(dateStr);
    var lastDay = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate();
    return d.getDate() === lastDay;
}
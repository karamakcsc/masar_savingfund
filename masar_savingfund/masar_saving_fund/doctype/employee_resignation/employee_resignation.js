// Copyright (c) 2023, Karama kcsc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Resignation', {
	employee: function(frm) {
    //Get the employees listed in the form
    var selected_employees = new Array();
    selected_employees.push(frm.doc.employee);

    frappe.call({
        method: "masar_savingfund.custom.employee.employee.get_employee_savefund_balance",
        args: {
          selected_employees: selected_employees,
          date_to: frm.doc.posting_date
        },
        callback: function(r) {
              $.each(r.message, function(i, d) {
                frm.set_value('employee_contr', d.total_employee_contr);
                frm.set_value('bank_contr', d.total_bank_contr);
                frm.set_value('pl_employee_contr', d.total_employee_pl);
                frm.set_value('pl_bank_contr', d.total_bank_pl);
                frm.set_value('total_right', d.total_right);
                frm.set_value('deserved_amount', d.deserved_amount);
                frm.set_value('withdraw_amount', d.total_paid_amount);

          });
        }
    });
		cur_frm.refresh_field();
	}
});


frappe.ui.form.on('Employee Resignation', {
	resignation_date: function(frm) {
		if (frm.doc.docstatus ===0){
	var doc_data = {
			'resignation_date': frm.doc.resignation_date,
			'date_of_joining': frm.doc.date_of_joining,			
			'employee': frm.doc.employee,
			'employee_contr': frm.doc.employee_contr,
			'pl_employee_contr': frm.doc.pl_employee_contr,
			'bank_contr': frm.doc.bank_contr,
			'pl_bank_contr': frm.doc.pl_bank_contr,
			'withdraw_amount': frm.doc.withdraw_amount,
			'total_right': frm.doc.total_right,		
			'deserved_amount': frm.doc.deserved_amount,
			'income_emp_amount': frm.doc.income_emp_amount,
			'income_bank_amount': frm.doc.income_bank_amount,	

		};

    
    frappe.call({
        method: "masar_savingfund.masar_saving_fund.doctype.employee_resignation.employee_resignation.get_employee_equity_balance",
        args: {
			dict_doc: doc_data,
        },
		
        callback: function(r) {
			var d = JSON.parse(r.message);			
                frm.set_value('employee_equity_amount', d.emp_amount);
                frm.set_value('bank_equity_amount', d.bank_amount);
                frm.set_value('income_amount', d.income_amount);
				frm.set_value('income_emp_amount', d.income_emp_amount);
				frm.set_value('income_bank_amount', d.income_bank_amount);	
        }
    });
		cur_frm.refresh_field();
	}
}
});



frappe.ui.form.on('Employee Resignation', {
	onload: function(frm) {
		if (frm.doc.docstatus ===0){
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_resignation.employee_resignation.get_liability_account",
					callback: function(r) {
						frm.set_value('liability_account', r.message);
					}
						});
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_resignation.employee_resignation.get_employee_equity_account",
					callback: function(r) {
						frm.set_value('employee_equity', r.message);
					}
						});

			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_resignation.employee_resignation.get_bank_equity_account",
					callback: function(r) {
						frm.set_value('bank_equity', r.message);
					}
						});

			frappe.call({
				method: "masar_savingfund.masar_saving_fund.doctype.employee_resignation.employee_resignation.get_income_account",
				callback: function(r) {
					frm.set_value('income_account', r.message);
				}
					});

}
	}
});
//s
// Show General Ledger
frappe.ui.form.on('Employee Resignation', {
	refresh: function(frm) {
	  frm.events.show_general_ledger(frm);
	}
  });
  
  
  
  frappe.ui.form.on('Employee Resignation', {
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



  cur_frm.fields_dict['employee'].get_query = function(doc) {
	return {
		filters: {
			"status": "Active"
		}
	}
}


// frappe.ui.form.on('Employee Resignation', {
//     validate: function(frm) {
//         fetch_up_to_date_balance(frm);
//     },
//     employee: function(frm) {
//         fetch_up_to_date_balance(frm);
//     }
// });

// function fetch_up_to_date_balance(frm) {
//     if (!frm.doc.employee || !frm.doc.resignation_date) {
//         frappe.msgprint(__('Please select an Employee and Resignation Date.'));
//         return;
//     }

//     frappe.call({
//         method: "masar_savingfund.custom.employee.employee.get_employee_up_to_date_balance",
//         args: {
//             emp: frm.doc.employee,
//             date_to: frm.doc.resignation_date
//         },
//         callback: function(r) {
//             if (r.message && r.message.length > 0) {
//                 frm.set_value('cont_up_to_date', r.message[0].total_right);
//             } else {
//                 frm.set_value('cont_up_to_date', 0);
//             }
//         }
//     });
// }

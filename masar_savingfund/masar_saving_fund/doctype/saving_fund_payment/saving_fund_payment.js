// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt


//Get Default Accounts
frappe.ui.form.on('Saving Fund Payment', {
	onload: function(frm) {
    if (frm.doc.docstatus != 1){
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_cash_account",
					callback: function(r) {
						frm.set_value('cash_account', r.message);
					}
						});
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_employee_equity_account",
					callback: function(r) {
						frm.set_value('employee_equity', r.message);
					}
						});

			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_bank_equity_account",
					callback: function(r) {
						frm.set_value('bank_equity', r.message);
					}
						});

      frappe.call({
        method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_liability_account",
        callback: function(r) {
          frm.set_value('liability_account', r.message);
        }
          });
      frappe.call({
        method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_earning_revenue",
        callback: function(r) {
          frm.set_value('earning_revenue', r.message);
        }
          });

}
  }
});
//end Default Accounts
frappe.ui.form.on('Saving Fund Payment', {
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
                frm.set_value('paid_amount', d.deserved_amount);
          });
        }
    });
		cur_frm.refresh_field();
	}
});


// frappe.ui.form.on('Saving Fund Payment',  {
//     validate: function(frm) {
//     if(frm.doc.paid_amount > frm.doc.deserved_amount){
//         msgprint('Paid Amount Cannot Be Greater Than Deserved Amount');
//         validated = false;
//      }
//     }
// });

// Show General Ledger ////
frappe.ui.form.on('Saving Fund Payment', {
  refresh: function(frm) {
    frm.events.show_general_ledger(frm);
  }
});



frappe.ui.form.on('Saving Fund Payment', {
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
// END Show General Ledger //



frappe.ui.form.on("Saving Fund Payment", {
  paid_perc: function(frm) {
    paid_amount(frm);
    deserved_amount(frm);
  },
  paid_perc: function(frm) {
      calculate_deserved_amount(frm);
  }
});

var paid_amount = function(frm) {
  var doc = frm.doc;
  frm.set_value("paid_amount", doc.paid_perc * doc.deserved_amount);
};


// frappe.ui.form.on("Saving Fund Payment", "validate", function(frm) {
//   var postingDate = new Date(frm.doc.posting_date);
//   var joiningDate = new Date(frm.doc.date_of_joining);
//   joiningDate.setFullYear(joiningDate.getFullYear() + 10);
  
//   if (frm.doc.status === 'Left' || (frm.doc.status === 'Active' && joiningDate <= postingDate)) {
//     frm.toggle_display("section_break_7", true);
//     frm.toggle_display("total_rights_section", true);
//     frm.toggle_display("section_break_19", true);
//     frm.refresh_field();
//   } else {
//     frm.toggle_display("section_break_7", false);
//     frm.toggle_display("total_rights_section", false);
//     frm.toggle_display("section_break_19", false);
//     frm.refresh_field();
//   }

// });


frappe.ui.form.on('Saving Fund Payment', {
  employee: function(frm) {

    var postingDate = new Date(frm.doc.posting_date);
    var joiningDate = new Date(frm.doc.date_of_joining);
    joiningDate.setFullYear(joiningDate.getFullYear() + 10);
  
    if (frm.doc.status === 'Left' || (frm.doc.status === 'Active' && joiningDate <= postingDate)) {
      frm.toggle_display("section_break_7", true);
      frm.toggle_display("total_rights_section", true);
      frm.toggle_display("section_break_19", true);
      frm.refresh_field();
    } else {
      frm.toggle_display("section_break_7", false);
      frm.toggle_display("total_rights_section", false);
      frm.toggle_display("section_break_19", false);
      frm.refresh_field();
    }
  }
});
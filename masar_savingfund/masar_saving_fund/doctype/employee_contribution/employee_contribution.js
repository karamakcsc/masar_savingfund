// Copyright (c) 2022, Karama kcsc and contributors
// For license information, please see license.txt

//Get Default Accounts
frappe.ui.form.on('Employee Contribution', {
	onload: function(frm) {
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

}
});
//end Default Accounts

//Validate If Employee exist in the same month
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
	          date_to: frm.doc.posting_date
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
//End Validate If Employee exist in the same month

//calculate for employee and bank contr
frappe.ui.form.on("Employee Contribution Line", "basic_salary", function(frm, cdt, cdn) {
		  var d = locals[cdt][cdn];
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_employee_contr_perc",
					callback: function(r) {
						if(d.employee){
							d.employee_contr = flt(d.basic_salary) * flt(r.message) /100;
							//d.total_contr=flt(d.basic_salary)*flt(r.message)/100;
						}
					}
						});
			frappe.call({
					method: "masar_savingfund.masar_saving_fund.doctype.employee_contribution.employee_contribution.get_bank_contr_perc",
					callback: function(z) {
						if(d.employee){
							d.bank_contr = flt(d.basic_salary) * flt(z.message) /100;
							//d.total_contr+=flt(d.basic_salary)*flt(z.message)/100;
						}
					}
						});

        cur_frm.refresh_field(employee_contr_lines);
});
//end calculate for employee and bank contr

frappe.ui.form.on('Employee Contribution', {
	validate: function(frm) {
		for (let e = 0; e < frm.doc.employee_contr_lines.length; e++) {
				frm.doc.employee_contr_lines[e].total_contr = flt(frm.doc.employee_contr_lines[e].employee_contr + frm.doc.employee_contr_lines[e].bank_contr)
				}


}
});

frappe.ui.form.on("Employee Contribution", "validate", function(frm, cdt, cdn) {

   var contr_lines = frm.doc.employee_contr_lines;
   var total = 0
	 for (let i = 0; i < contr_lines.length; i++) {
	total = total + contr_lines[i].employee_contr
	}

	frm.set_value("total_employee_contr",total)

});


frappe.ui.form.on("Employee Contribution", "validate", function(frm, cdt, cdn) {

   var contr_lines = frm.doc.employee_contr_lines;
   var total = 0
	 for (let i = 0; i < contr_lines.length; i++) {
	total = total + contr_lines[i].bank_contr
	}

	frm.set_value("total_bank_contr",total)

});


////Add Multiple button /////Siam//////Start Code//
frappe.ui.form.on('Employee Contribution', {
    refresh: function(frm) {
        if (!frm._add_multiple) {
            frm._add_multiple = 1;
            var grid = frm.get_field('employee_contr_lines').grid;
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

// End Add Multiple button /////Siam//////END Code//

// Show General Ledger
frappe.ui.form.on('Employee Contribution', {
  refresh: function(frm) {
    frm.events.show_general_ledger(frm);
  }
});



frappe.ui.form.on('Employee Contribution', {
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

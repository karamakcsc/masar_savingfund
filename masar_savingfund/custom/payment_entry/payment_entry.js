
  frappe.ui.form.on("Payment Entry","party", function(frm, cdt, cdn) {
      var e = locals[cdt][cdn];
      //Get the employees listed in the form
      var selected_employees = new Array();
      selected_employees.push(e.party);

      frappe.call({
          method: "masar_savingfund.custom.payment_entry.payment_entry.get_employee_total_right",
          args: {
            selected_employees: selected_employees,
            date_to: frm.doc.posting_date
          },
          callback: function(r) {
                $.each(r.message, function(i, d) {
                   frm.doc.total_right=d.total_right;
            });
            refresh_field("total_right");

          }
      });
    });

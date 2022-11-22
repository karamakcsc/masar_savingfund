get_chart_data: function(columns, result) {
	return {
	        frappe.call({
    			method: "erpnext.projects.doctype.project_details.project_details.summary",
    			callback: function(r) {
    	      		data: r.message,

    				type: 'pie', // or 'bar', 'line', 'pie', 'percentage'
        	                        height: 300
    			}
    		});
		}
	}

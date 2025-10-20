// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('SUNAT Payment Method', {
	refresh: function(frm) {
		// Custom functionality
		if (frm.doc.codigo_sunat) {
			frm.set_df_property('codigo_sunat', 'read_only', 1);
		}
	},
	
	codigo_sunat: function(frm) {
		// Validar formato del código SUNAT (3 dígitos)
		if (frm.doc.codigo_sunat && frm.doc.codigo_sunat.length !== 3) {
			frappe.msgprint(__('El código SUNAT debe tener exactamente 3 dígitos'));
			frm.set_value('codigo_sunat', '');
		}
	}
});

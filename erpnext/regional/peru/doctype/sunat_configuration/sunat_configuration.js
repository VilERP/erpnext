// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('SUNAT Configuration', {
	refresh: function(frm) {
		// Agregar botón para probar conexión SUNAT
		if (frm.doc.ruc && frm.doc.usuario_sunat) {
			frm.add_custom_button(__('Probar Conexión SUNAT'), function() {
				frappe.call({
					method: 'erpnext.accounts.doctype.sunat_configuration.sunat_configuration.test_sunat_connection',
					args: {
						'doc': frm.doc
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__('Conexión exitosa con SUNAT'));
						} else {
							frappe.msgprint(__('Error en la conexión con SUNAT'));
						}
					}
				});
			});
		}
	},
	
	ruc: function(frm) {
		// Validar RUC (11 dígitos numéricos)
		if (frm.doc.ruc) {
			if (frm.doc.ruc.length !== 11 || !/^\d+$/.test(frm.doc.ruc)) {
				frappe.msgprint(__('El RUC debe tener exactamente 11 dígitos numéricos'));
				frm.set_value('ruc', '');
			}
		}
	},
	
	company: function(frm) {
		// Auto-llenar datos de la empresa
		if (frm.doc.company) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Company',
					name: frm.doc.company
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('razon_social', r.message.company_name);
					}
				}
			});
		}
	}
});

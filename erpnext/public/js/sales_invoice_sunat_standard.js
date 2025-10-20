frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            if (frm.doc.custom_sunat_doc_state === 'Pendiente') {
                frm.add_custom_button(__('Enviar a SUNAT'), function() {
                    send_to_sunat_standard(frm);
                }, __('SUNAT'));
            }
        }
    }
});

function send_to_sunat_standard(frm) {
    frappe.call({
        method: 'erpnext.accounts.doctype.sales_invoice.sunat_integration.send_to_sunat_api',
        args: {'sales_invoice': frm.doc.name},
        callback: function(r) {
            if (r.message && r.message.success) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('Documento enviado exitosamente a SUNAT'),
                    indicator: 'green'
                });
            }
        }
    });
}

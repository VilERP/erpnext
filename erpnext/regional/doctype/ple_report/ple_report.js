// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('PLE Report', {
    refresh: function(frm) {
        // Botón para generar archivo si el documento está guardado
        if (!frm.doc.__islocal && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Generate PLE File'), function() {
                generate_ple_file(frm);
            });
        }
        
        // Botón para descargar archivo si ya está generado
        if (frm.doc.file_content && frm.doc.status === 'Generated') {
            frm.add_custom_button(__('Download TXT File'), function() {
                download_txt_file(frm);
            });
        }
        
        // Auto-calcular fechas al cambiar año/mes
        if (frm.doc.period_year && frm.doc.period_month) {
            auto_set_dates(frm);
        }
    },
    
    period_year: function(frm) {
        auto_set_dates(frm);
    },
    
    period_month: function(frm) {
        auto_set_dates(frm);
    }
});

function auto_set_dates(frm) {
    if (frm.doc.period_year && frm.doc.period_month) {
        const year = frm.doc.period_year;
        const month = frm.doc.period_month.padStart(2, '0');
        
        // Primer día del mes
        const from_date = `${year}-${month}-01`;
        
        // Último día del mes
        const last_day = new Date(year, parseInt(month), 0).getDate();
        const to_date = `${year}-${month}-${last_day}`;
        
        frm.set_value('from_date', from_date);
        frm.set_value('to_date', to_date);
    }
}

function generate_ple_file(frm) {
    frappe.call({
        method: 'generate_ple_file',
        doc: frm.doc,
        freeze: true,
        freeze_message: __('Generating PLE file...'),
        callback: function(r) {
            if (r.message && r.message.success) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('PLE file generated successfully'),
                    indicator: 'green'
                });
            }
        }
    });
}

function download_txt_file(frm) {
    if (!frm.doc.file_content) {
        frappe.msgprint(__('No file content available'));
        return;
    }
    
    // Crear blob y descargar
    const blob = new Blob([frm.doc.file_content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = frm.doc.file_name || 'ple_report.txt';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    frappe.show_alert({
        message: __('File downloaded'),
        indicator: 'green'
    });
}

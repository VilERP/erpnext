// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Company', {
    refresh: function(frm) {
        // Auto-llenar razón social desde company name
        if (frm.doc.company_name && !frm.doc.custom_sunat_razon_social) {
            frm.set_value('custom_sunat_razon_social', frm.doc.company_name);
        }
    },

    validate: function(frm) {
        // Validar RUC solo al guardar
        if (frm.doc.custom_sunat_ruc) {
            let ruc = frm.doc.custom_sunat_ruc.trim();

            // Validar longitud
            if (ruc.length !== 11) {
                frappe.throw(__('El RUC debe tener exactamente 11 dígitos'));
            }

            // Validar que sean solo números
            if (!/^\d+$/.test(ruc)) {
                frappe.throw(__('El RUC debe contener solo números'));
            }

            // Validar dígito verificador (algoritmo SUNAT)
            if (!validar_ruc_sunat(ruc)) {
                frappe.throw(__('El RUC no es válido según el algoritmo de SUNAT'));
            }
        }

        // Validar Ubigeo solo al guardar
        if (frm.doc.custom_sunat_ubigeo) {
            let ubigeo = frm.doc.custom_sunat_ubigeo.trim();

            if (ubigeo.length !== 6 || !/^\d+$/.test(ubigeo)) {
                frappe.throw(__('El Ubigeo debe tener exactamente 6 dígitos numéricos'));
            }
        }
    }
});

function validar_ruc_sunat(ruc) {
    // Algoritmo de validación de RUC de SUNAT
    let suma = 0;
    let factores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];

    for (let i = 0; i < 10; i++) {
        suma += parseInt(ruc[i]) * factores[i];
    }

    let resto = suma % 11;
    let digito_verificador = 11 - resto;

    if (digito_verificador === 10) digito_verificador = 0;
    if (digito_verificador === 11) digito_verificador = 1;

    return digito_verificador === parseInt(ruc[10]);
}

# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup(company=None, patch=True):
    """Setup para Perú - SUNAT"""
    make_custom_fields()
    load_sunat_master_data()

def make_custom_fields(update=True):
    """Crear campos SUNAT en Sales Invoice y Company"""
    
    custom_fields = {
        "Sales Invoice": [
            dict(
                fieldname="custom_sunat_section",
                label=_("Información SUNAT"),
                fieldtype="Section Break",
                insert_after="project",
                collapsible=1
            ),
            dict(
                fieldname="custom_sunat_doc_type",
                label=_("Tipo de Documento SUNAT"),
                fieldtype="Link",
                options="SUNAT Document Type",
                insert_after="custom_sunat_section",
                in_list_view=1
            ),
            dict(
                fieldname="custom_sunat_doc_state",
                label=_("Estado del Documento"),
                fieldtype="Select",
                options="\nPendiente\nEnviado\nAceptado\nRechazado\nAnulado",
                default="Pendiente",
                insert_after="custom_sunat_doc_type",
                read_only=0,
                allow_on_submit=1
            ),
            dict(
                fieldname="custom_sunat_col_break_1",
                fieldtype="Column Break",
                insert_after="custom_sunat_doc_state"
            ),
            dict(
                fieldname="custom_sunat_payment_method",
                label=_("Método de Pago SUNAT"),
                fieldtype="Link",
                options="SUNAT Payment Method",
                insert_after="custom_sunat_col_break_1"
            ),
            dict(
                fieldname="custom_sunat_transaction_date",
                label=_("Fecha de Transacción SUNAT"),
                fieldtype="Datetime",
                insert_after="custom_sunat_payment_method",
                allow_on_submit=1,
                print_hide=1
            ),
            dict(
                fieldname="custom_sunat_col_break_2",
                fieldtype="Column Break",
                insert_after="custom_sunat_transaction_date"
            ),
            dict(
                fieldname="custom_sunat_hash_code",
                label=_("Código Hash SUNAT"),
                fieldtype="Data",
                insert_after="custom_sunat_col_break_2",
                allow_on_submit=1,
                print_hide=1,
                read_only=1
            ),
            dict(
                fieldname="custom_sunat_qr_code",
                label=_("Código QR SUNAT"),
                fieldtype="Long Text",
                insert_after="custom_sunat_hash_code",
                allow_on_submit=1,
                print_hide=1,
                read_only=1
            ),
        ],
        "Company": [
            dict(
                fieldname="custom_sunat_section",
                label=_("Información SUNAT"),
                fieldtype="Section Break",
                insert_after="company_name",
                collapsible=1
            ),
            dict(
                fieldname="custom_sunat_ruc",
                label=_("RUC"),
                fieldtype="Data",
                insert_after="custom_sunat_section",
                length=11
            ),
            dict(
                fieldname="custom_sunat_razon_social",
                label=_("Razón Social"),
                fieldtype="Data",
                insert_after="custom_sunat_ruc"
            ),
            dict(
                fieldname="custom_sunat_col_break_1",
                fieldtype="Column Break",
                insert_after="custom_sunat_razon_social"
            ),
            dict(
                fieldname="custom_sunat_direccion_fiscal",
                label=_("Dirección Fiscal"),
                fieldtype="Small Text",
                insert_after="custom_sunat_col_break_1"
            ),
            dict(
                fieldname="custom_sunat_ubigeo",
                label=_("Ubigeo"),
                fieldtype="Data",
                insert_after="custom_sunat_direccion_fiscal",
                length=6
            ),
        ]
    }
    
    create_custom_fields(custom_fields, update=update)

def load_sunat_master_data():
    """Cargar datos maestros SUNAT si no existen"""
    
    # Tipos de Documento SUNAT
    if not frappe.db.exists("SUNAT Document Type", {"codigo_sunat": "01"}):
        doc_types = [
            {"codigo_sunat": "01", "nombre_documento": "Factura"},
            {"codigo_sunat": "03", "nombre_documento": "Boleta de Venta"},
            {"codigo_sunat": "07", "nombre_documento": "Nota de Crédito"},
            {"codigo_sunat": "08", "nombre_documento": "Nota de Débito"},
            {"codigo_sunat": "09", "nombre_documento": "Guía de Remisión"},
        ]
        
        for dt in doc_types:
            if not frappe.db.exists("SUNAT Document Type", {"codigo_sunat": dt["codigo_sunat"]}):
                doc = frappe.get_doc({
                    "doctype": "SUNAT Document Type",
                    "codigo_sunat": dt["codigo_sunat"],
                    "nombre_documento": dt["nombre_documento"]
                })
                doc.insert(ignore_permissions=True)
    
    # Métodos de Pago SUNAT
    if not frappe.db.exists("SUNAT Payment Method", {"codigo_sunat": "001"}):
        payment_methods = [
            {"codigo_sunat": "001", "nombre_metodo": "Depósito en cuenta"},
            {"codigo_sunat": "003", "nombre_metodo": "Transferencia de fondos"},
            {"codigo_sunat": "008", "nombre_metodo": "Efectivo"},
        ]
        
        for pm in payment_methods:
            if not frappe.db.exists("SUNAT Payment Method", {"codigo_sunat": pm["codigo_sunat"]}):
                doc = frappe.get_doc({
                    "doctype": "SUNAT Payment Method",
                    "codigo_sunat": pm["codigo_sunat"],
                    "nombre_metodo": pm["nombre_metodo"]
                })
                doc.insert(ignore_permissions=True)
    
    frappe.db.commit()

# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def validate_ruc(ruc):
    """Validar formato de RUC peruano"""
    if not ruc:
        return False
    
    # RUC debe tener 11 dígitos
    if len(ruc) != 11 or not ruc.isdigit():
        return False
    
    return True

def get_sunat_document_type(invoice_type):
    """Obtener código SUNAT según tipo de factura"""
    mapping = {
        "Sales Invoice": "01",  # Factura
        "Sales Return": "07",   # Nota de Crédito
        "Debit Note": "08",     # Nota de Débito
    }
    return mapping.get(invoice_type, "01")

def format_amount_sunat(amount):
    """Formatear monto según SUNAT (12E, 2D)"""
    # Máximo 12 enteros, 2 decimales
    return "{:.2f}".format(float(amount))

def format_date_sunat(date):
    """Formatear fecha según SUNAT (DD/MM/YYYY)"""
    if isinstance(date, str):
        from datetime import datetime
        date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime("%d/%m/%Y")

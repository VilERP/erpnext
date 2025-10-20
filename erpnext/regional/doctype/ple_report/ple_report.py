# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from datetime import datetime
from erpnext.regional.peru.ple.generator import generate_ple_14_1


class PLEReport(Document):
    def validate(self):
        """Validaciones antes de guardar"""
        # Validar que from_date sea menor que to_date
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                frappe.throw(_("From Date cannot be greater than To Date"))
        
        # Auto-generar el nombre del archivo si no existe
        if not self.file_name:
            self.file_name = self.generate_file_name()
    
    def on_submit(self):
        """Generar el archivo PLE al enviar"""
        self.generate_ple_file()
    
    def generate_file_name(self):
        """Generar nombre de archivo según formato SUNAT"""
        # Obtener RUC de la compañía
        company_doc = frappe.get_doc("Company", self.company)
        ruc = company_doc.tax_id or "00000000000"
        
        # Formato: LERRRRRRRRRRRAAAAMMDDLLLLLLCCOIMG.TXT
        # LE: Prefijo
        # RRRRRRRRRR: RUC (11 dígitos)
        # AAAA: Año
        # MM: Mes
        # DD: Día (00 para todo el mes)
        # LLLLLL: Libro (140100 para Registro de Ventas)
        # CC: Moneda (01 para PEN)
        # O: Operación (1 para normal)
        # I: Indicador (1 para con información)
        # M: Moneda extranjera (1 si hay)
        # G: Generación (1 para primera vez)
        
        year = str(self.period_year)
        month = str(self.period_month).zfill(2)
        day = "00"
        
        # Código de libro según tipo de reporte
        if self.report_type == "14.1 - Registro de Ventas":
            libro = "140100"
        elif self.report_type == "8.1 - Registro de Compras":
            libro = "080100"
        else:
            libro = "000000"
        
        file_name = f"LE{ruc}{year}{month}{day}{libro}00111.TXT"
        return file_name
    
    @frappe.whitelist()
    def generate_ple_file(self):
        """Generar el contenido del archivo PLE"""
        try:
            if self.report_type == "14.1 - Registro de Ventas":
                content = generate_ple_14_1(
                    company=self.company,
                    from_date=self.from_date,
                    to_date=self.to_date
                )
            else:
                frappe.throw(_("Report type not implemented yet"))
            
            # Guardar contenido
            self.file_content = content
            self.total_records = len(content.split('\n')) - 1  # -1 por línea vacía final
            self.generation_date = datetime.now()
            self.status = "Generated"
            
            # Guardar sin validaciones
            self.db_set('file_content', content)
            self.db_set('total_records', self.total_records)
            self.db_set('generation_date', self.generation_date)
            self.db_set('status', 'Generated')
            
            frappe.msgprint(_("PLE file generated successfully with {0} records").format(self.total_records))
            
            return {
                "success": True,
                "records": self.total_records,
                "file_name": self.file_name
            }
            
        except Exception as e:
            frappe.log_error(f"Error generating PLE file: {str(e)}")
            frappe.throw(_("Error generating PLE file: {0}").format(str(e)))

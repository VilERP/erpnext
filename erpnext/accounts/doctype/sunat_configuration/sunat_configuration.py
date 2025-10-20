# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SUNATConfiguration(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		company: DF.Link
		ruc: DF.Data
		razon_social: DF.Data
		regimen_tributario: DF.Select | None
		direccion_fiscal: DF.SmallText | None
		ubigeo: DF.Data | None
		telefono: DF.Data | None
		email_facturacion: DF.Data | None
		usuario_sunat: DF.Data | None
		password_sunat: DF.Password | None
		certificado_digital: DF.Attach | None
		password_certificado: DF.Password | None
		ambiente_sunat: DF.Select
		url_servicio_sunat: DF.Data | None
		codigo_establecimiento: DF.Data
		activo: DF.Check
	# end: auto-generated types
	
	def validate(self):
		# Validar RUC (11 dígitos)
		if self.ruc and len(self.ruc) != 11:
			frappe.throw("El RUC debe tener exactamente 11 dígitos")
		
		# Validar que solo haya una configuración por empresa
		if self.company:
			existing = frappe.db.exists("SUNAT Configuration", {
				"company": self.company,
				"name": ("!=", self.name)
			})
			if existing:
				frappe.throw(f"Ya existe una configuración SUNAT para la empresa {self.company}")

# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document

class SUNATPaymentMethod(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		codigo_sunat: DF.Data
		nombre_metodo: DF.Data
		descripcion: DF.SmallText | None
		activo: DF.Check
		requiere_numero_operacion: DF.Check
		requiere_fecha_operacion: DF.Check
		permite_fraccionamiento: DF.Check
		dias_credito_maximo: DF.Int | None
	# end: auto-generated types
	pass

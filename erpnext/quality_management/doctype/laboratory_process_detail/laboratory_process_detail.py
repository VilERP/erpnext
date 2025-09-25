# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LaboratoryProcessDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		actual_value: DF.Float
		end_time: DF.Time | None
		expected_value: DF.Float
		observations: DF.Text | None
		parameter: DF.Data
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		process_name: DF.Data
		result: DF.Literal["Aprobado", "Rechazado", "Pendiente"]
		start_time: DF.Time | None
		unit_of_measure: DF.Link | None
	# end: auto-generated types
	pass

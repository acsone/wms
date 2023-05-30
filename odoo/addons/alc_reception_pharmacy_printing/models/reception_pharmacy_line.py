# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.alc_printing_base.utils import hw_print
from odoo.addons.alc_reception_pharmacy.models.reception_pharmacy_line import (
    ReceptionPharmacyLine as ReceptionPharmacyLineBase,
)


class ReceptionPharmacyLine(ReceptionPharmacyLineBase):
    def print_reception_pharmacy_label(self):
        self.ensure_one()
        printer = self.env.user.printing_pharmacy_reception_printer_id
        if not printer:
            raise ValidationError(
                _("No printer defined for reception, please select one first")
            )
        hw_print(
            self,
            "alc_reception_pharmacy_printing.report_pharmacy_lot_label",
            qty=1,
            printer_id=printer.id,
        )

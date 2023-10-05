# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import config

from odoo.addons.alc_reception_pharmacy.wizards.receive_pharmacy_products import (
    ReceivePharmacyProducts as PharmacyProducts,
)


class ReceivePharmacyProducts(PharmacyProducts):
    def _add(self):
        line = super()._add()
        if not config["test_enable"]:
            line.print_reception_pharmacy_label()
        return line

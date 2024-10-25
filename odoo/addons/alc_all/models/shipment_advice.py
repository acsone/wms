# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tools import drop_index, index_exists

from odoo.addons.shipment_advice.models import shipment_advice


class ShipmentAdvice(shipment_advice.ShipmentAdvice):

    name = fields.Char(index=False)

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "shipment_advice_name_uniq",
        ):
            # covered by the previous index
            drop_index(self._cr, "shipment_advice_name_index", "shipment_advice")

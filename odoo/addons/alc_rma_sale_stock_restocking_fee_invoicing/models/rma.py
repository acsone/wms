# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.models.rma import Rma as RmaBase


class Rma(RmaBase):
    def _create_receipt(self):
        res = super()._create_receipt()
        if (
            self.reason_id.charge_restocking_fee
            and self.partner_id.charge_restocking_fee
        ):
            self.reception_move_id.charge_restocking_fee = True
        return res

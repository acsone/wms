# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_carrier_label_gls.models.res_partner import (
    ResPartner as Partner,
)


class ResPartner(Partner):
    def _gls_prepare_address(self):
        self.ensure_one()
        address_payload = super()._gls_prepare_address()
        address_payload["Name2"] = self.suite if self.suite else ""
        return address_payload

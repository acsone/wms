# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AddressService(AbstractComponent):
    _inherit = "shopinvader.address.service"

    def _json_parser(self):
        parser = super(AddressService, self)._json_parser()
        parser.append("vet_depot_number")
        parser.append("vet_subscription_number")
        return parser

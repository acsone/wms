# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartnerSerializer(models.AbstractModel):
    _inherit = "res.partner.serializer"

    @property
    def _json_address_parser(self):
        parser = super(ResPartnerSerializer, self)._json_address_parser
        parser.append("vet_depot_number")
        parser.append("vet_subscription_number")
        return parser

    @property
    def _json_address_schema(self):
        schema = super(ResPartnerSerializer, self)._json_address_schema
        schema.update(
            {
                "vet_depot_number": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                },
                "vet_subscription_number": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                },
            }
        )
        return schema

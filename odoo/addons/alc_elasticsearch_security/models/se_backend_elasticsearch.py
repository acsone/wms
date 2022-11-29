# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SeBackendElasticsearch(models.Model):

    _inherit = "se.backend.elasticsearch"

    role_ids = fields.One2many("elasticsearch.role", "backend_id")

    def create_pricelist_roles(self):
        self.ensure_one()
        pricelists = self.env["product.pricelist"].search([])
        for pricelist in pricelists:
            self.create_or_update_linked_role(pricelist)

    @api.model
    def get_exported_fields(self):
        """Return the list of field names exported, to authorize them."""
        # could be split into one generic, OCA function, and an ALC override
        export = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        s = lambda x: x.split(":")[-1]  # keep the alias
        g = lambda y: s(y[0]) if isinstance(y, tuple) else s(y)  # root subparser
        fs = [g(e) for e in export.get_json_parser()]
        return [f for f in fs if not any(e in f for e in ("price", "stock"))]

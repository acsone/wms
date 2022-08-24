# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.queue_job.job import job


class SeBackendElasticsearch(models.Model):

    _inherit = "se.backend.elasticsearch"

    role_ids = fields.One2many("elasticsearch.role", "backend_id")

    def create_pricelist_roles(self):
        self.ensure_one()
        pricelists = self.env["product.pricelist"].search([])
        for pricelist in pricelists:
            self.create_or_update_pricelist_role(pricelist)

    # The queue capacity must be set to 1 since OpensSearch doesn't support
    # concurrent update of roles
    @job(default_channel="root.background.ellasticsearch.role")
    def create_or_update_pricelist_role(self, pricelist):
        BODY = """{
            "index_permissions":[
                {
                    "index_patterns":["alc_shopinvader_variant_*"],
                    "fls": ["indicated_price", "price.%s.*", "price.%s.*", "current_%s", "current_%s", "current_%s_exclusive"]
                }
            ]
            }
        """
        pricelist._compute_role_name()  # it is a compute store, value might be outdated
        price_role_name = pricelist.role_name
        domain = [("pricelist_id", "=", pricelist.id)]
        existing_role = self.env["elasticsearch.role"].search(domain)
        values = {
            "body": BODY
            % (
                price_role_name,
                pricelist.discount_role_name,
                price_role_name,
                pricelist.discount_role_name,
                pricelist.discount_role_name,
            ),
            "name": price_role_name,
        }
        if not existing_role:
            values.update({"backend_id": self.id, "pricelist_id": pricelist.id})
            existing_role.create(values)
        else:
            existing_role.write(values)

    @api.model
    def get_exported_fields(self):
        """Return the list of field names exported, to authorize them."""
        # could be split into one generic, OCA function, and an ALC override
        export = self.env.ref("shopinvader.ir_exp_shopinvader_variant")
        s = lambda x: x.split(":")[-1]  # keep the alias
        g = lambda y: s(y[0]) if isinstance(y, tuple) else s(y)  # root subparser
        fs = [g(e) for e in export.get_json_parser()]
        return [f for f in fs if not any(e in f for e in ("price", "stock"))]

# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from slugify import slugify

from odoo import fields, models


class SeBackendElasticsearch(models.Model):

    _inherit = "se.backend.elasticsearch"

    role_ids = fields.One2many("elasticsearch.role", "backend_id")

    def create_pricelist_roles(self):
        self.ensure_one()
        pricelists = self.env["product.pricelist"].search([])
        for pricelist in pricelists:
            self.create_or_update_pricelist_role(pricelist)

    def create_or_update_pricelist_role(self, pricelist):
        BODY = """{"index_permissions": [{"fls": ["price_%s"]}]}"""
        role_name = slugify(pricelist.name)
        domain = [("name", "=", role_name), ("backend_id", "=", self.id)]
        existing_role = self.env["elasticsearch.role"].search(domain)
        values = {"body": BODY % role_name}
        if not existing_role:
            values.update({"name": role_name, "backend_id": self.id})
            existing_role.create(values)
        else:
            existing_role.write(values)

# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "one.vat.mixin"]

    vat_id = fields.Many2one("account.tax", compute="_compute_product_vat")
    vat = fields.Char(compute="_compute_product_vat")

    @api.constrains("taxes_id")
    def _check_only_one_vat_customer_tax(self):
        self._check_only_one_vat_tax_field("taxes_id")

    @api.constrains("supplier_taxes_id")
    def _check_only_one_vat_supplier_tax(self):
        self._check_only_one_vat_tax_field("supplier_taxes_id")

    @api.depends("taxes_id")
    def _compute_product_vat(self):
        vat_group = self.env.ref("account_tax_one_vat.vat_tax_group")
        for record in self:
            vat = record.taxes_id.filtered(lambda r: r.tax_group_id == vat_group)
            record.vat_id = vat
            record.vat = vat.name

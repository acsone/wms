# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "one.vat.mixin"]

    @api.constrains("taxes_id")
    def _check_only_one_vat_customer_tax(self):
        self._check_only_one_vat_tax_field("taxes_id")

    @api.constrains("supplier_taxes_id")
    def _check_only_one_vat_supplier_tax(self):
        self._check_only_one_vat_tax_field("supplier_taxes_id")

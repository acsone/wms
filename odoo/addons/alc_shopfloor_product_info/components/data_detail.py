# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component


class DataDetailAction(Component):
    _inherit = "shopfloor.data.detail.action"

    @property
    def _product_detail_parser(self):
        parser = super(DataDetailAction, self)._product_detail_parser
        parser.append(
            ("locations", lambda record, fname: self.locations_for_product(record),)
        )
        return parser

    def locations_for_product(self, record):
        res = []
        # Retrieve all products -- maybe more than one location
        product_template = record.product_tmpl_id
        products = product_template.product_variant_ids

        quants = self.env["stock.quant"].search([("product_id", "in", products.ids)])
        locations = quants.mapped("location_id").filtered(
            lambda l: l.usage == "internal"
        )
        for location in locations:
            loc = self.location_detail(location)
            res.append(loc)
        return res

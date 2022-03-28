# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools
from odoo.osv.expression import AND


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    @tools.ormcache()
    def _get_shop_domain(self):
        assortment = self.env.ref("alc_eshop.shopinvader_assortment_store")
        return assortment._get_eval_domain()

    def _get_product_domain(self):
        res = super(ResPartner, self)._get_product_domain()
        return AND([res, self._get_shop_domain()])

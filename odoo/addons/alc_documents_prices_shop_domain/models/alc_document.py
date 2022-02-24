# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
from odoo.osv.expression import AND


class AlcDocument(models.Model):

    _inherit = "alc.document"

    def _get_products_domain(self):
        res = super(AlcDocument, self)._get_products_domain()
        assortment = self.env.ref("alc_eshop.shopinvader_assortment_store")
        domain_assortment = assortment._get_eval_domain()
        return AND([res, domain_assortment])

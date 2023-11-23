# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, tools
from odoo.osv.expression import AND

from odoo.addons.alc_partner_type.models.res_partner import ResPartner as ResPartnerBase


class ResPartner(ResPartnerBase):
    @api.model
    @tools.ormcache()
    def _get_shop_domain(self):
        assortment = self.env.ref(
            "alc_eshop_product_domain.shopinvader_assortment_store"
        )
        return assortment._get_eval_domain()

    def _get_product_domain(self):
        product_domain = super()._get_product_domain()
        return AND([product_domain, self._get_shop_domain()])

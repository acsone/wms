# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.models import Model


class ProductPricelist(Model):

    _name = "product.pricelist"
    _inherit = ["product.pricelist", "elasticsearch.role.mixin"]

    def _get_role_name(self):
        return self.role_name

    def _get_role_body(self):
        body = """{
            "index_permissions":[
                {
                    "index_patterns":["alc_shopinvader_variant_*"],
                    "fls": ["indicated_price", "price.%s.*", "price.%s.*", "current_%s", "current_%s", "current_%s_exclusive"]
                }
            ]
            }
        """
        price_role_name = self.role_name
        return body % (
            price_role_name,
            self.discount_role_name,
            price_role_name,
            self.discount_role_name,
            self.discount_role_name,
        )

    def _get_vals(self):
        self._compute_role_name()  # it is a compute store, value might be outdated
        return super()._get_vals()

# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_sale.routers.sales import (
    ShopinvaderApiSaleSalesRouterHelper,
)


class Shopinvader_api_saleSales_routerHelper(ShopinvaderApiSaleSalesRouterHelper):

    _inherit = "shopinvader_api_sale.sales_router.helper"

    def _get_domain_adapter(self):
        domain = super()._get_domain_adapter()
        # only return normal and call-off sale orders
        domain.append(("order_type", "in", ("order", "call_off")))
        return domain

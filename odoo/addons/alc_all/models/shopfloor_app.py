# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import drop_index, index_exists

from odoo.addons.shopfloor.models import shopfloor_app


class ShopfloorApp(shopfloor_app.ShopfloorApp):

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "shopfloor_app_tech_name",
        ):
            # covered by the previous index
            drop_index(self._cr, "shopfloor_app_tech_name_index", "shopfloor_app")

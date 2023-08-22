# Copyright 2023 ACSONE SA/NV (http://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class DataDetailAction(Component):
    _inherit = "shopfloor.data.detail.action"

    def _get_product_locations(self, record):
        locations = super()._get_product_locations(record)
        return locations.filtered("display_in_shopfloor_product_info")

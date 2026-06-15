# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component


class SearchAction(Component):
    _inherit = "shopfloor.search.action"

    @property
    def _barcode_type_handler(self):
        handlers = super(SearchAction, self)._barcode_type_handler

        menu = self.work.menu
        if not menu:
            return handlers

        mapping = {
            "product": menu.allow_product_scan,
            "package": menu.allow_package_scan,
            "picking": menu.allow_picking_scan,
            "location": menu.allow_location_scan,
            "location_dest": menu.allow_location_dest_scan,
            "lot": menu.allow_lot_scan,
            "serial": menu.allow_serial_scan,
            "packaging": menu.allow_packaging_scan,
            "delivery_packaging": menu.allow_delivery_packaging_scan,
            "origin_move": menu.allow_origin_move_scan,
            "expiration_date": menu.allow_expiration_date_scan,
        }

        for btype, is_allowed in mapping.items():
            if not is_allowed and btype in handlers:
                del handlers[btype]

        return handlers

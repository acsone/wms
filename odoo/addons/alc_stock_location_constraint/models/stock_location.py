# Copyright 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):
    @api.constrains(
        "zone_location_id", "corridor", "rack", "level", "posx", "posy", "posz"
    )
    def _check_alc_unique_location_coordinates(self):
        constraint = self.env["ir.config_parameter"].get_param(
            "alc_stock_location_constraint.stock_location_constraint"
        )
        if not constraint:
            return
        for location in self:
            domain = [
                ("zone_location_id", "=", location.zone_location_id.id),
                ("corridor", "=", location.corridor),
                ("rack", "=", location.rack),
                ("level", "=", location.level),
                ("posx", "=", location.posx),
                ("posy", "=", location.posy),
                ("posz", "=", location.posz),
                ("id", "!=", location.id),
            ]
            duplicate = self.search(domain)
            if duplicate:
                raise ValidationError(
                    _(
                        "The following locations have the same characteristics than this one ({current_location}): {duplicate_locations}"
                    ).format(
                        current_location=location.display_name,
                        duplicate_locations="\n".join(duplicate.mapped("display_name")),
                    )
                )

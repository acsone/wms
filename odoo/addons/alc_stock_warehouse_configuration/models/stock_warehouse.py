# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_warehouse import Warehouse

PROTECTED_FIELDS = ["reception_steps", "delivery_steps"]


class StockWarehouse(Warehouse):

    alc_constrains_configuration = fields.Boolean(
        string="Constrain Configuration",
        help="Check this if you don't want warehouse configuration changed (delivery/reception steps).",
    )

    def write(self, vals):
        if not any(warehouse.alc_constrains_configuration for warehouse in self):
            return super().write(vals)
        if any(val in PROTECTED_FIELDS for val in vals):
            raise UserError(_("You cannot modify the Warehouse configuration!"))
        return super().write(vals)

    def _get_input_output_locations(self, reception_steps, delivery_steps):
        # As current configuration is quite touchy to change using Odoo's warehouse
        # configuration, constrain the Warehouse default location for Receptions
        # without changing the reception steps.
        # TODO: Align stock configuration to allow warehouse behavior when writing it.
        in_loc, out_loc = super()._get_input_output_locations(
            reception_steps, delivery_steps
        )
        if self.alc_constrains_configuration and self == self.env.ref(
            "stock.warehouse0"
        ):
            reception = self.env.ref("stock.stock_location_company")
            in_loc = reception
        return (in_loc, out_loc)

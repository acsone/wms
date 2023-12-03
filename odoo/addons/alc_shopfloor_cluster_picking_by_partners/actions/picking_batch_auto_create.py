# Copyright 2020 Camptocamp
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class PickingBatchAutoCreateAction(Component):
    """Automatic creation of picking batches."""

    _inherit = "shopfloor.picking.batch.auto.create"

    def _prepare_make_picking_batch_values(
        self,
        picking_types,
        group_by_commercial_partner=False,
        maximum_number_of_preparation_lines=False,
        stock_device_types=None,
        **kwargs,
    ):
        values = super()._prepare_make_picking_batch_values(
            picking_types,
            group_by_commercial_partner=group_by_commercial_partner,
            maximum_number_of_preparation_lines=maximum_number_of_preparation_lines,
            stock_device_types=stock_device_types,
            **kwargs,
        )
        shopfloor_menu = kwargs.get("shopfloor_menu")
        if shopfloor_menu:
            values[
                "group_pickings_by_partner"
            ] = shopfloor_menu.group_pickings_by_partner
        return values

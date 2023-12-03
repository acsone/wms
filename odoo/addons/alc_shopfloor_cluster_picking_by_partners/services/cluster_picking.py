# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def _create_wizard_batch_picking(self, env_in_cursor, menu):
        wizard = super(ClusterPicking, self)._create_wizard_batch_picking(
            env_in_cursor, menu
        )
        if menu.group_pickings_by_partner:
            wizard.write({"group_pickings_by_partner": menu.group_pickings_by_partner})
        return wizard

    def _last_picked_line(self, picking):
        res = super(ClusterPicking, self)._last_picked_line(picking)
        if self.work.menu.group_pickings_by_partner:
            # Retrieve pickings for the current wave and for the same partner
            pickings = self.env["stock.picking"].search(
                [
                    ("wave_id", "=", picking.wave_id.id),
                    ("partner_id", "=", picking.partner_id.id),
                ]
            )
            # Get the last picked line for these pickings
            return fields.first(
                pickings.mapped("pack_operation_ids")
                .filtered(
                    lambda l: l.qty_done > 0
                    and l.result_package_id
                    # if we are moving the entire package, we shouldn't
                    # add stuff inside it, it's not a new package
                    and l.package_id != l.result_package_id
                )
                .sorted(key="write_date", reverse=True)
            )
        return res

    def _check_picking_condition(self, bin_package, operation):
        res = super(ClusterPicking, self)._check_picking_condition(
            bin_package, operation
        )
        if self.work.menu.group_pickings_by_partner:
            if any(
                ml.picking_id.partner_id != operation.picking_id.partner_id
                for ml in bin_package.planned_pack_operation_ids.filtered(
                    lambda x: x.state not in ("done", "cancel")
                )
            ):
                return True
            return False
        return res

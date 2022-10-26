# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def _create_wizard_batch_picking(self, env_in_cursor, menu):
        wizard = super(ClusterPicking, self)._create_wizard_batch_picking(
            env_in_cursor, menu
        )
        wizard.write({"delivery_carrier_ids": [(6, 0, menu.delivery_carrier_ids.ids)]})
        return wizard

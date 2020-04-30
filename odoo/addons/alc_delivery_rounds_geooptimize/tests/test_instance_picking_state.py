# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests import test_instance_picking_state


class TestInstancePickingState(
    test_instance_picking_state.TestInstancePickingState
):
    """
    All the initial tests must succeed if the optimization process is disabled
    """

    @classmethod
    def setUpClass(cls):
        super(TestInstancePickingState, cls).setUpClass()
        cls.IrConfigParameter = cls.env["ir.config_parameter"]
        cls.IrConfigParameter.set_param(
            "alc_delivery_rounds_geooptimize.geo_optimization_enabled", "false"
        )

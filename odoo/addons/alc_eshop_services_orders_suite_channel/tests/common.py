# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_eshop_services_orders.tests.common import TestOrders


class TestOrdersSuiteChannel(TestOrders):
    @classmethod
    def setUpClass(cls):
        super(TestOrdersSuiteChannel, cls).setUpClass()

        cls.sale_order.suite_name = "suite_name"
        cls.sale_order.sale_channel = "phone"

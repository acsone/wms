# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_receive_lot.tests.common import PackOperationLotAddCommon


class TestStockPickingStartAtReceiveLot(PackOperationLotAddCommon):
    def test_1(self):
        self.assertFalse(self.picking.started)
        self.button_receive()
        self.assertTrue(self.picking.started)

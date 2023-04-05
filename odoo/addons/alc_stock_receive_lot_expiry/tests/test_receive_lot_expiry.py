# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from freezegun import freeze_time

from odoo.tests.common import TransactionCase

from odoo.addons.alc_stock_receive_lot.tests.common import PackOperationLotAddCommon


class TestPackOperationLotAdd(PackOperationLotAddCommon, TransactionCase):
    @freeze_time("2022-02-01")
    def test_receive_on_view(self):
        self._create_lot()
        picking = self.picking
        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).create({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]

        # Simulate putaway to bin1 and bin2
        op1.location_dest_id = self.bin1

        wiz.move_line_id = op1
        self.assertTrue(wiz.lot_required)
        self.assertEqual(wiz.remaining_qty, 5)
        wiz.qty = 10
        wiz.expiration_date = "2030-01-01 10:00:00"
        self.assertFalse(wiz.is_removal_date_expired)
        wiz.expiration_date = "2022-01-01 10:00:00"
        self.assertTrue(wiz.is_removal_date_expired)

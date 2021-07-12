# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.alc_delivery_carrier_gls.tests.common import GLSCommonFeatures
from odoo.addons.delivery_carrier_label_gls.tests.common import mock_gls_client


class TestStockPicking(GLSCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()

    def test_00(self):
        """
        Data: One SO with 2 medoc and 2 ali
        Test Case: Process the pickings then the shipping
        Expected Result:
           Only one pack medoc with added aliments in it
          The transfer is possible
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p2, self.p3, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc.force_assign()

        for pack in pick_medoc.pack_operation_product_ids:
            pack.qty_done = pack.product_qty

        pack_medoc = pick_medoc.put_in_pack()
        pick_medoc.do_transfer()

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty
        final_pack = pack_medoc.browse(ship.put_in_pack()["res_id"])

        self.assertEqual(final_pack.id, pack_medoc.id)
        for pack in ship.pack_operation_ids:
            self.assertEqual(pack.result_package_id.id, pack_medoc.id)

        # add required values required to finalize the shipping on transfer
        final_pack.packaging_id = self.packaging_parcel
        final_pack.shipping_weight = 10

        with mock_gls_client():
            ship.do_transfer()

    def test_01(self):
        """
        Data: One SO with 2 ali
        Test Case: Process the pickings then the shipping
        Expected Result: Everything stays as usual
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p2, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        self.assertFalse(pick_medoc)

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty
        final_pack = ship.put_in_pack()
        final_pack_id = (
            final_pack["res_id"] if isinstance(final_pack, dict) else final_pack.id
        )
        self.assertEqual(
            final_pack_id, ship.mapped("pack_operation_ids.result_package_id").id
        )

    def test_02(self):
        """
        Data: One SO with 2 medoc and 2 ali
        Test Case: Medoc are not put in pack
        Expected Result: Call super and create a new package
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p2, self.p3, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc.force_assign()

        for pack in pick_medoc.pack_operation_product_ids:
            pack.qty_done = pack.product_qty

        pick_medoc.do_transfer()

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty

        final_pack = ship.put_in_pack()
        final_pack_id = (
            final_pack["res_id"] if isinstance(final_pack, dict) else final_pack.id
        )
        self.assertEqual(
            final_pack_id, ship.mapped("pack_operation_ids.result_package_id").id
        )

    def test_03(self):
        """
        Data: 2 SO, one with 2 medoc and 2 ali. The other with 2 medoc
        Test Case: Medoc are put in pack twice, creating 2 packs
        Expected Result: Raise error for medoc because 2 packs
        """
        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p2, self.p3, self.p4],
            carrier_id=self.carrier.id,
        )
        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_alim = picks.filtered(lambda p: p.picking_type_id == self.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc.force_assign()

        for pack in pick_medoc.pack_operation_product_ids:
            pack.qty_done = 5
        pick_medoc.put_in_pack()
        pick_medoc.do_transfer()

        sale2 = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p3],
            carrier_id=self.carrier.id,
        )
        picks2 = sale2.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        pick_medoc2 = picks2.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )
        pick_medoc2.force_assign()
        for pack in pick_medoc2.pack_operation_product_ids:
            pack.qty_done = pack.product_qty

        pick_medoc2.put_in_pack()
        pick_medoc2.do_transfer()

        pick_alim.force_assign()
        for pack in pick_alim.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick_alim.do_transfer()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.force_assign()
        for pack in ship.pack_operation_ids:
            pack.qty_done = pack.product_qty

        with self.assertRaises(ValidationError):
            ship.put_in_pack()

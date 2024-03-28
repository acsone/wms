# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.alc_delivery_carrier_gls.tests.common import GLSCommonFeatures
from odoo.addons.delivery_carrier_label_gls.tests.common import mock_gls_client


class TestStockPicking(GLSCommonFeatures):
    @classmethod
    def _create_pick_ship(cls):
        sale = cls._confirm_sale_order(
            partner=cls.partner1,
            product=[cls.p1, cls.p2, cls.p3, cls.p4],
            carrier_id=cls.carrier.id,
            picking_policy="one",
        )
        picks = sale.picking_ids.filtered(lambda p: p.picking_type_code == "internal")
        pick_alim = picks.filtered(lambda p: p.picking_type_id == cls.picking_type_ali)
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == cls.picking_type_medoc
        )

        pick_medoc.action_assign()
        for pack in pick_medoc.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty
        pack = pick_medoc.action_put_in_pack()
        # set a specific package type
        pack.package_type_id = cls.env["stock.package.type"].create(
            {"name": "parcel", "shipper_package_code": "INTERNAL"}
        )
        cls.pack_medoc = pack
        pick_medoc.button_validate()

        pick_alim.action_assign()
        for pack in pick_alim.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty
        pick_alim.button_validate()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        ship.action_assign()
        return sale, picks, ship

    def test_00(self):
        """
        Data: One SO with 2 medoc and 2 ali.

        Test Case: Process the pickings then the shipping
        Expected Result:
           Only one pack with the pack medoc and the alliments in it
        """
        _sale, _picks, ship = self._create_pick_ship()

        # process all the lines
        for move_line in ship.mapped("move_line_ids"):
            move_line.qty_done = move_line.reserved_uom_qty

        # process the picking
        gls_wizard_action_1 = ship.action_put_in_pack()
        # This simulates the action return and the wizard creation
        # triggering computes and onchanges
        wizard_model = self.env["delivery.package.gls.wizard"]
        wizard_1 = Form(wizard_model.with_context(**gls_wizard_action_1["context"]))
        gls_wizard_1 = wizard_1.save()
        gls_wizard_1.shipping_weight = 89
        with mock_gls_client():
            gls_wizard_1.put_in_pack()
        package = gls_wizard_1.package_id
        self.assertEqual(package.shipping_weight, 89)
        self.assertEqual(package.package_type_id.package_carrier_type, "gls")

    def test_package_done(self):
        """
        Data: One SO with 2 medoc and 2 ali.

        Test Case: Process the pickings then the shipping
        Expected Result:
           Only one pack with the pack medoc and the alliments in it
        """
        type_out = self.env.ref("stock.picking_type_out")
        type_out.show_entire_packs = True
        _sale, _picks, ship = self._create_pick_ship()

        # process all the lines without packages - As this is the case in deliveries
        move_lines_without_pack = ship.mapped("move_line_ids").filtered(
            lambda line: not line.package_id
        )
        for move_line in move_lines_without_pack:
            move_line.qty_done = move_line.reserved_uom_qty

        # process the picking
        gls_wizard_action_1 = ship.action_put_in_pack()
        # This simulates the action return and the wizard creation
        # triggering computes and onchanges
        wizard_model = self.env["delivery.package.gls.wizard"]
        wizard_1 = Form(wizard_model.with_context(**gls_wizard_action_1["context"]))
        gls_wizard_1 = wizard_1.save()
        gls_wizard_1.shipping_weight = 89
        with mock_gls_client():
            gls_wizard_1.put_in_pack()
        package = gls_wizard_1.package_id
        self.assertEqual(package.shipping_weight, 89)
        self.assertEqual(package.package_type_id.package_carrier_type, "gls")
        for line in ship.move_line_ids:
            self.assertEqual(line.qty_done, line.reserved_uom_qty)

        result = ship.button_validate()
        self.assertTrue(result)

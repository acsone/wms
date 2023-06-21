# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.alc_delivery_carrier_gls.tests.common import GLSCommonFeatures


class TestStockPickingValidation(GLSCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.gls_wizard_model = cls.env["delivery.package.gls.wizard"]

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
        pick_medoc.action_put_in_pack()
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
        Data: One SO, picks are done.

        Ship has to be done
        Test Case: We do not process the pack for medicine
        Expected Result: No way to validate the ship by standard mechanism.
                         We have to force validate if we want to validate it anyway
        """

        sale, _, ship = self._create_pick_ship()

        self.assertTrue(ship.gls_pack_in_picking)
        self.assertFalse(ship.validate_allowed)

        with self.assertRaises(UserError):
            ship.button_validate()

        ships = self.env["stock.picking"].search(
            [("origin", "=", sale.name), ("picking_type_code", "=", "outgoing")]
        )
        self.assertEqual(len(ships), 1)

        ship.action_force_validate()

        # since we didn't process any packs in the ship, it does nothing
        ships = self.env["stock.picking"].search(
            [("origin", "=", sale.name), ("picking_type_code", "=", "outgoing")]
        )
        self.assertEqual(ships, ship)  # is this really something we should test?

    def test_01(self):
        """
        Data: One SO, picks are done.

        Ship has to be done
        Test Case: We process all packs in the ship. But not the food products
        Expected Result: We can't validate the ship
        """

        ship = self._create_pick_ship()[2]
        # Do all the operations but the package one
        lines_without_package = ship.move_line_ids.filtered(
            lambda line: not line.package_level_id
        )
        for ml in lines_without_package:
            ml.qty_done = ml.reserved_uom_qty
        self.assertTrue(ship.gls_pack_in_picking)
        ship.action_put_in_pack()
        self.assertFalse(ship.validate_allowed)

        # Do the package operation
        for ml in ship.move_line_ids - lines_without_package:
            ml.qty_done = ml.reserved_uom_qty
        self.assertFalse(ship.gls_pack_in_picking)

    def test_02(self):
        """
        Data:Two SO, picks are done.

        Ship has to be done
        Test Case: We process one medicine pack outin the first time
                   Ship1 cannot be validated. We then process food.
                   Ship 1 can be validated, ship 2 can't
                   We process the second medicine pack one to allow second shipping
                   validation
        Expected Result: Once 2 packs are processed, we can validate the ships
        """
        ship = self._create_pick_ship()[2]

        sale1 = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p3],
            carrier_id=self.carrier.id,
            picking_policy="one",
        )

        picks1 = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "internal"
        )
        pick_medoc1 = picks1.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )

        pick_medoc1.action_assign()
        for pack in pick_medoc1.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty

        pick_medoc1.action_put_in_pack()
        pick_medoc1.button_validate()

        ship1 = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pack0 = ship.move_line_ids.filtered(lambda x: x.result_package_id)[0]
        pack0.qty_done = pack0.reserved_uom_qty

        with self.assertRaises(UserError):
            ship.button_validate()

        for pack in ship.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty

        pack_action = ship.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        # We instanciate the wizard with the context of the action
        # Then set the delivery package type
        pack_wiz = (
            self.env["choose.delivery.package"]
            .with_context(**pack_action_ctx)
            .create({})
        )
        # validate the wizard
        pack_wiz.action_put_in_pack()
        ship.button_validate()

        with self.assertRaises(UserError):
            ship1.button_validate()

        for pack in ship1.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty
        # ship1.action_put_in_pack()
        ship1.button_validate()

    def test_03(self):
        """
        Data: Carrier is not GLS.

        Test Case: We process the picks, not the medicine pack
        Expected Result: Everything can still be validated because it is not gls case
        """
        product_carrier2 = self.env["product.product"].create(
            {
                "name": "Product Carrier 2",
                "sale_ok": False,
                "type": "service",
            }
        )
        carrier2 = self.env["delivery.carrier"].create(
            {
                "name": "Unittest delivery carrier",
                "delivery_type": "fixed",
                "fixed_price": 10.0,
                "product_id": product_carrier2.id,
            }
        )

        sale = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p1, self.p3],
            carrier_id=carrier2.id,
        )

        picks = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "internal"
        )
        pick_medoc = picks.filtered(
            lambda p: p.picking_type_id == self.picking_type_medoc
        )

        pick_medoc.action_assign()
        for pack in pick_medoc.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty

        pick_medoc.action_put_in_pack()
        pick_medoc.button_validate()

        ship = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        self.assertFalse(ship.gls_pack_in_picking)
        self.assertTrue(ship.validate_allowed)

        ship.button_validate()

        ships = self.env["stock.picking"].search([("origin", "=", sale.name)])
        self.assertEqual(len(ships), 2)

    def test_04(self):
        """
        Data: Only 1 alim to ship.... (Pick done).

        Test Case: We validate the ship without processing the operation
        Expected Result: Validation error since the operation is not done nor into the pac
        """
        _, _, ship = self._create_pick_ship()

        sale1 = self._confirm_sale_order(
            partner=self.partner1,
            product=[self.p4],
            carrier_id=self.carrier.id,
            picking_policy="one",
        )

        pick = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "internal"
        )
        pick.action_assign()
        for pack in pick.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty

        pick.button_validate()

        ship = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        # validation is not possible since qty are not processed nor put in pack
        with self.assertRaises(UserError):
            ship.button_validate()

        # process qty
        for pack in ship.move_line_ids:
            pack.qty_done = pack.reserved_uom_qty

        # validation is not possible since product put in pack
        with self.assertRaises(UserError):
            ship.button_validate()

        pack_action = ship.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        # We instanciate the wizard with the context of the action
        # Then set the delivery package type
        pack_wiz = (
            self.env["choose.delivery.package"]
            .with_context(**pack_action_ctx)
            .create({})
        )
        # validate the wizard
        pack_wiz.action_put_in_pack()
        ship.button_validate()

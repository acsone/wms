# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.shopfloor.tests.common import CommonCase


class TestSearchFilter(CommonCase):
    @classmethod
    def setUpClassVars(cls):
        res = super().setUpClassVars()
        cls.picking_type = cls.env.ref("stock.picking_type_internal")

        cls.test_menu = (
            cls.env["shopfloor.menu"]
            .sudo()
            .create(
                {
                    "name": "Test Scan Search Menu",
                    # Link to the scenario usage name
                    "scenario_id": cls.env.ref("shopfloor.scenario_cluster_picking").id,
                    # Link the warehouse operations allowed for this menu
                    "picking_type_ids": [Command.link(cls.picking_type.id)],
                    # Your new validation configuration rules
                    "allow_product_scan": True,
                    "allow_location_scan": False,  # Blocks bin identifier confusion!
                }
            )
        )
        with cls.work_on_actions(cls, menu=cls.test_menu) as work:
            cls.search = work.component(usage="search")

        return res

    def test_search_product_handler(self):
        self.test_menu.sudo().write({"allow_product_scan": True})
        res_allowed = self.search.find(barcode="A", types=["product"])
        self.assertEqual(res_allowed.type, "product")
        self.assertEqual(res_allowed.record, self.product_a)

        self.test_menu.sudo().write({"allow_product_scan": False})
        res_restricted = self.search.find(barcode="A", types=["product"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_package_handler(self):
        package = self.env["stock.quant.package"].sudo().create({"name": "PKG001"})

        self.test_menu.sudo().write({"allow_package_scan": True})
        res_allowed = self.search.find(barcode="PKG001", types=["package"])
        self.assertEqual(res_allowed.type, "package")
        self.assertEqual(res_allowed.record, package)

        self.test_menu.sudo().write({"allow_package_scan": False})
        res_restricted = self.search.find(barcode="PKG001", types=["package"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_picking_handler(self):
        picking = self._create_picking(lines=[(self.product_a, 1)], confirm=True)

        self.test_menu.sudo().write({"allow_picking_scan": True})
        res_allowed = self.search.find(barcode=picking.name, types=["picking"])
        self.assertEqual(res_allowed.type, "picking")
        self.assertEqual(res_allowed.record, picking)

        self.test_menu.sudo().write({"allow_picking_scan": False})
        res_restricted = self.search.find(barcode=picking.name, types=["picking"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_location_handler(self):
        self.test_menu.sudo().write({"allow_location_scan": True})
        res_allowed = self.search.find(barcode="SHELF1", types=["location"])
        self.assertEqual(res_allowed.type, "location")
        self.assertEqual(res_allowed.record, self.shelf1)

        self.test_menu.sudo().write({"allow_location_scan": False})
        res_restricted = self.search.find(barcode="SHELF1", types=["location"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_location_dest_handler(self):
        self.test_menu.sudo().write({"allow_location_dest_scan": True})
        res_allowed = self.search.find(barcode="SHELF1", types=["location_dest"])
        self.assertEqual(res_allowed.type, "location_dest")
        self.assertEqual(res_allowed.record, self.shelf1)

        self.test_menu.sudo().write({"allow_location_dest_scan": False})
        res_restricted = self.search.find(barcode="SHELF1", types=["location_dest"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_lot_handler(self):
        lot = self._create_lot(self.product_a)
        lot.sudo().name = "LOT001"

        self.test_menu.sudo().write({"allow_lot_scan": True})
        res_allowed = self.search.find(barcode="LOT001", types=["lot"])
        self.assertEqual(res_allowed.type, "lot")
        self.assertEqual(res_allowed.record, lot)

        self.test_menu.sudo().write({"allow_lot_scan": False})
        res_restricted = self.search.find(barcode="LOT001", types=["lot"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_serial_handler(self):
        serial = self._create_lot(self.product_b)
        serial.sudo().name = "SN001"

        self.test_menu.sudo().write({"allow_serial_scan": True})
        res_allowed = self.search.find(barcode="SN001", types=["serial"])
        self.assertEqual(res_allowed.type, "serial")
        self.assertEqual(res_allowed.record, serial)

        self.test_menu.sudo().write({"allow_serial_scan": False})
        res_restricted = self.search.find(barcode="SN001", types=["serial"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_packaging_handler(self):
        self.test_menu.sudo().write({"allow_packaging_scan": True})
        res_allowed = self.search.find(barcode="ProductABox", types=["packaging"])
        self.assertEqual(res_allowed.type, "packaging")
        self.assertEqual(res_allowed.record, self.product_a_packaging)

        self.test_menu.sudo().write({"allow_packaging_scan": False})
        res_restricted = self.search.find(barcode="ProductABox", types=["packaging"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_delivery_packaging_handler(self):
        pkg_type = (
            self.env["stock.package.type"]
            .sudo()
            .create({"name": "Pallet", "barcode": "PAL01"})
        )

        self.test_menu.sudo().write({"allow_delivery_packaging_scan": True})
        res_allowed = self.search.find(barcode="PAL01", types=["delivery_packaging"])
        self.assertEqual(res_allowed.type, "delivery_packaging")
        self.assertEqual(res_allowed.record, pkg_type)

        self.test_menu.sudo().write({"allow_delivery_packaging_scan": False})
        res_restricted = self.search.find(barcode="PAL01", types=["delivery_packaging"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_origin_move_handler(self):
        picking = self._create_picking(lines=[(self.product_a, 5)], confirm=True)
        # Force moves to a 'done' state to allow generic search validation tracking match
        picking.move_ids.sudo().write({"state": "done", "origin": "test-origin"})

        self.test_menu.sudo().write({"allow_origin_move_scan": True})
        res_allowed = self.search.find(barcode="test-origin", types=["origin_move"])
        self.assertEqual(res_allowed.type, "origin_move")
        self.assertIn(picking.move_ids[0], res_allowed.record)

        self.test_menu.sudo().write({"allow_origin_move_scan": False})
        res_restricted = self.search.find(barcode="SO001", types=["origin_move"])
        self.assertEqual(res_restricted.type, "none")

    def test_search_expiration_date_handler(self):
        # TODO: For now the `expiration_date_from_scan` barcode handler returns None
        # -> uncomment ↓ when the code inside base `shopfloor` is completed

        # self.test_menu.sudo().write({"allow_expiration_date_scan": True})
        # res_allowed = self.search.find(barcode="2026-12-31", types=["expiration_date"])
        # self.assertEqual(res_allowed.type, "expiration_date")

        self.test_menu.sudo().write({"allow_expiration_date_scan": False})
        res_restricted = self.search.find(
            barcode="2026-12-31", types=["expiration_date"]
        )
        self.assertEqual(res_restricted.type, "none")

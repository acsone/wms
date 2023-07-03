# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from .common import ProductCharacteristicsCommonFeatures


class TestProductTemplate(ProductCharacteristicsCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_1(self):
        # no min/max, and no route for 'approvisionner a la commande'
        self.assertTrue(self.product_template.no_min_max_no_on_command_reappro)
        self.assertTrue(self.product_template.has_anomaly)

    def test_2(self):
        # min/max, and route for 'approvisionner a la commande'
        self.product_template.write(
            {
                "orderpoint_min": 5,
                "orderpoint_max": 15,
                "route_ids": [Command.link(self.route_mto.id)],
            }
        )
        self.assertTrue(self.product_template.min_max_on_command_reappro)

    def test_3(self):
        # not sale_ok but not archived
        self.product_template.sale_ok = False
        self.assertTrue(self.product_template.sale_not_ok_not_archived)

    def test_5(self):
        # mismatch routes/ picking zone
        self.product_template.write(
            {"route_ids": [Command.set([self.route_aliment.id, self.route_medoc.id])]}
        )
        self.assertTrue(self.product_template.mismatch_route_picking)

    def test_7(self):
        # can be bought without buy route
        self.product_template.write(
            {"route_ids": [Command.unlink(self.route_buy.id)], "purchase_ok": True}
        )

        self.assertTrue(self.product_template.can_be_bought_without_buy_route)

    def test_8(self):
        # route mto + route new
        self.product_template.route_ids = [
            Command.set([self.route_mto.id, self.route_new.id])
        ]

        self.assertTrue(self.product_template.mto_with_abnormal_route)

    def test_9(self):
        # product without dimensions
        self.assertTrue(self.product_template.has_no_dimensions)

        self.product_template.write(
            {"product_height": 10.0, "product_width": 5.0, "product_length": 2.0}
        )

        self.assertFalse(self.product_template.has_no_dimensions)

    def test_10(self):
        # product without packaging dimensions
        self.assertTrue(self.product_template.packaging_has_no_dimensions)

        self.product_palette.write(
            {"height": 100.0, "width": 50.0, "packaging_length": 20.0}
        )
        self.assertTrue(self.product_template.packaging_has_no_dimensions)
        self.product_box.write(
            {"height": 100.0, "width": 50.0, "packaging_length": 20.0}
        )

        self.assertFalse(self.product_template.packaging_has_no_dimensions)

    def test_11(self):
        # product without packaging at all
        self.assertFalse(self.product_template1.packaging_has_no_dimensions)

    def test_12(self):
        # product not sale_ok but on website

        self.product_template1.write({"sale_ok": False, "web_published": True})
        self.assertTrue(self.product_template1.not_sold_on_website)

    def test_13(self):
        # product mto without sale order but with a purchase order

        self.product_template1.is_mto = True
        self.product_template1.invalidate_recordset()
        self.assertTrue(self.product_template1.mto_purchased_not_sold)

    def test_14(self):
        # product in a mto bin but without mto route
        self.product_template1.write({"location_id": self.location_bin_mto.id})
        self.assertTrue(self.product_template1.mto_stock_no_mto_route)

        self.product_template1.write({"route_ids": [Command.set([self.route_mto.id])]})
        self.product_template1.invalidate_recordset()
        self.assertFalse(self.product_template1.mto_stock_no_mto_route)

    def test_15(self):
        # product in an mto bin but with new route

        self.product_template1.write(
            {
                "route_ids": [Command.set([self.route_new.id])],
                "location_id": self.location_bin_mto.id,
            }
        )
        self.assertTrue(self.product_template1.mto_stock_new_route)

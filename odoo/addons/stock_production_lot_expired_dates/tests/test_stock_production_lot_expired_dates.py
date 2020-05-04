# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockProductionLotLifeDates(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestStockProductionLotLifeDates, cls).setUpClass()
        cls.product_model = cls.env["product.product"]
        cls.production_lot_model = cls.env["stock.production.lot"]
        cls.category = cls.env.ref("product.product_category_all")
        cls.category_2 = cls.env.ref("product.product_category_2")
        cls.category_3 = cls.env.ref("product.product_category_3")
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.product = cls.product_model.create(
            {
                "name": "Unittest product",
                "type": "product",
                "categ_id": cls.category.id,
                "use_time": 10,
                "life_time": 11,
                "alert_time": 12,
                "removal_time": 13,
            }
        )
        cls.production_lot = cls.production_lot_model.create(
            {"name": "000001", "product_id": cls.product.id}
        )

        cls.product_2 = cls.product_model.create(
            {
                "name": "Unittest product 2",
                "type": "product",
                "categ_id": cls.category_2.id,
                "use_time": -13,
                "life_time": -12,
                "alert_time": -11,
                "removal_time": -10,
            }
        )
        cls.production_lot_2 = cls.production_lot_model.create(
            {"name": "000001", "product_id": cls.product_2.id}
        )

        cls.product_3 = cls.product_model.create(
            {
                "name": "Unittest product 3",
                "type": "product",
                "categ_id": cls.category_3.id,
                "use_time": 0,
                "life_time": 0,
                "alert_time": 0,
                "removal_time": 0,
            }
        )
        cls.production_lot_3 = cls.production_lot_model.create(
            {"name": "000001", "product_id": cls.product_3.id}
        )

    def _set_lot_base_date(self, base_date):
        """ It is faster to set directly the param instead
        of relying on the config setting execution """
        self.env["ir.config_parameter"].set_param(
            "stock_production_lot_expired_dates.production_lot_base_date", base_date
        )

    def test_1_onchange_use_date(self):
        for base_date in [None, "alert", "life", "removal", "use"]:
            self._set_lot_base_date(base_date)
            for production_lot in [
                self.production_lot,
                self.production_lot_2,
                self.production_lot_3,
            ]:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                production_lot.use_date = "2016-12-23 10:00:00"
                production_lot.onchange_use_date()
                date_must_change = (
                    base_date == "use" and production_lot != self.production_lot_3
                )
                self.assertEqual(production_lot.use_date, "2016-12-23 10:00:00")
                self.assertEqual(
                    production_lot.life_date,
                    "2016-12-24 10:00:00" if date_must_change else False,
                )
                self.assertEqual(
                    production_lot.alert_date,
                    "2016-12-25 10:00:00" if date_must_change else False,
                )
                self.assertEqual(
                    production_lot.removal_date,
                    "2016-12-26 10:00:00" if date_must_change else False,
                )
                # Check the onchange not fails with no value
                production_lot.use_date = False
                production_lot.onchange_use_date()

    def test_2_onchange_life_date(self):
        for base_date in [None, "alert", "life", "removal", "use"]:
            self._set_lot_base_date(base_date)
            for production_lot in [
                self.production_lot,
                self.production_lot_2,
                self.production_lot_3,
            ]:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                production_lot.life_date = "2016-12-23 10:00:00"
                production_lot.onchange_life_date()
                date_must_change = (
                    base_date == "life" and production_lot != self.production_lot_3
                )
                self.assertEqual(
                    production_lot.use_date,
                    "2016-12-22 10:00:00" if date_must_change else False,
                )
                self.assertEqual(production_lot.life_date, "2016-12-23 10:00:00")
                self.assertEqual(
                    production_lot.alert_date,
                    "2016-12-24 10:00:00" if date_must_change else False,
                )
                self.assertEqual(
                    production_lot.removal_date,
                    "2016-12-25 10:00:00" if date_must_change else False,
                )
                # Check the onchange not fails with no value
                production_lot.life_date = False
                production_lot.onchange_life_date()

    def test_3_onchange_alert_date(self):
        for base_date in [None, "alert", "life", "removal", "use"]:
            self._set_lot_base_date(base_date)
            for production_lot in [
                self.production_lot,
                self.production_lot_2,
                self.production_lot_3,
            ]:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                production_lot.alert_date = "2016-12-23 10:00:00"
                production_lot.onchange_alert_date()
                date_must_change = (
                    base_date == "alert" and production_lot != self.production_lot_3
                )
                self.assertEqual(
                    production_lot.use_date,
                    "2016-12-21 10:00:00" if date_must_change else False,
                )
                self.assertEqual(
                    production_lot.life_date,
                    "2016-12-22 10:00:00" if date_must_change else False,
                )
                self.assertEqual(production_lot.alert_date, "2016-12-23 10:00:00")
                self.assertEqual(
                    production_lot.removal_date,
                    "2016-12-24 10:00:00" if date_must_change else False,
                )
                # Check the onchange not fails with no value
                production_lot.alert_date = False
                production_lot.onchange_alert_date()

    def test_4_onchange_removal_date(self):
        for base_date in [None, "alert", "life", "removal", "use"]:
            self._set_lot_base_date(base_date)
            for production_lot in [
                self.production_lot,
                self.production_lot_2,
                self.production_lot_3,
            ]:
                production_lot.use_date = False
                production_lot.life_date = False
                production_lot.alert_date = False
                production_lot.removal_date = False
                production_lot.removal_date = "2016-12-23 10:00:00"
                production_lot.onchange_removal_date()
                date_must_change = (
                    base_date == "removal" and production_lot != self.production_lot_3
                )
                self.assertEqual(
                    production_lot.use_date,
                    "2016-12-20 10:00:00" if date_must_change else False,
                )
                self.assertEqual(
                    production_lot.life_date,
                    "2016-12-21 10:00:00" if date_must_change else False,
                )
                self.assertEqual(
                    production_lot.alert_date,
                    "2016-12-22 10:00:00" if date_must_change else False,
                )
                self.assertEqual(production_lot.removal_date, "2016-12-23 10:00:00")
                # Check the onchange not fails with no value
                production_lot.removal_date = False
                production_lot.onchange_removal_date()

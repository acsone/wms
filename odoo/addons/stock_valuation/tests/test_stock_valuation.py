# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from freezegun import freeze_time
from openerp.osv.expression import AND, OR

from odoo import fields
from odoo.tests.common import SavepointCase


def _get_time_domain(ttime):
    now = fields.Datetime.now()
    domain = AND([[("date", ">=", ttime)], [("date", "<=", now)]])
    return OR([domain, [("move_id", "=", False)]])


class TestStockValuation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockValuation, cls).setUpClass()
        cls.env["stock.history.materialized"].refresh_view()
        cls.env["stock.history"].init()
        cls.supplier1 = cls.env.ref("base.res_partner_12")
        cls.uom = cls.env.ref("product.product_uom_unit")
        cls.p1 = cls.env["product.product"].create(
            {"name": "Sorbet", "uom_id": cls.uom.id, "property_cost_method": "average"}
        )

    def buy(self, product, price, ttime):
        with freeze_time(ttime):
            po = self.env["purchase.order"].create(
                {
                    "partner_id": self.supplier1.id,
                    "date_planned": ttime,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom": self.uom.id,
                                "product_qty": 1,
                                "price_unit": price,
                                "date_planned": ttime,
                            },
                        )
                    ],
                }
            )
            po.button_confirm()
            po.picking_ids.action_confirm()
            po.picking_ids.action_done()
        return po

    def sell(self, product, ttime):
        with freeze_time(ttime):
            so = self.env["sale.order"].create(
                {
                    "partner_id": self.supplier1.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom": self.uom.id,
                                "product_qty": 1,
                            },
                        )
                    ],
                }
            )
            so.action_confirm()
            so.picking_ids.action_confirm()
            so.picking_ids.action_done()
        return so

    def check_at_date(self, product, ttime, expected_qty, expected_inv_value):
        History = self.env["stock.history"]

        product_domain = [("product_id", "=", product.id)]
        domain = AND([_get_time_domain(ttime), product_domain])
        hist1 = History.with_context(history_date=ttime)
        data = hist1.read_group(domain, [], [])
        self.assertEqual(data[0]["quantity"], expected_qty)
        inventory_value = sum(hist1.search(domain).mapped("inventory_value"))
        self.assertEqual(inventory_value, expected_inv_value)

    def test_get_wizard_to_create_ticket(self):
        """Test we get the wizard to create tickets."""
        p1 = self.p1

        # Caution: there are calls to NOW() in the SQL query of the database
        # view, these are not affected by freeze_time -> we need use dates for
        # which we are sure that the execution time will not fall in the middle
        # of the range...
        self.po1 = self.buy(p1, 100, "2020-01-02 00:00:00")
        self.po2 = self.buy(p1, 50, "2020-01-03 00:00:00")
        self.po3 = self.buy(p1, 153, "2020-01-04 00:00:00")
        self.so1 = self.sell(p1, "2020-01-05 00:00:00")

        now = "2020-01-06 12:00:00"
        with freeze_time(now):
            self.env["stock.history.materialized"].refresh_view()

            self.check_at_date(p1, "2020-01-01 12:00:00", 0, 0)
            self.check_at_date(p1, "2020-01-02 12:00:00", 1, 100.0)
            self.check_at_date(p1, "2020-01-03 12:00:00", 2, 2 * (100.0 + 50.0) / 2)
            self.check_at_date(
                p1, "2020-01-04 12:00:00", 3, 3 * (100.0 + 50.0 + 153.0) / 3
            )
            self.check_at_date(
                p1, "2020-01-05 12:00:00", 2, 2 * (100.0 + 50.0 + 153.0) / 3
            )

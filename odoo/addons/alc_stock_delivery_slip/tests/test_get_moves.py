# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestStockDeliveryNoteGetMoves(TransactionCase):
    @classmethod
    def _create_so(cls, product):
        so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "suite_name": "123454321",
                "client_order_ref": "customer.ref.123",
                "order_line": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 10,
                            "price_unit": 50,
                            "tax_id": [(4, cls.tax.id, False)],
                        }
                    )
                ],
            }
        )
        so.action_confirm()
        reassign = so.picking_ids.filtered(
            lambda x: x.state == "confirmed"
            or ((x.state in ["partially_available", "waiting"]) and not x.printed)
        )
        if reassign:
            reassign.do_unreserve()
            reassign.action_assign()
        return so

    @classmethod
    def _prepare_shipping(cls, so, lot_name):
        picking = so.picking_ids
        picking.action_assign()
        move_ids = picking.move_ids
        move_ids.write(
            {
                "lot_ids": [
                    Command.create(
                        {
                            "expiration_date": "2017-01-31 10:00:00",
                            "name": lot_name,
                            "product_qty": 10,
                            "product_id": so.order_line[0].product_id.id,
                            "company_id": cls.env.user.company_id.id,
                        }
                    )
                ],
                "quantity_done": 10,
            }
        )
        return picking

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.smallyear = str(datetime.now().year)[2:]
        # Create a sale tax
        cls.tax = cls.env["account.tax"].create(
            {
                "is_vat": True,
                "amount": 6,
                "name": "test_tax",
            }
        )
        # Create a couple of products
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "5173360",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        # Add some stock for p1 and p2
        cls.env["stock.quant"]._update_available_quantity(
            cls.p1, cls.env.ref("stock.stock_location_stock"), 100
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.p2, cls.env.ref("stock.stock_location_stock"), 100
        )
        # Create the customer
        cls.partner = cls.env["res.partner"].create(
            {
                "title": cls.env.ref("base.res_partner_title_prof").id,
                "name": "HOENS OLIVIER",
                "email": "tester@pytest.com",
                "ref": "123456789",
                "street": "Rue Polisart 2 A",
                "zip": "5300",
                "city": "ANDENNE",
                "country_id": cls.env.ref("base.be").id,
            }
        )
        cls.so = cls._create_so(cls.p1)

    def test_no_delivery(self):
        picking = self._prepare_shipping(self.so, "20190101")
        res = picking.get_moves_by_order()
        self.assertEqual(len(res), 0)

    def test_one_shipping(self):
        picking = self._prepare_shipping(self.so, "20190101")
        picking.button_validate()
        res = picking.get_moves_by_order()
        self.assertEqual(len(res), 1)
        order, all_moves = res[0]
        self.assertEqual(order, self.so)
        moves, _bo_moves = all_moves
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0].product_qty, 10.0)

    def test_no_group_shipping(self):
        picking1 = self._prepare_shipping(self.so, "20190101")
        # create a second so
        so2 = self._create_so(self.p2)
        picking2 = self._prepare_shipping(so2, "20190102")
        (picking1 | picking2).button_validate()
        # picking 1 and 2 are separated
        # thus only their own moves are shown
        res = picking1.get_moves_by_order()
        self.assertEqual(len(res), 1)
        order, all_moves = res[0]
        self.assertEqual(order, self.so)
        moves, bo_moves = all_moves
        self.assertEqual(len(moves), 1)
        self.assertEqual(len(bo_moves), 0)
        self.assertEqual(moves[0].product_qty, 10.0)

        res = picking2.get_moves_by_order()
        self.assertEqual(len(res), 1)
        order, all_moves = res[0]
        self.assertEqual(order, so2)
        moves, bo_moves = all_moves
        self.assertEqual(len(moves), 1)
        self.assertEqual(len(bo_moves), 0)
        self.assertEqual(moves[0].product_qty, 10.0)

    def test_(self):
        picking = self._prepare_shipping(self.so, "20190101")
        res = picking.get_moves_by_order()
        self.assertEqual(len(res), 0)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        res = picking.get_moves_by_order()
        self.assertEqual(len(res), 1)
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )
        return_wizard._onchange_picking_id()
        picking_action = return_wizard.create_returns()
        reception = self.env["stock.picking"].browse(picking_action["res_id"])
        self.assertEqual(reception.state, "assigned")
        res = reception.get_moves_by_order()
        self.assertEqual(len(res), 1)

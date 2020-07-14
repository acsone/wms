# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestStockPicking(common.TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(TestStockPicking, self).setUp()

        location_obj = self.env["stock.location"]

        self.env.user.write({"ref": "757823948234", "tz": "Europe/Brussels"})

        # Create partner
        self.partner = self.env["res.partner"].create(
            {"name": "Hello World", "ref": "29969868875"}
        )

        self.warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse pick and ship",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "WPS",
            }
        )
        self.warehouse.pick_type_id.subcode = "PICK"
        self.warehouse.pick_type_id.groupbypartner = False
        self.warehouse.out_type_id.groupbypartner = True
        self.warehouse.out_type_id.create_invoice_on_transfer = True

        round_template = self.env["round.template"].create(
            {
                "code": "78",
                "name": "Test",
                "time_leave_planned": 12.50,
                "time_picking_planned": 12.50,
            }
        )

        round_itinerary = self.env["round.itinerary"].create(
            {
                "sequence": 100,
                "name": "Test itinerary",
                "code": "TEST1",
                "template_ids": [(6, 0, [round_template.id])],
                "partner_position_ids": [
                    (0, 0, {"sequence": 1, "partner_id": self.partner.id})
                ],
            }
        )

        self.round = self.env["round.instance"].create(
            {
                "template_id": round_template.id,
                "date": fields.Date.today(),
                "time_leave_planned": 12.50,
                "time_picking_planned": 12.50,
                "itinerary_ids": [(6, 0, [round_itinerary.id])],
            }
        )

        self.parent_location = location_obj.create(
            {"name": "G", "location_id": self.env.ref("stock.stock_location_stock").id}
        )

        self.pick_type = self.env["stock.picking.type"].search(
            [("code", "=", "outgoing")], limit=1
        )
        self.pick_type.subcode = "PICK"

        # Create additional product and update the available quantity (15)
        self.additional_product = self.env["product.product"].create(
            {
                "name": "Additional product",
                "default_code": "987654321",
                "tracking": "lot",
                "list_price": 20,
                "type": "product",
            }
        )

        location_add_product = location_obj.create(
            {
                "name": "GAA320",
                "kind": "bin",
                "zone": "G",
                "corridor": "A",
                "shelf": "A",
                "height": "3",
                "box": "30",
                "location_id": self.parent_location.id,
                "bin_checksum_1": "123",
                "bin_checksum_2": "123",
            }
        )
        self.env["stock.location"]._parent_store_compute()

        one_year = datetime.now() + relativedelta(years=1)
        lot_additional_product = self.env["stock.production.lot"].create(
            {
                "name": "000000001",
                "product_id": self.additional_product.id,
                "life_date": fields.Datetime.to_string(one_year),
            }
        )
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.additional_product.id,
                "product_tmpl_id": self.additional_product.product_tmpl_id.id,
                "new_quantity": 15,
                "lot_id": lot_additional_product.id,
                "location_id": location_add_product.id,
            }
        )
        update_qty_wizard.change_product_qty()

        # Create main product linked to the additional product with quanity 20

        product_uom_id = self.env.ref("product.product_uom_unit").id
        self.main_product = self.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "tracking": "lot",
                "list_price": 100,
                "type": "product",
                "additional_product_id": self.additional_product.id,
                "product_uom": product_uom_id,
                "ratio_main_product": 2,
                "ratio_additional_product": 1,
            }
        )

        location_product_1 = location_obj.create(
            {
                "name": "GAA210",
                "kind": "bin",
                "zone": "G",
                "corridor": "A",
                "shelf": "A",
                "height": "2",
                "box": "10",
                "location_id": self.parent_location.id,
                "bin_checksum_1": "123",
                "bin_checksum_2": "123",
            }
        )
        self.env["stock.location"]._parent_store_compute()

        one_year = datetime.now() + relativedelta(years=1)
        lot_product_1 = self.env["stock.production.lot"].create(
            {
                "name": "000000001",
                "product_id": self.main_product.id,
                "life_date": fields.Datetime.to_string(one_year),
            }
        )
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.main_product.id,
                "product_tmpl_id": self.main_product.product_tmpl_id.id,
                "new_quantity": 100,
                "lot_id": lot_product_1.id,
                "location_id": location_product_1.id,
            }
        )
        update_qty_wizard.change_product_qty()

    def test_prepare_pack_ops_1(self):
        """
        Test the method _prepare_pack_ops
        We have 100 units of main product
        and 15 units of additional product.

        On the main product, we set the additional product with a ratio 2/1
        (for 2 products, 1 given).

        We will create 3 pickings with 20 units of main product.
        According the ratio, we need 10 units of additional product.

        In the first case, we have 15 units in stocks dus we can take
        10 units of additional product.
        In the second case, we left 5 units in stocks dus we can only take
        5 units of additional product.
        In the last case, the stock of additional product is empty.
        :return:
        """

        location_id = self.env.ref("stock.stock_location_stock").id
        location_dest_id = self.env.ref("stock.stock_location_customers").id
        product_uom_id = self.env.ref("product.product_uom_unit").id

        # Picking 1
        # Stock additional product: 15.0
        tomorrow = datetime.now() + relativedelta(days=1)
        picking_1 = (
            self.env["stock.picking"]
            .create(
                {
                    "partner_id": self.partner.id,
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                    "min_date": fields.Datetime.to_string(tomorrow),
                    "picking_type_id": self.pick_type.id,
                    "delivery_round_id": self.round.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": "Test medoc 1",
                                "product_id": self.main_product.id,
                                "product_uom_qty": 20,
                                "product_uom": product_uom_id,
                            },
                        )
                    ],
                }
            )
            .with_context(round_autoset=False)
        )
        picking_1.action_confirm()
        picking_1.action_assign()
        self.assertEqual(len(picking_1.move_lines), 2)
        main_line = picking_1.move_lines.filtered(
            lambda line: line.product_id == self.main_product
        )
        self.assertEqual(main_line.product_uom_qty, 20.0)
        add_line = picking_1.move_lines.filtered(
            lambda line: line.product_id == self.additional_product
        )
        self.assertEqual(add_line.product_uom_qty, 10.0)

        # Picking 2
        # Stock additional product: 5.0
        picking_2 = (
            self.env["stock.picking"]
            .create(
                {
                    "partner_id": self.partner.id,
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                    "min_date": fields.Datetime.to_string(tomorrow),
                    "picking_type_id": self.pick_type.id,
                    "delivery_round_id": self.round.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": "Test medoc 1",
                                "product_id": self.main_product.id,
                                "product_uom_qty": 20,
                                "product_uom": product_uom_id,
                            },
                        )
                    ],
                }
            )
            .with_context(round_autoset=False)
        )
        picking_2.action_confirm()
        picking_2.action_assign()
        self.assertEqual(len(picking_2.move_lines), 2)
        main_line = picking_2.move_lines.filtered(
            lambda line: line.product_id == self.main_product
        )
        self.assertEqual(main_line.product_uom_qty, 20.0)
        add_line = picking_2.move_lines.filtered(
            lambda line: line.product_id == self.additional_product
        )
        self.assertEqual(add_line.product_uom_qty, 5.0)

        # Picking 3
        # Stock additional product: 0
        picking_3 = (
            self.env["stock.picking"]
            .create(
                {
                    "partner_id": self.partner.id,
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                    "min_date": fields.Datetime.to_string(tomorrow),
                    "picking_type_id": self.pick_type.id,
                    "delivery_round_id": self.round.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": "Test medoc 1",
                                "product_id": self.main_product.id,
                                "product_uom_qty": 20,
                                "product_uom": product_uom_id,
                            },
                        )
                    ],
                }
            )
            .with_context(round_autoset=False)
        )
        picking_3.action_confirm()
        picking_3.action_assign()
        # The system will not create a new line
        self.assertEqual(len(picking_3.move_lines), 1)
        main_line = picking_3.move_lines.filtered(
            lambda line: line.product_id == self.main_product
        )
        self.assertEqual(main_line.product_uom_qty, 20.0)

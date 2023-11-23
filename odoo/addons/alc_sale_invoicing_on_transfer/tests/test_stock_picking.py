# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.tests.common import trap_jobs


class TestStockPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "invoicing_mode": "at_shipping"}
        )

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "TST",
            }
        )

        # Create product and update the available quantity (°°)
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "default_code": "1234567",
                "list_price": 100,
                "type": "product",
            }
        )
        cls.sale_order = cls._confirm_sale_order()

    @classmethod
    def _confirm_sale_order(cls, partner=None, product=None, qty=1):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.product
        warehouse = cls.warehouse_1
        sale_model = cls.env["sale.order"]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": [
                Command.create(
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "price_unit": 50,
                    },
                )
            ],
        }
        so = sale_model.create(so_values)
        so.action_confirm()
        return so

    @classmethod
    def _create_and_deliver_picking(cls, sale):
        pick = sale.mapped("picking_ids")
        for move in pick.move_ids:
            move.quantity_done = move.product_qty
        pick._action_done()

    def test_00(self):
        """
        Data:

            A so ready to be delivered
            Picking type out configured to create the invoice on transfer
        Test Case:
            Deliver the SO (process the picking)
        Expected Result:
            A new invoice is created
        """
        self.warehouse_1.out_type_id.create_invoice_on_transfer = True
        self.assertFalse(self.sale_order.invoice_ids)
        with trap_jobs() as trap:
            self._create_and_deliver_picking(self.sale_order)
            trap.assert_enqueued_job(self.sale_order.picking_ids._invoicing_at_shipping)
            self.assertFalse(self.sale_order.invoice_ids)
            trap.perform_enqueued_jobs()
            self.assertTrue(self.sale_order.invoice_ids)

    def test_01(self):
        """
        Data:

            A so ready to be delivered
            Picking type out configured to not create the invoice on transfer
        Test Case:
            Deliver the SO (process the picking)
        Expected Result:
            No invoice created
        """
        self.warehouse_1.out_type_id.create_invoice_on_transfer = False
        self.assertFalse(self.sale_order.invoice_ids)
        self._create_and_deliver_picking(
            self.sale_order.with_context(queue_job__no_delay=True)
        )
        self.assertFalse(self.sale_order.invoice_ids)

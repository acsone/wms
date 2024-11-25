# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import uuid

from odoo.fields import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestStockDeliveryNote(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "5173360",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_vet_belges"
                ).id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.p1, cls.env.ref("stock.stock_location_stock"), 100
        )
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
        cls.customer_csv_only = cls.partner.copy(
            {"send_pdf_deliveryship": False, "send_csv_deliveryship": True}
        )

        cls.customer_pdf_only = cls.partner.copy(
            {"send_pdf_deliveryship": True, "send_csv_deliveryship": False}
        )

        cls.so_csv, cls.picking_csv = cls._create_and_transfer_picking(
            partner=cls.customer_csv_only, lot_name="20170102"
        )
        cls.operation = cls.env.ref("rma.rma_operation_replace")
        cls.operation.action_create_delivery = "automatic_on_confirm"

    @classmethod
    def _create_and_transfer_picking(cls, partner, product=None, lot_name=None):
        lot_name = lot_name or str(uuid.uuid1())
        if product is None:
            product = cls.p1
        so = cls.env["sale.order"].create(
            {
                "partner_id": partner.id,
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
                        },
                    )
                ],
            }
        )
        so.action_confirm()
        picking = so.picking_ids
        picking.customer_id = partner
        picking.action_assign()

        lot = cls.env["stock.lot"].create(
            {
                "expiration_date": "2017-01-31 10:00:00",
                "name": lot_name,
                "product_qty": 10,
                "product_id": product.id,
                "company_id": cls.env.user.company_id.id,
            },
        )
        lines = picking.move_line_ids
        lines.write({"lot_id": lot.id, "qty_done": 10})
        # use context to avoid wizards
        picking.with_context(skip_sms=True, skip_expired=True).button_validate()
        return so, picking

    def _create_rma(self, picking):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking_form.create_rma = True
        stock_return_picking_form.rma_operation_id = self.operation
        return_wizard = stock_return_picking_form.save()
        return_wizard.create_returns()
        return picking.move_ids.rma_ids

    def test_00(self):
        """Check the csv is generated for rma delivery."""
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_csv.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.name.endswith(".csv"))
        rmas = self._create_rma(self.picking_csv)
        rma_delivery_picking = rmas.delivery_move_ids.picking_id
        rma_delivery_picking.action_set_quantities_to_reservation()
        rma_delivery_picking._action_done()
        moves = rma_delivery_picking._delivery_slip_moves(False)
        self.assertEqual(len(moves), 1)

    def test_01(self):
        """Check the csv is not generated for rma delivery if the operation is set to.

        ignore the csv sent
        """
        self.operation.no_csv_delivery_slip = True
        attachments = self.env["ir.attachment"].search(
            [("res_id", "=", self.picking_csv.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertTrue(attachments.name.endswith(".csv"))
        rmas = self._create_rma(self.picking_csv)
        rma_delivery_picking = rmas.delivery_move_ids.picking_id
        rma_delivery_picking.action_set_quantities_to_reservation()
        rma_delivery_picking._action_done()
        moves = rma_delivery_picking._delivery_slip_moves(False)
        self.assertEqual(len(moves), 0)

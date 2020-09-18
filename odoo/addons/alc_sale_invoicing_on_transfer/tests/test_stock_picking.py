# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.queue_job.job import Job
from odoo.tests.common import SavepointCase


class TestStockPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, test_queue_job_no_delay=True
            )
        )
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
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
                "tracking": "none",
                "list_price": 100,
                "type": "product",
            }
        )
        cls.sale_order = cls._confirm_sale_order()

    def filter(self, record):
        return 0

    def setUp(self):
        super(TestStockPicking, self).setUp()

        # mute logger
        loggers = ["odoo.addons.queue_job.models.base"]
        for logger in loggers:
            logging.getLogger(logger).addFilter(self)

        @self.addCleanup
        def un_mute_logger():
            for logger_ in loggers:
                logging.getLogger(logger_).removeFilter(self)

    @classmethod
    def _confirm_sale_order(cls, partner=None, product=None, qty=1):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.product
        warehouse = cls.warehouse_1
        Sale = cls.env["sale.order"]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "product_uom": cls.env.ref("product.product_uom_unit").id,
                        "price_unit": 50,
                    },
                )
            ],
        }
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    @classmethod
    def _create_and_deliver_picking(cls, sale):
        pick = sale.mapped("picking_ids")
        pick.force_assign()
        for pack in pick.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick.do_new_transfer()

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
        self._create_and_deliver_picking(self.sale_order)
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
        self._create_and_deliver_picking(self.sale_order)
        self.assertFalse(self.sale_order.invoice_ids)

    def test_02(self):
        """
        Data:
            A so ready to be delivered
            Picking type out configured to create the invoice on transfer
            Delay of queue job
        Test Case:
            1 Deliver the SO (process the picking)
            2 Create the invoice
            3 Process job queue
        Expected Result:
            1 No invoice created
            2 invoice created
            3 job processed without error
        """
        QueueJob = self.env["queue.job"]
        sale_order = self.sale_order.with_context(test_queue_job_no_delay=False)
        self.warehouse_1.out_type_id.create_invoice_on_transfer = True
        self.assertFalse(sale_order.invoice_ids)
        existing_jobs = QueueJob.search([])
        self._create_and_deliver_picking(sale_order)
        invoice_job = QueueJob.search([]) - existing_jobs
        self.assertTrue(invoice_job)
        # no invoice created on deliver
        self.assertFalse(sale_order.invoice_ids)
        sale_order.action_invoice_create()
        # invoice created manually
        self.assertTrue(sale_order.invoice_ids)
        # process the job
        job = Job.load(self.env, invoice_job.uuid)
        job.perform()

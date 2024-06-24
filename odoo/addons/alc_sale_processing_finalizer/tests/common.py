# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from freezegun import freeze_time

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestSaleProcessingFinalizerComon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env["res.config.settings"].create(
            {
                "send_processing_finalizer_email": False,
            }
        ).execute()
        today = datetime.date.today()
        with freeze_time(today - datetime.timedelta(days=100)):
            cls.warehouse_1 = cls.env.ref("stock.warehouse0")
            cls.warehouse_1.write(
                {
                    "name": "Test Warehouse",
                    "reception_steps": "one_step",
                    "delivery_steps": "pick_ship",
                    "code": "BWH",
                }
            )
            cls.SaleOrder = cls.env["sale.order"]
            cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})
            cls.p1 = cls.env["product.product"].create(
                {"name": "Unittest P1", "type": "product"}
            )
            cls.p2 = cls.env["product.product"].create(
                {"name": "Unittest P2", "type": "product"}
            )
            cls.p3 = cls.env["product.product"].create(
                {"name": "P3", "type": "product"}
            )
            cls.p4 = cls.env["product.product"].create(
                {"name": "P4", "type": "product"}
            )
            cls.env["stock.quant"]._update_available_quantity(
                cls.p4, cls.env.ref("stock.stock_location_stock"), 10
            )
            cls.so_after_3months_to_purge = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "warehouse_id": cls.warehouse_1.id,
                    "order_line": [
                        Command.create(
                            {
                                "name": cls.p1.name,
                                "product_id": cls.p1.id,
                                "product_uom_qty": 2,
                                "product_uom": cls.p1.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                    ],
                }
            )
            cls.so_draft_auto_finalize = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "warehouse_id": cls.warehouse_1.id,
                    "order_line": [
                        Command.create(
                            {
                                "name": cls.p3.name,
                                "product_id": cls.p3.id,
                                "product_uom_qty": 1,
                                "product_uom": cls.p3.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                    ],
                }
            )
            cls.so_after_3months_to_keep = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "warehouse_id": cls.warehouse_1.id,
                    "auto_finalize_processing": False,
                    "order_line": [
                        Command.create(
                            {
                                "name": cls.p2.name,
                                "product_id": cls.p2.id,
                                "product_uom_qty": 6,
                                "product_uom": cls.p2.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                    ],
                }
            )
            cls.so_after_3months_to_purge.action_confirm()
            cls.so_after_3months_to_purge.action_done()  # lock the so
            cls.so_after_3months_to_keep.action_confirm()
            cls.so_after_3months_to_keep.action_done()  # lock the so
        cls.so_auto_finalize = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p4.name,
                            "product_id": cls.p4.id,
                            "product_uom_qty": 7,
                            "product_uom": cls.p4.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so_auto_finalize.action_confirm()
        cls.so_auto_finalize.action_done()

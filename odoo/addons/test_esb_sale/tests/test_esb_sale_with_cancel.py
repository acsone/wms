# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from copy import deepcopy

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import BaseCommon


class TestSaleController(BaseCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setup_records()
        cls.order_data = {
            "increment_id": "INC-ID",
            "customer_id": cls.partner.ref,
            "date": "2017-09-18",
            "order_ref": "refClt",
            "lines": [
                {"line_id": "1", "sku": "0001", "quantity": 3, "free": False},
                {
                    # free line: to be skipped
                    "line_id": "2",
                    "sku": "FOO",
                    "quantity": 3,
                    "free": True,
                },
            ],
        }
        cls.order_data_cnk = {
            "increment_id": "INC-ID",
            "customer_id": cls.partner.ref,
            "date": "2017-09-18",
            "order_ref": "refClt",
            "lines": [{"line_id": "1", "cnk": "00999", "quantity": 3, "free": False}],
        }
        cls.request_data = {
            "jsonrpc": "3.0",
            "id": "4321",
            "method": "create",
            "params": {"data": cls.order_data},
        }

    @classmethod
    def setup_records(cls):
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "default_code": "0001",
                "cnk_code": "00999",
                "list_price": 10.0,
            }
        )
        cls.delivery_product = cls.env["product.product"].create(
            {"name": "Delivery", "default_code": "DELIVERY"}
        )
        cls.delivery_1 = cls.env["delivery.carrier"].create(
            {
                "delivery_type": "fixed",
                "name": "delivery carrier 1",
                "esb_ref": "031",
                "product_id": cls.delivery_product.id,
            }
        )
        cls.payment_30_net = cls.env.ref("account.account_payment_term_30days")
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "John Doe",
                "ref": "111111",
                "property_delivery_carrier_id": cls.delivery_1.id,
                "supplier_promotion_sale_allowed": True,
                "property_payment_term_id": cls.payment_30_net.id,
            }
        )
        cls.partner_shipping = cls.env["res.partner"].create(
            {
                "name": "John Doe (ship)",
                "ref": "58020388759284",
                "type": "delivery",
                "street": "Middle street 2",
                "city": "Some Island",
                "zip": "7492125",
                "parent_id": cls.partner.id,
            }
        )
        cls.partner_newpharma = cls.env["res.partner"].create(
            {
                "name": "newpharam",
                "ref": cls.env["res.partner"].newpharma_refs[0],
                "property_delivery_carrier_id": cls.delivery_1.id,
                "supplier_promotion_sale_allowed": True,
                "property_payment_term_id": cls.payment_30_net.id,
                "auto_cancel_unavailable_qty_sold": True,
                "sale_reason_backorder_strategy": "cancel",
            }
        )
        cls.pricelist_1 = cls.env["product.pricelist"].create(
            {
                "name": "Pricelist 1",
                "item_ids": [
                    (
                        0,
                        False,
                        {
                            "applied_on": "0_product_variant",
                            "product_id": cls.p1.id,
                            "compute_price": "fixed",
                            "fixed_price": 9,
                        },
                    )
                ],
            }
        )

    @freeze_time("2017-09-18 11:30:20")
    def test_create_saleorder(self):
        """
        Set properties on NewPharma partner:

            - auto_cancel_unavailable_qty_sold : This will cancel the ordered quantity if unavailable at confirm
            - sale_reason_backorder_strategy-> cancel : This will lead to a sale exception

        In this case, an exception present on sale order line will lead to set
        the ordered quantity -> 0

        Check that no picking will be created.
        """
        starting_date = fields.Datetime().now()
        data = deepcopy(self.order_data)
        data["num_suite"] = "iamsuitename"
        data["customer_id"] = self.partner_newpharma.ref
        order = self.env["sale.order"]._ws_create_new(data, starting_date)
        self.assertFalse(order.picking_ids)

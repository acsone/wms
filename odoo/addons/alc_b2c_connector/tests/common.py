# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random
import string
from functools import partial

from odoo import Command

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase
from odoo.addons.fastapi.dependencies import (
    authenticated_partner_impl as base_authenticated_partner_impl,
    fastapi_endpoint_id,
)

from ..dependencies import authenticated_partner_impl
from ..hooks import _initialize_product_assortment_filter


class CommonB2CServiceCase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _initialize_product_assortment_filter(cls.env.cr)
        cls.currency_id = cls.env.user.company_id.currency_id
        cls.pricelist_id = cls.env.ref(
            "alc_product_pricelist_data.product_pricelist_pb1"
        )
        # ensure same currency across products and pricelists
        cls.pricelist_id.currency_id = cls.currency_id
        cls.ProductProduct = cls.env["product.product"]
        # disable all products
        cls.ProductProduct.search([]).mapped("orderpoint_ids").write({"active": False})
        cls.ProductProduct.search([]).write({"active": False})
        cls.env.ref("alc_b2c_connector.alc_b2c_rest_api_user").email = "test@test.be"
        cls.env["stock.location"]._parent_store_compute()
        cls.env["product.category"]._parent_store_compute()

        # create specific taxes
        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "type_tax_use": "sale",
            }
        )
        cls.tax_6_percent = cls.env["account.tax"].create(
            {
                "name": "Tax 6%",
                "amount": 6.0000,
                "amount_type": "percent",
                "type_tax_use": "sale",
            }
        )
        # create products
        cls.saleable_product = cls.ProductProduct.create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0001",
                "default_code": "12345",
                "cnk_code": "CNK123",
                "taxes_id": [(6, False, [cls.tax_6_percent.id])],
            }
        )
        cls.change_product_qty(cls.saleable_product, 5)
        cls.saleable_product_2 = cls.ProductProduct.create(
            {
                "name": "Product 2",
                "sale_ok": True,
                "type": "product",
                "list_price": 20,
                "barcode": "XXX0002",
                "default_code": "23456",
                "cnk_code": "CNK234",
                "taxes_id": [(6, False, [cls.tax_fixed.id])],
            }
        )
        cls.change_product_qty(cls.saleable_product_2, 110)
        cls.not_saleable_product = cls.ProductProduct.create(
            {
                "name": "Product 3",
                "sale_ok": False,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0003",
                "default_code": "34567",
            }
        )
        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Inbound payment mode",
                "company_id": cls.env.ref("base.main_company").id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "payment_type": "inbound",
            }
        )
        cls.b2c_user = cls.env.ref("alc_b2c_connector.alc_b2c_rest_api_user")
        cls.sale_channel = cls.env.ref("sale_channel.sale_channel_amazon")
        cls.sale_channel2 = cls.env.ref("sale_channel.sale_channel_ebay")
        cls.endpoint = cls.env.ref("alc_b2c_connector.fastapi_endpoint_b2c")
        cls.endpoint.user_id = cls.b2c_user
        cls.b2c_client = cls.env["alc.b2c.client"].create(
            {
                "name": "B2c backend test",
                "product_assortment_id": cls.env.ref(
                    "alc_b2c_connector.b2c_product_assortment_filter"
                ).id,
                "pricelist_id": cls.pricelist_id.id,
                "sale_team_id": cls.env.ref("sales_team.salesteam_website_sales").id,
                "payment_mode_id": cls.payment_mode.id,
                "sale_channel_id": cls.sale_channel.id,
                "sale_reason_backorder_strategy": "cancel",
                "api_key": "1234",
                "partner_id": cls.b2c_user.partner_id.id,
                "fastapi_endpoint_id": cls.endpoint.id,
            }
        )
        # disable sale exceptions
        cls.env["ir.config_parameter"].set_param(
            "alc_sale_exception_settings.sale_exception_check_enabled", False
        )
        # cls.default_fastapi_authenticated_partner = cls.b2c_user.partner_id
        cls.default_fastapi_odoo_env = cls.env(
            user=cls.b2c_user, context=dict(cls.env.context)
        )
        cls.default_fastapi_dependency_overrides = {
            base_authenticated_partner_impl: authenticated_partner_impl,
            fastapi_endpoint_id: partial(lambda a: a, cls.endpoint.id),
        }

    @classmethod
    def change_product_qty(cls, product, qty):
        cls.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": qty,
            }
        ).change_product_qty()


class CommonB2CSaleServiceCase(CommonB2CServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("product.group_discount_per_so_line")
        # create a b2c_partner
        cls.b2c_partner = cls.env["res.partner"].create(
            {
                "name": "EXISTING B2C PARTNER",
                "is_b2c_customer": True,
                "partner_type": "student_like",
                "ref": f"{cls.sale_channel.name}_ABC",
                "email": "b2c@b2c.be",
                "alc_b2c_client_id": cls.b2c_client.id,
            }
        )

        # create a specific payment mode for the VT
        cls.vt_payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Specific VT payment mode",
                "company_id": cls.env.ref("base.main_company").id,
                "bank_account_link": "variable",
                "payment_method_id": cls.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "payment_type": "inbound",
            }
        )

        # create a vete
        cls.vt_partner = cls.env["res.partner"].create(
            {
                "name": "VT",
                "partner_type": "veterinary",
                "ref": f"{cls.sale_channel.name}_VTREF",
                "email": "vt@vt.be",
                "supplier_promotion_sale_allowed": True,
                "customer_payment_mode_id": cls.vt_payment_mode.id,
            }
        )
        cls.SaleOrder = cls.env["sale.order"]
        cls.payment_term_test = cls.env.ref(
            "account.account_payment_term_advance"
        ).copy()
        cls.b2c_client.payment_term_id = cls.payment_term_test

    @classmethod
    def _gen_string(cls, length=10):
        return "".join(random.choice(string.ascii_letters) for _ in range(length))

    @classmethod
    def _gen_recipent(cls, _id=None, title="mr"):
        _id = _id or cls._gen_string()
        return {
            "id": _id,
            "title": title,
            "last_name": cls._gen_string(),
            "first_name": cls._gen_string(),
            "street": cls._gen_string(),
            "street2": cls._gen_string(),
            "zip": cls._gen_string(),
            "city": cls._gen_string(),
            "email": cls._gen_string(),
            "phone": cls._gen_string(),
            "mobile": cls._gen_string(),
            "name2": cls._gen_string(),
        }

    def setUp(self):
        super().setUp()
        # create a b2c sale_order
        self.b2c_order = self.env["sale.order"].create(
            {
                "alc_b2c_client_id": self.b2c_client.id,
                "b2c_ref": 10,
                "partner_id": self.b2c_partner.id,
                "partner_invoice_id": self.vt_partner.id,
                "partner_shipping_id": self.vt_partner.id,
                "pricelist_id": self.pricelist_id.id,
                "order_line": [
                    Command.create(
                        {
                            "b2c_ref": 1,
                            "product_id": self.saleable_product.id,
                            "name": self.saleable_product.name,
                            "product_uom": self.saleable_product.uom_id.id,
                            "product_uom_qty": 10,
                        },
                    )
                ],
                "sale_channel_id": self.sale_channel.id,
            }
        )

    def _get_so_from_name(self, name):
        return self.SaleOrder.search([("name", "=", name)])

    def _do_picking(self, picking):
        for move in picking.move_ids:
            move.quantity_done = move.product_qty
        picking._action_done()

    def _deliver_orders(self, orders):
        for order in orders:
            # validate SO
            order.action_confirm()
            # process deliveries
            picking_internals = order.picking_ids.filtered(
                lambda p: p.picking_type_code == "internal"
            )
            picking_outs = order.picking_ids.filtered(
                lambda p: p.picking_type_code == "outgoing"
            )
            for picking in picking_internals:
                self._do_picking(picking)
                self.assertEqual(picking.state, "done")
            for picking in picking_outs:
                self._do_picking(picking)
                self.assertEqual(picking.state, "done")

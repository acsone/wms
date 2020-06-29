# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import SavepointComponentCase

from ..hooks import _initialize_product_assortment_filter
from ..services.base_b2c_service import B2C_COLLECTION


class CommonCase(SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(CommonCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        _initialize_product_assortment_filter(cls.env.cr)
        cls.ProductProduct = cls.env["product.product"]
        # disable all products
        cls.ProductProduct.search([]).mapped("orderpoint_ids").write({"active": False})
        cls.ProductProduct.search([]).write({"active": False})
        cls.env["stock.location"]._parent_store_compute()
        cls.env["product.category"]._parent_store_compute()
        cls.saleable_product = cls.ProductProduct.create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0001",
                "default_code": "12345",
                "cnk_code": "CNK123",
            }
        )
        cls.not_saleable_product = cls.ProductProduct.create(
            {
                "name": "Product 2",
                "sale_ok": False,
                "type": "product",
                "list_price": 10,
                "barcode": "XXX0002",
                "default_code": "23456",
            }
        )
        cls.change_product_qty(cls.saleable_product, 5)
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
        cls.b2c_backend = cls.env["alc.b2c.backend"].create(
            {
                "name": "B2c backend test",
                "product_assortment_id": cls.env.ref(
                    "alc_b2c_connector.b2c_product_assortment_filter"
                ).id,
                "pricelist_id": cls.env.ref(
                    "alc_b2c_connector.product_pricelist_b2c"
                ).id,
                "sale_team_id": cls.env.ref("sales_team.salesteam_website_sales").id,
                "payment_mode_id": cls.payment_mode.id,
                "sale_channel": "web",
            }
        )

    @classmethod
    def change_product_qty(cls, product, qty):
        cls.env["stock.change.product.qty"].create(
            {"product_id": product.id, "new_quantity": qty}
        ).change_product_qty()

    @classmethod
    @contextmanager
    def work_on_services(cls, **params):
        params = params or {}
        ctx = cls.env["res.users"].sudo(
            cls.env.ref("alc_b2c_connector.alc_b2c_rest_api_user").id
        )
        if "b2c_backend" not in params:
            params["b2c_backend"] = cls.b2c_backend
        collection = _PseudoCollection(B2C_COLLECTION, ctx.env)
        yield WorkContext(
            model_name="rest.service.registration", collection=collection, **params
        )

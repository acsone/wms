# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import SavepointComponentCase

from ..hooks import _initialize_product_assortment_filter
from ..services.base_chronovet_service import CHRONOVET_COLLECTION


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
        cls.chronovet_backend = cls.env["alc.chronovet.backend"].get_singleton()

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
            cls.env.ref("alc_chronovet_connector.alc_chronovet_rest_api_user").id
        )
        if "chronovet_backend" not in params:
            params["chronovet_backend"] = ctx.env.ref(
                "alc_chronovet_connector.alc_chronovet_backend"
            )
        collection = _PseudoCollection(CHRONOVET_COLLECTION, ctx.env)
        yield WorkContext(
            model_name="rest.service.registration", collection=collection, **params
        )

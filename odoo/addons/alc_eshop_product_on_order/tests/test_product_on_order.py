# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock
from freezegun import freeze_time
from werkzeug.exceptions import NotFound

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestProductOnOrder(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestProductOnOrder, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()
        cls.env["stock.location"].search([])._parent_store_compute()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.inventory_model = cls.env["stock.inventory"]
        cls.inventory_line_model = cls.env["stock.inventory.line"]
        cls.product_ali = cls.env["product.product"].create(
            {
                "name": "product_ali",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("alc_product_category_data.product_categ_ali").id,
            }
        )
        cls.product_medoc = cls.env["product.product"].create(
            {
                "name": "product_medoc",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("alc_product_category_data.product_categ_medoc").id,
            }
        )
        cls.product_mto = cls.env["product.product"].create(
            {
                "name": "product_medoc",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("alc_product_category_data.product_categ_materiel").id,
                "route_ids": [(6, 0, cls.env.ref("stock.route_warehouse0_mto").ids)],
            }
        )

        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner_2"})

        # put qty for medoc...
        cls._add_product_qty(cls.product_medoc, 4)
        # We create 3 SO
        # 1 for product with stock
        # 1 for product out of stock
        # 1 for MTO
        cls.so_medoc_in_stock = cls.sell(cls.product_medoc, 2, "2020-01-01 14:00:00")
        cls.so_ali_out_of_stock = cls.sell(cls.product_ali, 3, "2020-01-02 14:00:00")
        cls.so_mto = cls.sell(cls.product_mto, 3, "2020-01-03 14:00:00")

    @classmethod
    def _add_product_qty(cls, product, quantity):
        wiz = cls.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": quantity,
                "location_id": cls.stock_location.id,
            }
        )
        wiz.change_product_qty()

    @classmethod
    def sell(cls, product, qty, ttime, confirm=True, deliver=False):
        with freeze_time(ttime):
            so = cls.env["sale.order"].create(
                {
                    "partner_id": cls.partner_1.id,
                    "sale_channel": "web",
                    "date_order": ttime,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom": product.uom_id.id,
                                "product_uom_qty": qty,
                            },
                        )
                    ],
                }
            )
            if confirm or deliver:
                so.action_confirm()
            if deliver:
                so.picking_ids.action_confirm()
                so.picking_ids.action_done()
        return so

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

    @classmethod
    @contextmanager
    def products_on_order_service(cls, authenticated_partner_id):
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
        )
        yield work.component(usage="products_on_order")

    def test_simple_search(self):
        """Check simple call.

        We should have 3 products since we have 3 WIP so
        """

        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search()
            self.assertEqual(3, res["size"])

    def test_search_mto(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search(restricts=["is_mto"])
            self.assertEqual(1, res["size"])

    def test_search_has_backorder(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search(restricts=["has_backorder"])
            self.assertEqual(2, res["size"])

    def test_search_family(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search(product_families=["meds"])
            self.assertEqual(1, res["size"])
            res = service.search(product_families=["food"])
            self.assertEqual(1, res["size"])
            res = service.search(product_families=["meds", "food"])
            self.assertEqual(2, res["size"])

    def test_search_order_ref(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search(order_ref=self.so_medoc_in_stock.name)
            self.assertEqual(1, res["size"])

    def test_search_customer_ref(self):
        customer_ref = "my_ref"
        self.so_medoc_in_stock.client_order_ref = customer_ref
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search(customer_ref=customer_ref)
            self.assertEqual(1, res["size"])

    def test_search_date_order(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.search(
                order_date_min="2020-01-03 13:00:00",
                order_date_max="2020-01-03 15:00:00",
            )
            self.assertEqual(1, res["size"])

    def test_cancel_wrong_ref(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.cancel(order_line_id=-1, params={"quantity": 1})
            self.assertEqual(False, res["status"])

    def test_cancel_no_back_order(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.cancel(
                order_line_id=self.so_medoc_in_stock.order_line.id, quantity=1,
            )
            self.assertEqual(False, res["status"])

    def test_cancel(self):
        template = self.env.ref(
            "alc_eshop_product_on_order.sale_order_request_backorder_cancellation"
        )
        template.auto_delete = False

        all_mails = self.env["mail.mail"].search([])
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.cancel(
                order_line_id=self.so_ali_out_of_stock.order_line.id, quantity=1,
            )
            self.assertTrue(res["status"])
        new_mail = self.env["mail.mail"].search([]) - all_mails
        self.assertTrue(new_mail)
        self.assertEqual(self.so_ali_out_of_stock.id, new_mail.res_id)
        self.assertEqual(self.so_ali_out_of_stock._name, new_mail.model)

    def test_get(self):
        with self.products_on_order_service(self.partner_1.id) as service:
            res = service.get(order_line_id=self.so_ali_out_of_stock.order_line.id,)
            self.assertTrue(res)

    def test_get_not_found(self):
        with self.products_on_order_service(
            self.partner_1.id
        ) as service, self.assertRaises(NotFound):
            service.get(order_line_id=123459876,)

# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import fields

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import products_on_order_router


class TestProductOnOrder(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = products_on_order_router
        # disable others products
        cls.env["product.product"].search([]).write({"active": False})
        cls.env["stock.location"].search([])._parent_store_compute()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.product_ali = cls.env["product.product"].create(
            {
                "name": "product_ali",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("alc_product_food.product_categ_ali").id,
            }
        )
        cls.product_medoc = cls.env["product.product"].create(
            {
                "name": "product_medoc",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_medoc"
                ).id,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_mto.active = True
        cls.warehouse.mto_pull_id.procure_method = "make_to_stock"
        cls.product_mto = cls.env["product.product"].create(
            {
                "name": "product_medoc",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_materiel"
                ).id,
                "route_ids": [(6, 0, cls.route_mto.ids)],
            }
        )
        cls.mto_vendor = cls.env["res.partner"].create({"name": "mto_vendor"})
        # search product with route mto
        cls.env["product.product"].search([("route_ids", "in", cls.route_mto.ids)])
        cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product_mto.product_tmpl_id.id,
                "partner_id": cls.mto_vendor.id,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product_medoc.product_tmpl_id.id,
                "partner_id": cls.mto_vendor.id,
            }
        )
        cls.env["product.supplierinfo"].create(
            {
                "product_tmpl_id": cls.product_ali.product_tmpl_id.id,
                "partner_id": cls.mto_vendor.id,
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
            }
        )
        wiz.change_product_qty()

    @classmethod
    def sell(cls, product, qty, ttime, confirm=True, deliver=False):
        with freeze_time(ttime):
            so = cls.env["sale.order"].create(
                {
                    "partner_id": cls.partner_1.id,
                    "sale_channel_id": cls.env.ref(
                        "alc_sale_channel.sale_channel_web"
                    ).id,
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
                so.picking_ids._action_done()
        return so

    def test_simple_search(self):
        """Check simple call.

        We should have 3 products since we have 3 WIP so
        """
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get("/products_on_order")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 3)

    def test_search_restricts(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"restricts[]": ["is_mto"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get(
                "/products_on_order", params={"restricts[]": ["has_backorder"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

            response = test_client.get(
                "/products_on_order",
                params={"restricts[]": ["has_backorder", "is_mto"]},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

    def test_search_family(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"product_families[]": ["meds"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

            response = test_client.get(
                "/products_on_order", params={"product_families[]": ["food"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)
            response = test_client.get(
                "/products_on_order", params={"product_families[]": ["meds", "food"]}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 2)

    def test_search_order_ref(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"order_ref": self.so_medoc_in_stock.name}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_search_customer_ref(self):
        customer_ref = "my_ref"
        self.so_medoc_in_stock.client_order_ref = customer_ref
        self.so_medoc_in_stock.flush_recordset()
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order", params={"customer_ref": customer_ref}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_search_date_order(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                "/products_on_order",
                params={
                    "order_date_min": fields.Datetime.to_datetime(
                        "2020-01-03 13:00:00"
                    ).isoformat(),
                    "order_date_max": fields.Datetime.to_datetime(
                        "2020-01-03 15:00:00"
                    ).isoformat(),
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["size"], 1)

    def test_cancel_wrong_ref(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                "/products_on_order/cancel/-1", json={"quantity": 1}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_cancel_no_back_order(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_medoc_in_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], False)

    def test_cancel(self):
        template = self.env.ref(
            "alc_eshop_api_products_on_order.sale_order_request_backorder_cancellation"
        )
        template.auto_delete = False

        all_mails = self.env["mail.mail"].search([])
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.post(
                f"/products_on_order/cancel/{self.so_ali_out_of_stock.order_line.id}",
                json={"quantity": 1},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], True)
        new_mail = self.env["mail.mail"].search([]) - all_mails
        subject = (
            f"Ref {self.so_ali_out_of_stock.name}: "
            "Demande annulation backorder product_ali"
        )
        self.assertTrue(new_mail)
        self.assertEqual(new_mail.subject, subject)
        self.assertEqual(self.so_ali_out_of_stock.id, new_mail.res_id)
        self.assertEqual(self.so_ali_out_of_stock._name, new_mail.model)

    def test_get(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get(
                f"/products_on_order/{self.so_ali_out_of_stock.order_line.id}"
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["order_line_id"], self.so_ali_out_of_stock.order_line.id
            )

    def test_get_not_found(self):
        with self._create_test_client(partner=self.partner_1) as test_client:
            response = test_client.get("/products_on_order/123456789")
            self.assertEqual(response.status_code, 404)

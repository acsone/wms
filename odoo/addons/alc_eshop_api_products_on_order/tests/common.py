# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.extendable_fastapi.tests.common import FastAPITransactionCase

from ..routers import products_on_order_router


class ProductOnOrderCase(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = products_on_order_router
        # disable others products
        if "loyalty.program" in cls.env:
            cls.env["loyalty.program"].search([]).toggle_active()
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

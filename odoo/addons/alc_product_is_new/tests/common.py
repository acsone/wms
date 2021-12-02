# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class ProductNewCharacteristicsCommonFeatures(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(ProductNewCharacteristicsCommonFeatures, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        storage_type_new = cls.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute"
        )
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.ResPartner = cls.env["res.partner"]
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product new",
                "sale_ok": True,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "default_code": "678911",
            }
        )
        cls.product_template2 = cls.product2.product_tmpl_id
        cls.product_template2.product_package_storage_type_id = storage_type_new.id

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest missing dimensions and barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.p1.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest missing dimensions and weight",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "barcode": "123456789",
            }
        )
        cls.p2.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest missing barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
            }
        )
        cls.p3.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p4 = cls.env["product.product"].create(
            {
                "name": "Unittest missing weight",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "barcode": "123456778",
            }
        )
        cls.p4.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p5 = cls.env["product.product"].create(
            {
                "name": "Unittest missing dimensions",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "barcode": "123456723",
            }
        )
        cls.p5.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p6 = cls.env["product.product"].create(
            {
                "name": "Unittest weight and barcode",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
            }
        )
        cls.p6.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p7 = cls.env["product.product"].create(
            {
                "name": "Unittest complete product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "length": 2.0,
                "width": 4.0,
                "height": 6.0,
                "weight": 10.0,
                "barcode": "2345678910",
            }
        )
        cls.p7.product_tmpl_id.product_package_storage_type_id = storage_type_new.id
        cls.p8 = cls.env["product.product"].create(
            {
                "name": "Unittest not new product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.products = [cls.p1, cls.p2, cls.p3, cls.p4, cls.p5, cls.p6, cls.p7, cls.p8]
        cls.supplier = cls.ResPartner.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.reception_location = cls.StockLocation.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "internal",
                "act_as_view": True,
            }
        )
        cls.bin1 = cls.StockLocation.create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls.picking = cls.StockPicking.create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "product_uom": product.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.reception_location.id,
                        },
                    )
                    for product in cls.products
                ],
            }
        )
        cls.picking.action_assign()

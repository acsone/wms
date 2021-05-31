# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import io

from PIL import Image

from .test_actions_data_base import ActionsDataDetailCaseBase


def fake_colored_image(color="#4169E1", size=(800, 500)):
    with io.BytesIO() as img_file:
        Image.new("RGB", size, color).save(img_file, "JPEG")
        img_file.seek(0)
        return base64.b64encode(img_file.read())


class TestActionsDataDetailCase(ActionsDataDetailCaseBase):
    def test_data_location(self):
        location = self.stock_location
        data = self.data_detail.location_detail(location)
        self.assert_schema(self.schema_detail.location_detail(), data)
        pack_operations = self.env["stock.pack.operation"].search(
            [
                ("location_id", "child_of", location.id),
                ("product_qty", ">", 0),
                ("state", "not in", ("done", "cancel")),
            ]
        )
        self.assertDictEqual(
            data,
            self._expected_location_detail(location, pack_operations=pack_operations),
        )

    def test_data_packaging(self):
        data = self.data_detail.packaging(self.packaging)
        self.assert_schema(self.schema_detail.packaging(), data)
        self.assertDictEqual(data, self._expected_packaging(self.packaging))

    def test_data_lot(self):
        lot = self.env["stock.production.lot"].create(
            {
                "product_id": self.product_b.id,
                "ref": "#FOO",
                "removal_date": "2020-05-20",
                "life_date": "2020-05-31",
            }
        )
        data = self.data_detail.lot_detail(lot)
        self.assert_schema(self.schema_detail.lot_detail(), data)

        expected = {
            "id": lot.id,
            "name": lot.name,
            "ref": "#FOO",
            "product": self._expected_product_detail(self.product_b, full=True),
        }
        # ignore time and TZ, we don't care here
        self.assertEqual(data.pop("removal_date").split(" ")[0], "2020-05-20")
        self.assertEqual(data.pop("expire_date").split(" ")[0], "2020-05-31")
        self.assertDictEqual(data, expected)

    def test_data_package(self):
        package = self.move_a.linked_move_operation_ids.operation_id.package_id
        package.packaging_id = self.packaging.id
        package.package_storage_type_id = self.storage_type_pallet
        # package.invalidate_cache()
        data = self.data_detail.package_detail(package, picking=self.picking)
        self.assert_schema(self.schema_detail.package_detail(), data)

        lines = self.env["stock.pack.operation"].search(
            [("package_id", "=", package.id), ("state", "not in", ("done", "cancel"))]
        )
        pickings = lines.mapped("picking_id")
        expected = {
            "id": package.id,
            "location": {
                "id": package.location_id.id,
                "name": package.location_id.display_name,
            },
            "name": package.name,
            "operation_count": 1,
            "packaging": self.data_detail.packaging(package.packaging_id),
            "weight": 20.0,
            "pickings": self.data_detail.pickings(pickings),
            "operations": self.data_detail.operations(lines),
            "storage_type": {
                "id": self.storage_type_pallet.id,
                "name": self.storage_type_pallet.name,
            },
        }
        self.assertDictEqual(data, expected)

    def test_data_picking(self):
        picking = self.picking
        carrier = picking.carrier_id.search([], limit=1)
        picking.write(
            {
                "origin": "created by test",
                "note": "read me",
                "priority": "3",
                "carrier_id": carrier.id,
            }
        )
        picking.write({"min_date": "2020-05-13"})
        data = self.data_detail.picking_detail(picking)
        self.assert_schema(self.schema_detail.picking_detail(), data)
        expected = {
            "id": picking.id,
            "operation_count": 4,
            "name": picking.name,
            "note": "read me",
            "origin": "created by test",
            "weight": 110.0,
            "partner": {"id": self.customer.id, "name": self.customer.name},
            "carrier": {"id": picking.carrier_id.id, "name": picking.carrier_id.name},
            "priority": "Very Urgent",
            "operation_type": {
                "id": picking.picking_type_id.id,
                "name": picking.picking_type_id.name,
            },
            "operations": self.data_detail.operations(picking.pack_operation_ids),
            "picking_type_code": "outgoing",
        }
        self.assertEqual(data.pop("scheduled_date").split(" ")[0], "2020-05-13")
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_package(self):
        pack_operation = self.move_a.linked_move_operation_ids.operation_id
        result_package = self.env["stock.quant.package"].create(
            {"packaging_id": self.packaging.id}
        )
        pack_operation.write({"qty_done": 3.0, "result_package_id": result_package.id})
        data = self.data_detail.operations(pack_operation)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema_detail.operation(), data)
        product = self.product_a.with_context(location=pack_operation.location_id.id)
        expected = {
            "id": pack_operation.id,
            "qty_done": 3.0,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product_detail(product),
            "package_src": {
                "id": pack_operation.package_id.id,
                "name": pack_operation.package_id.name,
                "operation_count": 1,
                "weight": 20.0,
                "storage_type": None,
            },
            "package_dest": {
                "id": result_package.id,
                "name": result_package.name,
                "operation_count": 0,
                "weight": 60.0,
                "storage_type": None,
            },
            "location_src": self._expected_location(pack_operation.location_id),
            "location_dest": self._expected_location(pack_operation.location_dest_id),
            "priority": "1",
            "is_done": True,
            "type": "package",
        }
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_lot(self):
        pack_operation = self.move_b.linked_move_operation_ids.operation_id
        data = self.data_detail.operations(pack_operation)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema_detail.operation(), data)
        product = self.product_b.with_context(location=pack_operation.location_id.id)
        lot_id = pack_operation.pack_lot_ids.lot_id
        expected = {
            "id": pack_operation.id,
            "qty_done": 0.0,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product_detail(product),
            "lot": {"id": lot_id.id, "name": lot_id.name, "ref": None},
            "package_src": None,
            "package_dest": None,
            "location_src": self._expected_location(pack_operation.location_id),
            "location_dest": self._expected_location(pack_operation.location_dest_id),
            "priority": "1",
            "is_done": False,
            "type": "lot",
        }
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_raw(self):
        pack_operation = self.move_d.linked_move_operation_ids.operation_id
        data = self.data_detail.operations(pack_operation)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema_detail.operation(), data)
        product = self.product_d.with_context(location=pack_operation.location_id.id)
        expected = {
            "id": pack_operation.id,
            "qty_done": 0.0,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product_detail(product),
            "package_src": None,
            "package_dest": None,
            "location_src": self._expected_location(pack_operation.location_id),
            "location_dest": self._expected_location(pack_operation.location_dest_id),
            "priority": "1",
            "is_done": False,
            "type": "product",
        }
        self.assertDictEqual(data, expected)

    def test_product(self):
        pack_operation = self.move_b.linked_move_operation_ids.operation_id
        product = pack_operation.product_id.with_context(
            location=pack_operation.location_id.id
        )
        Partner = self.env["res.partner"].sudo()
        manuf = Partner.create({"name": "Manuf 1"})
        product.sudo().write(
            {
                "image_small": fake_colored_image(size=(128, 128)),
                "manufacturer": manuf.id,
            }
        )
        vendor_a = Partner.create({"name": "Supplier A"})
        vendor_b = Partner.create({"name": "Supplier B"})
        SupplierInfo = (
            self.env["product.supplierinfo"]
            .sudo()
            .with_context(disable_check_dates=True)
        )  # avoid side effect with pricelist_discount
        SupplierInfo.create(
            {
                "name": vendor_a.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_code": "SUPP1",
            }
        )
        SupplierInfo.create(
            {
                "name": vendor_b.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_code": "SUPP2",
            }
        )
        data = self.data_detail.product_detail(product)
        self.assert_schema(self.schema_detail.product_detail(), data)
        expected = self._expected_product_detail(product, full=True)
        self.assertDictEqual(data, expected)

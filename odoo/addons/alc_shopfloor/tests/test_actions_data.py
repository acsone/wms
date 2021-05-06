# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .test_actions_data_base import ActionsDataCaseBase


class ActionsDataCase(ActionsDataCaseBase):
    def test_data_packaging(self):
        data = self.data.packaging(self.packaging)
        self.assert_schema(self.schema.packaging(), data)
        self.assertDictEqual(data, self._expected_packaging(self.packaging))

    def test_data_delivery_packaging(self):
        data = self.data.delivery_packaging(self.delivery_packaging)
        self.assert_schema(self.schema.delivery_packaging(), data)
        self.assertDictEqual(
            data, self._expected_delivery_packaging(self.delivery_packaging)
        )

    def test_data_location(self):
        location = self.stock_location
        data = self.data.location(location)
        self.assert_schema(self.schema.location(), data)
        expected = {
            "id": location.id,
            "name": location.name,
            "barcode": location.barcode,
        }
        self.assertDictEqual(data, expected)

    def test_data_location_no_barcode(self):
        location = self.stock_location
        location.sudo().barcode = None
        data = self.data.location(location)
        self.assert_schema(self.schema.location(), data)
        expected = {
            "id": location.id,
            "name": location.name,
            "barcode": location.name,
        }
        self.assertDictEqual(data, expected)

    def test_data_lot(self):
        lot = self.env["stock.production.lot"].create(
            {"product_id": self.product_b.id, "ref": "#FOO"}
        )
        data = self.data.lot(lot)
        self.assert_schema(self.schema.lot(), data)
        expected = {"id": lot.id, "name": lot.name, "ref": "#FOO"}
        self.assertDictEqual(data, expected)

    def test_data_package(self):
        package = self.move_a.linked_move_operation_ids.operation_id.package_id
        package.packaging_id = self.packaging.id
        package.package_storage_type_id = self.storage_type_pallet
        data = self.data.package(package, picking=self.picking, with_packaging=True)
        self.assert_schema(self.schema.package(with_packaging=True), data)
        expected = {
            "id": package.id,
            "name": package.name,
            "packaging": self._expected_packaging(package.packaging_id),
            "storage_type": self._expected_storage_type(
                package.package_storage_type_id
            ),
            "weight": 20.0,
            "operation_count": 1,
        }
        self.assertDictEqual(data, expected)

    def test_data_operation_package(self):
        operation = self.picking.pack_operation_pack_ids[0]
        data = self.data.operations(operation)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema.operation(), data)
        expected = {
            "id": operation.id,
            "is_done": False,
            "package_src": self._expected_package(
                operation.package_id, operation_count=1
            ),
            "location_dest": self._expected_location(operation.location_dest_id),
            "location_src": self._expected_location(operation.picking_id.location_id),
            "product": self._expected_product(operation.package_id.single_product_id),
            "quantity": 1.0,
            "qty_done": 0.0,
            "package_dest": None,
            "priority": "1",
            "type": "package",
        }
        self.assertDictEqual(data, expected)

    def test_data_picking(self):
        carrier = self.picking.carrier_id.search([], limit=1)
        self.picking.write(
            {"origin": "created by test", "note": "read me", "carrier_id": carrier.id}
        )
        data = self.data.picking(self.picking)
        self.assert_schema(self.schema.picking(), data)
        expected = {
            "id": self.picking.id,
            "operation_count": 4,
            "name": self.picking.name,
            "note": "read me",
            "origin": "created by test",
            "weight": 110.0,
            "partner": {"id": self.customer.id, "name": self.customer.name},
            "carrier": {"id": carrier.id, "name": carrier.name},
        }
        self.assertEqual(data.pop("scheduled_date").split(" ")[0], "2020-08-03")
        self.assertDictEqual(data, expected)

    def test_data_product(self):
        (
            self.env["product.packaging"]
            .sudo()
            .create(
                {
                    "name": "Box 2",
                    "product_tmpl_id": self.product_a.product_tmpl_id.id,
                    "barcode": "ProductABox2",
                }
            )
        )
        self.product_a.packaging_ids.write({"qty": 0})
        data = self.data.product(self.product_a)
        self.assert_schema(self.schema.product(), data)
        # No packaging expected as all qties are zero
        expected = self._expected_product(self.product_a)
        self.assertDictEqual(data, expected)
        # packaging w/ no zero qty are included
        self.product_a.packaging_ids[0].write({"qty": 100})
        self.product_a.packaging_ids[1].write({"qty": 20})
        data = self.data.product(self.product_a)
        expected = self._expected_product(self.product_a)
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_package(self):
        pack_operation = self.move_a.linked_move_operation_ids.operation_id
        result_package = self.env["stock.quant.package"].create(
            {"packaging_id": self.packaging.id}
        )
        pack_operation.write({"qty_done": 3.0, "result_package_id": result_package.id})
        data = self.data.operations(pack_operation)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema.operation(), data)
        expected = {
            "id": pack_operation.id,
            "qty_done": 3.0,
            "is_done": True,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product(self.product_a),
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
            "type": "package",
        }
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_lot(self):
        pack_operation = self.move_b.linked_move_operation_ids.operation_id
        data = self.data.operations(pack_operation)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema.operation(), data)
        lot_id = pack_operation.pack_lot_ids.lot_id
        expected = {
            "id": pack_operation.id,
            "qty_done": 0.0,
            "is_done": False,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product(self.product_b),
            "lot": {"id": lot_id.id, "name": lot_id.name, "ref": None},
            "package_src": None,
            "package_dest": None,
            "location_src": self._expected_location(pack_operation.location_id),
            "location_dest": self._expected_location(pack_operation.location_dest_id),
            "priority": "1",
            "type": "lot",
        }
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_raw(self):
        pack_operation = self.move_d.linked_move_operation_ids.operation_id
        datas = self.data.operations(pack_operation)
        self.assertEqual(1, len(datas))
        data = datas[0]
        self.assert_schema(self.schema.operation(), data)
        expected = {
            "id": pack_operation.id,
            "qty_done": 0.0,
            "is_done": False,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product(self.product_d),
            "location_src": self._expected_location(pack_operation.location_id),
            "location_dest": self._expected_location(pack_operation.location_dest_id),
            "package_src": None,
            "package_dest": None,
            "priority": "1",
            "type": "product",
        }
        self.assertDictEqual(data, expected)

    def test_data_pack_operation_with_picking(self):
        pack_operation = self.move_d.linked_move_operation_ids.operation_id
        data = self.data.operations(pack_operation, with_picking=True)
        self.assertEqual(1, len(data))
        data = data[0]
        self.assert_schema(self.schema.operation(with_picking=True), data)
        expected = {
            "id": pack_operation.id,
            "qty_done": 0.0,
            "quantity": pack_operation.product_qty,
            "product": self._expected_product(self.product_d),
            "package_src": None,
            "package_dest": None,
            "location_src": self._expected_location(pack_operation.location_id),
            "location_dest": self._expected_location(pack_operation.location_dest_id),
            "picking": self.data.picking(pack_operation.picking_id),
            "priority": "1",
            "is_done": False,
            "type": "product",
        }
        self.assertDictEqual(data, expected)

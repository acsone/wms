# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestGetLocationReserve(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestGetLocationReserve, cls).setUpClass()

        cls.StockLocation = cls.env["stock.location"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.vlb_location = cls.stock_location.location_id

        cls.reserve_medoc_root = cls.StockLocation.create(
            {
                "name": "Reserve Medoc Root",
                "location_id": cls.vlb_location.id,
                "usage": "internal",
                "act_as_view": True,
                "kind": "reserve",
            }
        )
        cls.reserve_medoc_root._parent_store_compute()

        # Create the reserve RM99 (GD80X1)
        cls.reserve_medoc = cls.StockLocation.create(
            {
                "name": "RM99",
                "kind": "reserve",
                "usage": "internal",
                "location_id": cls.reserve_medoc_root.id,
            }
        )
        cls.reserve_medoc._parent_store_compute()

        # Create the reserve RM99 (GD80X1)
        cls.sub_reserve_medoc = cls.StockLocation.create(
            {
                "name": "RM100",
                "kind": "reserve",
                "usage": "internal",
                "location_id": cls.reserve_medoc.id,
            }
        )
        cls.sub_reserve_medoc._parent_store_compute()

        cls.location_medoc_root = cls.StockLocation.create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
                "reserve_location_id": cls.reserve_medoc_root.id,
            }
        )

        cls.zone_gustave = cls.StockLocation.create(
            {"name": "G", "location_id": cls.location_medoc_root.id}
        )

        cls.location_medoc = cls.StockLocation.create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.location_medoc_root.id,
            }
        )

        cls.zone_2 = cls.StockLocation.create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )

        cls.sub_location_medoc = cls.StockLocation.create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.location_medoc.id,
            }
        )

        cls.zone_3 = cls.StockLocation.create(
            {"name": "G", "location_id": cls.sub_location_medoc.id}
        )

        cls.rangement_medoc_root = cls.StockLocation.create(
            {"name": "GD80B1", "kind": "bin", "location_id": cls.zone_gustave.id}
        )
        cls.rangement_medoc_root._parent_store_compute()

        cls.rangement_medoc = cls.StockLocation.create(
            {"name": "GD80B1", "kind": "bin", "location_id": cls.zone_2.id}
        )
        cls.rangement_medoc._parent_store_compute()

        cls.sub_rangement_medoc = cls.StockLocation.create(
            {"name": "GD80B1", "kind": "bin", "location_id": cls.zone_3.id}
        )
        cls.sub_rangement_medoc._parent_store_compute()

        cls.rangement_medoc_2 = cls.StockLocation.create(
            {
                "name": "GD80B1",
                "kind": "bin",
                "location_id": cls.zone_gustave.id,
                "reserve_location_id": cls.reserve_medoc.id,
            }
        )
        cls.rangement_medoc_2._parent_store_compute()

    def test_00(self):
        """
        Data:
        The reserve is on the location where to put the medicines.
        Test case:
        We retrieve the reserve location associated to the stock location
        Expected: reserve_id is the reserve on the stock location
        """

        reserve = self.rangement_medoc_2.get_location_reserve()
        self.assertEqual(reserve.id, self.reserve_medoc.id)

    def test_01(self):
        """
        Data:
        The reserve is on the first parent of the location where to put the medicines.
        Test case:
        We retrieve the reserve location associated to the stock location
        Expected: reserve_id is the reserve on the parent_location (reserve_medoc_root)
        """

        reserve = self.rangement_medoc_root.get_location_reserve()
        self.assertEqual(reserve.id, self.reserve_medoc_root.id)

    def test_02(self):
        """
        Data:
        The reserve is on the grand parent of the location where to put the medicines.
        Test case:
        We retrieve the reserve location associated to the stock location
        Expected: reserve_id is the reserve on the grand parent_location (reserve_medoc_root)
        """

        reserve = self.rangement_medoc.get_location_reserve()
        self.assertEqual(reserve.id, self.reserve_medoc_root.id)

    def test_03(self):
        """
        Data:
        The reserve is on the grand grand parent of the location where to put the medicines.
        Test case:
        We retrieve the reserve location associated to the stock location
        Expected: reserve_id is the reserve on the grand grand parent_location (reserve_medoc_root)
        """

        reserve = self.sub_rangement_medoc.get_location_reserve()
        self.assertEqual(reserve.id, self.reserve_medoc_root.id)

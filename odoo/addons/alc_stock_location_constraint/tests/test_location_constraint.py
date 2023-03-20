# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockLocationConstraint(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_obj = cls.env["stock.location"]
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test A",
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "corridor": "A",
                "rack": "R",
                "level": "1",
                "posx": 1,
                "posy": 1,
                "posz": 1,
            }
        )

    def test_location_char_unique(self):
        # Activate the constraint
        # Try to add a duplicate and check constraint raises
        # Try to add a different location and check no constraint raises
        self.env["res.config.settings"].create(
            {
                "alc_stock_location_constraint": True,
            }
        ).execute()
        message = "The following locations have the same characteristics than this one (Test B): Test A"
        with self.assertRaises(ValidationError, msg=message):
            self.location_obj.create(
                {
                    "name": "Test A",
                    "location_id": self.env.ref("stock.stock_location_stock").id,
                    "corridor": "A",
                    "rack": "R",
                    "level": "1",
                    "posx": 1,
                    "posy": 1,
                    "posz": 1,
                }
            )

        self.location_obj.create(
            {
                "name": "Test B",
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "corridor": "A",
                "rack": "R",
                "level": "1",
                "posx": 1,
                "posy": 1,
                "posz": 2,
            }
        )

    def test_location_char_no_unique(self):
        # Check the deactivation of the constraint check
        self.location_obj.create(
            {
                "name": "Test A",
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "corridor": "A",
                "rack": "R",
                "level": "1",
                "posx": 1,
                "posy": 1,
                "posz": 1,
            }
        )

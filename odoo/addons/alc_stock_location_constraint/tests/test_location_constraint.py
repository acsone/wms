# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from psycopg2.errors import UniqueViolation

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestStockLocationConstraint(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_obj = cls.env["stock.location"]
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.stock.write({"is_zone": True})
        cls.stock.flush_recordset()
        # Create a view that is a child of Stock that should be an area
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Area",
                "location_id": cls.stock.id,
                "usage": "view",
            }
        )
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test A",
                "location_id": cls.location.id,
                "corridor": "A",
                "rack": "R",
                "level": "1",
                "posx": 1,
                "posy": 1,
                "posz": 1,
            }
        )

    @mute_logger("odoo.sql_db")
    def test_location_char_unique(self):
        # Activate the constraint
        # Try to add a duplicate and check constraint raises
        # Try to add a different location and check no constraint raises
        self.env["res.config.settings"].create(
            {
                "alc_stock_location_constraint": True,
            }
        ).execute()
        with (
            self.assertRaisesRegex(
                UniqueViolation, "Duplicate entry for location coordinates"
            ),
            self.env.cr.savepoint(),
        ):
            self.location_obj.create(
                {
                    "name": "Test A",
                    "location_id": self.location.id,
                    "corridor": "A",
                    "rack": "R",
                    "level": "1",
                    "posx": 1,
                    "posy": 1,
                    "posz": 1,
                }
            )

    @mute_logger("odoo.sql_db")
    def test_location_char_not_unique(self):
        # Activate the constraint
        # Try to add a duplicate and check constraint raises
        # Try to add a different location and check no constraint raises
        self.env["res.config.settings"].create(
            {
                "alc_stock_location_constraint": True,
            }
        ).execute()

        self.location_obj.create(
            {
                "name": "Test B",
                "location_id": self.location.id,
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
                "location_id": self.location.id,
                "corridor": "A",
                "rack": "R",
                "level": "1",
                "posx": 1,
                "posy": 1,
                "posz": 1,
            }
        )
